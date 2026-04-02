"""
Unit tests for Task State Management module.

Tests cover all state transitions, error handling, and file persistence.
"""

import pytest
from pathlib import Path
from datetime import datetime

from lingmaflow.core.task_state import (
    TaskStatus,
    TaskState,
    TaskStateManager,
    InvalidStateError,
    MalformedStateFileError,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def tmp_state_file(tmp_path):
    """Create a temporary directory for test state files."""
    return tmp_path / "TASK_STATE.md"


@pytest.fixture
def manager(tmp_state_file):
    """Create a TaskStateManager with a temporary file."""
    return TaskStateManager(tmp_state_file)


@pytest.fixture
def valid_state_file(tmp_state_file):
    """Create a valid TASK_STATE.md file."""
    content = """當前步驟：STEP-01
狀態：in_progress
上一步結果：Completed setup
下一步動作：Write tests
未解決問題：
- Database connection timeout
- API rate limiting
最後更新：2024-01-01T12:00:00.000000"""
    tmp_state_file.write_text(content, encoding='utf-8')
    return tmp_state_file


# ============================================================================
# Test TaskStatus Enum
# ============================================================================

class TestTaskStatusEnum:
    """Test TaskStatus enumeration values."""
    
    def test_status_values(self):
        """Test that status enum has correct values."""
        assert TaskStatus.NOT_STARTED.value == "not_started"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.BLOCKED.value == "blocked"
        assert TaskStatus.DONE.value == "done"


# ============================================================================
# Test TaskState Dataclass
# ============================================================================

class TestTaskStateDataclass:
    """Test TaskState dataclass initialization and defaults."""
    
    def test_default_initialization(self):
        """Test default TaskState creation."""
        state = TaskState()
        assert state.current_step == "STEP-00"
        assert state.status == TaskStatus.NOT_STARTED
        assert state.last_result == ""
        assert state.next_action == ""
        assert state.unresolved == []
        assert state.timestamp != ""
    
    def test_custom_initialization(self):
        """Test TaskState with custom values."""
        state = TaskState(
            current_step="STEP-05",
            status=TaskStatus.IN_PROGRESS,
            last_result="Success",
            next_action="Continue",
            unresolved=["Issue 1", "Issue 2"],
            timestamp="2024-01-01T00:00:00"
        )
        assert state.current_step == "STEP-05"
        assert state.status == TaskStatus.IN_PROGRESS
        assert state.last_result == "Success"
        assert state.next_action == "Continue"
        assert len(state.unresolved) == 2
        assert state.timestamp == "2024-01-01T00:00:00"


# ============================================================================
# Test Load Functionality
# ============================================================================

class TestLoadFunctionality:
    """Test TaskStateManager.load() method."""
    
    def test_load_nonexistent_file(self, manager):
        """Test loading non-existent file returns NOT_STARTED status."""
        state = manager.load()
        assert state.status == TaskStatus.NOT_STARTED
        assert state.current_step == "STEP-00"
    
    def test_load_existing_file(self, manager, valid_state_file):
        """Test loading existing file parses correctly."""
        state = manager.load()
        assert state.status == TaskStatus.IN_PROGRESS
        assert state.current_step == "STEP-01"
        assert state.last_result == "Completed setup"
        assert state.next_action == "Write tests"
        assert len(state.unresolved) == 2
        assert "Database connection timeout" in state.unresolved
    
    def test_load_missing_current_step_raises_error(self, manager, tmp_state_file):
        """Test that missing current_step raises MalformedStateFileError."""
        content = """狀態：in_progress
最後更新：2024-01-01T00:00:00"""
        tmp_state_file.write_text(content, encoding='utf-8')
        
        with pytest.raises(MalformedStateFileError, match="當前步驟"):
            manager.load()
    
    def test_load_missing_status_raises_error(self, manager, tmp_state_file):
        """Test that missing status raises MalformedStateFileError."""
        content = """當前步驟：STEP-01
最後更新：2024-01-01T00:00:00"""
        tmp_state_file.write_text(content, encoding='utf-8')
        
        with pytest.raises(MalformedStateFileError, match="狀態"):
            manager.load()
    
    def test_load_invalid_status_value_raises_error(self, manager, tmp_state_file):
        """Test that invalid status value raises MalformedStateFileError."""
        content = """當前步驟：STEP-01
狀態：RUNNING
最後更新：2024-01-01T00:00:00"""
        tmp_state_file.write_text(content, encoding='utf-8')
        
        with pytest.raises(MalformedStateFileError, match="Invalid status value"):
            manager.load()


# ============================================================================
# Test Save Functionality
# ============================================================================

class TestSaveFunctionality:
    """Test TaskStateManager.save() method."""
    
    def test_save_writes_all_fields(self, manager, tmp_state_file):
        """Test save writes correct format with all fields."""
        state = TaskState(
            current_step="STEP-03",
            status=TaskStatus.IN_PROGRESS,
            last_result="Test passed",
            next_action="Deploy",
            unresolved=["Bug #123"],
            timestamp="2024-01-01T12:00:00"
        )
        manager.save(state)
        
        content = tmp_state_file.read_text(encoding='utf-8')
        assert "當前步驟：STEP-03" in content
        assert "狀態：in_progress" in content
        assert "上一步結果：Test passed" in content
        assert "下一步動作：Deploy" in content
        assert "- Bug #123" in content
        assert "最後更新：" in content
    
    def test_save_timestamp_format(self, manager, tmp_state_file):
        """Test timestamp is in ISO8601 format."""
        state = TaskState()
        manager.save(state)
        
        content = tmp_state_file.read_text(encoding='utf-8')
        # Check that timestamp exists and looks like ISO8601
        assert "最後更新：" in content
        # Verify the timestamp can be parsed
        lines = content.split('\n')
        timestamp_line = [l for l in lines if '最後更新' in l][0]
        timestamp_str = timestamp_line.split('：')[1]
        # Should not raise an exception
        datetime.fromisoformat(timestamp_str)
    
    def test_save_creates_parent_directory(self, manager, tmp_path):
        """Test save creates parent directory if it doesn't exist."""
        nested_path = tmp_path / "subdir" / "TASK_STATE.md"
        manager.path = nested_path
        
        state = TaskState()
        manager.save(state)
        
        assert nested_path.exists()
        assert (tmp_path / "subdir").is_dir()


# ============================================================================
# Test Advance Method
# ============================================================================

class TestAdvanceMethod:
    """Test TaskStateManager.advance() method."""
    
    def test_advance_updates_step_and_status(self, manager, valid_state_file):
        """Test advance updates step, status stays IN_PROGRESS."""
        manager.load()
        new_state = manager.advance("STEP-02", "Setup complete")
        
        assert new_state.current_step == "STEP-02"
        assert new_state.last_result == "Setup complete"
        assert new_state.status == TaskStatus.IN_PROGRESS
    
    def test_advance_from_done_raises_error(self, manager, tmp_state_file):
        """Test advance from DONE raises InvalidStateError."""
        content = """當前步驟：STEP-10
狀態：done
最後更新：2024-01-01T00:00:00"""
        tmp_state_file.write_text(content, encoding='utf-8')
        manager.load()
        
        with pytest.raises(InvalidStateError, match="Cannot advance from DONE"):
            manager.advance("STEP-11", "More work")
    
    def test_advance_without_load_raises_error(self, manager):
        """Test advance without loading state raises error."""
        with pytest.raises(InvalidStateError, match="State not loaded"):
            manager.advance("STEP-01", "Result")


# ============================================================================
# Test Block Method
# ============================================================================

class TestBlockMethod:
    """Test TaskStateManager.block() method."""
    
    def test_block_changes_status_and_adds_unresolved(self, manager, valid_state_file):
        """Test block changes status to BLOCKED, adds to unresolved."""
        manager.load()
        new_state = manager.block("API timeout")
        
        assert new_state.status == TaskStatus.BLOCKED
        assert "API timeout" in new_state.unresolved
    
    def test_block_from_done_raises_error(self, manager, tmp_state_file):
        """Test block from DONE raises InvalidStateError."""
        content = """當前步驟：STEP-10
狀態：done
最後更新：2024-01-01T00:00:00"""
        tmp_state_file.write_text(content, encoding='utf-8')
        manager.load()
        
        with pytest.raises(InvalidStateError, match="Cannot block a DONE task"):
            manager.block("Some issue")
    
    def test_block_from_not_started_raises_error(self, manager, tmp_state_file):
        """Test block from NOT_STARTED raises InvalidStateError."""
        content = """當前步驟：STEP-00
狀態：not_started
最後更新：2024-01-01T00:00:00"""
        tmp_state_file.write_text(content, encoding='utf-8')
        manager.load()
        
        with pytest.raises(InvalidStateError, match="Cannot block a NOT_STARTED task"):
            manager.block("Some issue")


# ============================================================================
# Test Resolve Method
# ============================================================================

class TestResolveMethod:
    """Test TaskStateManager.resolve() method."""
    
    def test_resolve_changes_status_and_removes_unresolved(self, manager, tmp_state_file):
        """Test resolve changes status to IN_PROGRESS, removes from unresolved."""
        content = """當前步驟：STEP-01
狀態：blocked
上一步結果：Blocked
下一步動作：Fix issue
未解決問題：
- API timeout
最後更新：2024-01-01T00:00:00"""
        tmp_state_file.write_text(content, encoding='utf-8')
        manager.load()
        
        new_state = manager.resolve("API timeout")
        
        assert new_state.status == TaskStatus.IN_PROGRESS
        assert "API timeout" not in new_state.unresolved
        assert len(new_state.unresolved) == 0
    
    def test_resolve_non_existent_reason(self, manager, tmp_state_file):
        """Test resolve with non-existent reason handles gracefully."""
        content = """當前步驟：STEP-01
狀態：blocked
未解決問題：
- Issue 1
最後更新：2024-01-01T00:00:00"""
        tmp_state_file.write_text(content, encoding='utf-8')
        manager.load()
        
        # Should not raise an error, just transition to IN_PROGRESS
        new_state = manager.resolve("Non-existent issue")
        
        assert new_state.status == TaskStatus.IN_PROGRESS
        assert len(new_state.unresolved) == 1  # Original issue still there
    
    def test_resolve_from_done_raises_error(self, manager, tmp_state_file):
        """Test resolve from DONE raises InvalidStateError."""
        content = """當前步驟：STEP-10
狀態：done
最後更新：2024-01-01T00:00:00"""
        tmp_state_file.write_text(content, encoding='utf-8')
        manager.load()
        
        with pytest.raises(InvalidStateError, match="Cannot resolve a DONE task"):
            manager.resolve("Some issue")


# ============================================================================
# Test Complete Method
# ============================================================================

class TestCompleteMethod:
    """Test TaskStateManager.complete() method."""
    
    def test_complete_changes_status_to_done(self, manager, tmp_state_file):
        """Test complete changes status to DONE."""
        # Create a state without unresolved issues
        content = """當前步驟：STEP-05
狀態：in_progress
上一步結果：Testing
下一步動作：Deploy
未解決問題：
最後更新：2024-01-01T00:00:00"""
        tmp_state_file.write_text(content, encoding='utf-8')
        manager.load()
        
        new_state = manager.complete()
        
        assert new_state.status == TaskStatus.DONE
    
    def test_complete_from_done_raises_error(self, manager, tmp_state_file):
        """Test complete from DONE raises InvalidStateError."""
        content = """當前步驟：STEP-10
狀態：done
最後更新：2024-01-01T00:00:00"""
        tmp_state_file.write_text(content, encoding='utf-8')
        manager.load()
        
        with pytest.raises(InvalidStateError, match="already complete"):
            manager.complete()
    
    def test_complete_from_not_started_raises_error(self, manager, tmp_state_file):
        """Test complete from NOT_STARTED raises InvalidStateError."""
        content = """當前步驟：STEP-00
狀態：not_started
最後更新：2024-01-01T00:00:00"""
        tmp_state_file.write_text(content, encoding='utf-8')
        manager.load()
        
        with pytest.raises(InvalidStateError, match="Cannot complete a NOT_STARTED task"):
            manager.complete()
    
    def test_complete_from_blocked_raises_error(self, manager, tmp_state_file):
        """Test complete from BLOCKED raises InvalidStateError."""
        content = """當前步驟：STEP-01
狀態：blocked
未解決問題：
- Critical bug
最後更新：2024-01-01T00:00:00"""
        tmp_state_file.write_text(content, encoding='utf-8')
        manager.load()
        
        with pytest.raises(InvalidStateError, match="Cannot complete a BLOCKED task"):
            manager.complete()


# ============================================================================
# Test Helper Methods
# ============================================================================

class TestHelperMethods:
    """Test is_blocked() and is_done() helper methods."""
    
    def test_is_blocked_when_blocked(self, manager, tmp_state_file):
        """Test is_blocked returns True when status is BLOCKED."""
        content = """當前步驟：STEP-01
狀態：blocked
最後更新：2024-01-01T00:00:00"""
        tmp_state_file.write_text(content, encoding='utf-8')
        manager.load()
        
        assert manager.is_blocked() is True
    
    def test_is_blocked_when_not_blocked(self, manager, valid_state_file):
        """Test is_blocked returns False when status is not BLOCKED."""
        manager.load()
        
        assert manager.is_blocked() is False
    
    def test_is_done_when_done(self, manager, tmp_state_file):
        """Test is_done returns True when status is DONE."""
        content = """當前步驟：STEP-10
狀態：done
最後更新：2024-01-01T00:00:00"""
        tmp_state_file.write_text(content, encoding='utf-8')
        manager.load()
        
        assert manager.is_done() is True
    
    def test_is_done_when_not_done(self, manager, valid_state_file):
        """Test is_done returns False when status is not DONE."""
        manager.load()
        
        assert manager.is_done() is False
    
    def test_helper_methods_without_load(self, manager):
        """Test helper methods return False when state not loaded."""
        assert manager.is_blocked() is False
        assert manager.is_done() is False


# ============================================================================
# Test Multiple Blocks
# ============================================================================

class TestMultipleBlocks:
    """Test multiple blocking issues management."""
    
    def test_multiple_blocks_add_multiple_issues(self, manager, tmp_state_file):
        """Test multiple blocks add multiple unresolved issues."""
        # Start with a clean state (no pre-existing unresolved issues)
        manager.load()
        manager.advance("STEP-01", "Started")
        
        manager.block("Issue 1")
        manager.block("Issue 2")
        manager.block("Issue 3")
        
        assert manager.state.status == TaskStatus.BLOCKED
        assert len(manager.state.unresolved) == 3
        assert "Issue 1" in manager.state.unresolved
        assert "Issue 2" in manager.state.unresolved
        assert "Issue 3" in manager.state.unresolved
    
    def test_resolve_one_issue_keeps_others(self, manager, tmp_state_file):
        """Test resolving one issue keeps others."""
        content = """當前步驟：STEP-01
狀態：blocked
未解決問題：
- Issue 1
- Issue 2
- Issue 3
最後更新：2024-01-01T00:00:00"""
        tmp_state_file.write_text(content, encoding='utf-8')
        manager.load()
        
        manager.resolve("Issue 2")
        
        assert manager.state.status == TaskStatus.IN_PROGRESS
        assert len(manager.state.unresolved) == 2
        assert "Issue 1" in manager.state.unresolved
        assert "Issue 2" not in manager.state.unresolved
        assert "Issue 3" in manager.state.unresolved


# ============================================================================
# Test State Transition Scenarios
# ============================================================================

class TestStateTransitionScenarios:
    """Test complete state transition workflows."""
    
    def test_full_workflow(self, manager, tmp_state_file):
        """Test complete workflow from start to finish."""
        # Start task
        state = manager.load()
        assert state.status == TaskStatus.NOT_STARTED
        
        # Advance to first step
        manager.advance("STEP-01", "Started")
        assert manager.state.status == TaskStatus.IN_PROGRESS
        
        # Encounter issue
        manager.block("Bug found")
        assert manager.is_blocked()
        assert len(manager.state.unresolved) == 1
        
        # Resolve issue
        manager.resolve("Bug found")
        assert manager.state.status == TaskStatus.IN_PROGRESS
        assert not manager.is_blocked()
        
        # Complete task
        manager.complete()
        assert manager.is_done()
        assert manager.state.status == TaskStatus.DONE
    
    def test_block_advance_block_resolve_complete(self, manager):
        """Test complex workflow with multiple blocks and resolves."""
        manager.load()
        manager.advance("STEP-01", "Step 1 done")
        
        # First block
        manager.block("Issue A")
        assert len(manager.state.unresolved) == 1
        
        # Resolve and continue
        manager.resolve("Issue A")
        manager.advance("STEP-02", "Step 2 done")
        
        # Second block with multiple issues
        manager.block("Issue B")
        manager.block("Issue C")
        assert len(manager.state.unresolved) == 2
        
        # Resolve one
        manager.resolve("Issue B")
        assert len(manager.state.unresolved) == 1
        
        # Can't complete while blocked
        with pytest.raises(InvalidStateError):
            manager.complete()
        
        # Resolve remaining
        manager.resolve("Issue C")
        
        # Now can complete
        manager.complete()
        assert manager.is_done()


# ============================================================================
# Tests for Done Conditions Extension (Phase 4)
# ============================================================================

class TestGetConditions:
    """Test get_conditions() method."""
    
    def test_get_conditions_parsing(self, tmp_path):
        """Test parsing Done Conditions block."""
        task_state_file = tmp_path / "TASK_STATE.md"
        content = """當前步驟：STEP-01
狀態：in_progress
上一步結果：Testing
下一步動作：Add tests
未解決問題：
最後更新：2024-01-01T12:00:00

## Done Conditions
- [ ] file:lingmaflow/core/task_state.py
- [ ] pytest:tests/test_task_state.py
- [x] func:lingmaflow.core.TaskStateManager
"""
        task_state_file.write_text(content, encoding='utf-8')
        
        manager = TaskStateManager(task_state_file)
        manager.load()
        conditions = manager.get_conditions()
        
        assert len(conditions) == 3
        assert "file:lingmaflow/core/task_state.py" in conditions
        assert "pytest:tests/test_task_state.py" in conditions
        assert "func:lingmaflow.core.TaskStateManager" in conditions
    
    def test_get_conditions_no_block(self, valid_state_file):
        """Test when no Done Conditions block exists."""
        manager = TaskStateManager(valid_state_file)
        manager.load()
        conditions = manager.get_conditions()
        
        assert conditions == []
    
    def test_get_conditions_empty_block(self, tmp_path):
        """Test with empty Done Conditions block."""
        task_state_file = tmp_path / "TASK_STATE.md"
        content = """當前步驟：STEP-01
狀態：in_progress
上一步結果：Testing
下一步動作：Add tests
未解決問題：
最後更新：2024-01-01T12:00:00

## Done Conditions
"""
        task_state_file.write_text(content, encoding='utf-8')
        
        manager = TaskStateManager(task_state_file)
        manager.load()
        conditions = manager.get_conditions()
        
        assert conditions == []
    
    def test_get_conditions_without_load_raises_error(self, tmp_state_file):
        """Test that calling without load raises error."""
        manager = TaskStateManager(tmp_state_file)
        
        with pytest.raises(InvalidStateError):
            manager.get_conditions()


class TestMarkConditionDone:
    """Test mark_condition_done() method."""
    
    def test_mark_condition_done_successful_update(self, tmp_path):
        """Test successfully marking a condition as done."""
        task_state_file = tmp_path / "TASK_STATE.md"
        content = """當前步驟：STEP-01
狀態：in_progress
上一步結果：Testing
下一步動作：Add tests
未解決問題：
最後更新：2024-01-01T12:00:00

## Done Conditions
- [ ] file:lingmaflow/core/task_state.py
- [ ] pytest:tests/test_task_state.py
"""
        task_state_file.write_text(content, encoding='utf-8')
        
        manager = TaskStateManager(task_state_file)
        manager.load()
        manager.mark_condition_done("file:lingmaflow/core/task_state.py")
        
        # Read file and verify
        updated_content = task_state_file.read_text(encoding='utf-8')
        assert "- [x] file:lingmaflow/core/task_state.py" in updated_content
        assert "- [ ] pytest:tests/test_task_state.py" in updated_content
    
    def test_mark_condition_done_invalid_condition(self, tmp_path):
        """Test marking non-existent condition."""
        task_state_file = tmp_path / "TASK_STATE.md"
        content = """當前步驟：STEP-01
狀態：in_progress
上一步結果：Testing
下一步動作：Add tests
未解決問題：
最後更新：2024-01-01T12:00:00

## Done Conditions
- [ ] file:lingmaflow/core/task_state.py
"""
        task_state_file.write_text(content, encoding='utf-8')
        
        manager = TaskStateManager(task_state_file)
        manager.load()
        
        with pytest.raises(ValueError, match="Condition not found"):
            manager.mark_condition_done("nonexistent:condition")
    
    def test_mark_condition_done_without_load_raises_error(self, tmp_state_file):
        """Test that calling without load raises error."""
        manager = TaskStateManager(tmp_state_file)
        
        with pytest.raises(InvalidStateError):
            manager.mark_condition_done("file:test.py")


class TestAllConditionsDone:
    """Test all_conditions_done() method."""
    
    def test_all_conditions_done_all_checked(self, tmp_path):
        """Test when all conditions are checked."""
        task_state_file = tmp_path / "TASK_STATE.md"
        content = """當前步驟：STEP-01
狀態：in_progress
上一步結果：Testing
下一步動作：Add tests
未解決問題：
最後更新：2024-01-01T12:00:00

## Done Conditions
- [x] file:lingmaflow/core/task_state.py
- [x] pytest:tests/test_task_state.py
"""
        task_state_file.write_text(content, encoding='utf-8')
        
        manager = TaskStateManager(task_state_file)
        manager.load()
        result = manager.all_conditions_done()
        
        assert result is True
    
    def test_all_conditions_done_partially_checked(self, tmp_path):
        """Test when some conditions are unchecked."""
        task_state_file = tmp_path / "TASK_STATE.md"
        content = """當前步驟：STEP-01
狀態：in_progress
上一步結果：Testing
下一步動作：Add tests
未解決問題：
最後更新：2024-01-01T12:00:00

## Done Conditions
- [x] file:lingmaflow/core/task_state.py
- [ ] pytest:tests/test_task_state.py
"""
        task_state_file.write_text(content, encoding='utf-8')
        
        manager = TaskStateManager(task_state_file)
        manager.load()
        result = manager.all_conditions_done()
        
        assert result is False
    
    def test_all_conditions_done_empty_block(self, tmp_path):
        """Test with empty Done Conditions block (vacuous truth)."""
        task_state_file = tmp_path / "TASK_STATE.md"
        content = """當前步驟：STEP-01
狀態：in_progress
上一步結果：Testing
下一步動作：Add tests
未解決問題：
最後更新：2024-01-01T12:00:00

## Done Conditions
"""
        task_state_file.write_text(content, encoding='utf-8')
        
        manager = TaskStateManager(task_state_file)
        manager.load()
        result = manager.all_conditions_done()
        
        assert result is True
    
    def test_all_conditions_done_no_block(self, valid_state_file):
        """Test when no Done Conditions block exists."""
        manager = TaskStateManager(valid_state_file)
        manager.load()
        result = manager.all_conditions_done()
        
        assert result is True  # No conditions = vacuously true
