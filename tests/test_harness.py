"""Tests for Harness Manager."""

import json
import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from lingmaflow.core.harness import HarnessManager, ResumePoint


@pytest.fixture
def temp_change_dir():
    """Create a temporary change directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def harness_manager(temp_change_dir):
    """Create a HarnessManager instance with temporary directory."""
    return HarnessManager(temp_change_dir)


class TestResumePoint:
    """Tests for ResumePoint dataclass."""
    
    def test_resume_point_creation(self):
        """Test creating a ResumePoint instance."""
        rp = ResumePoint(
            change_name="test-change",
            next_task_id="3.3",
            last_completed_id="3.2",
            context="task 3.3 started but not finished",
            failed_attempts=["httpx retry failed"]
        )
        
        assert rp.change_name == "test-change"
        assert rp.next_task_id == "3.3"
        assert rp.last_completed_id == "3.2"
        assert rp.context == "task 3.3 started but not finished"
        assert rp.failed_attempts == ["httpx retry failed"]


class TestHarnessManagerInit:
    """Tests for HarnessManager initialization."""
    
    def test_init_sets_correct_paths(self, harness_manager, temp_change_dir):
        """Test that __init__ sets correct file paths."""
        assert harness_manager.change_dir == temp_change_dir
        assert harness_manager.tasks_json_path == temp_change_dir / 'tasks.json'
        assert harness_manager.progress_md_path == temp_change_dir / 'PROGRESS.md'
        assert harness_manager.tasks_md_path == temp_change_dir / 'tasks.md'


class TestParseTasksMd:
    """Tests for parse_tasks_md method."""
    
    def test_parse_completed_task(self, harness_manager, temp_change_dir):
        """Test parsing completed task from tasks.md."""
        tasks_md = temp_change_dir / 'tasks.md'
        tasks_md.write_text("- [x] 1.1 Setup project structure\n")
        
        tasks = harness_manager.parse_tasks_md()
        
        assert len(tasks) == 1
        assert tasks[0]['id'] == '1.1'
        assert tasks[0]['description'] == 'Setup project structure'
        assert tasks[0]['done'] is True
    
    def test_parse_pending_task(self, harness_manager, temp_change_dir):
        """Test parsing pending task from tasks.md."""
        tasks_md = temp_change_dir / 'tasks.md'
        tasks_md.write_text("- [ ] 1.2 Define TaskStatus enum\n")
        
        tasks = harness_manager.parse_tasks_md()
        
        assert len(tasks) == 1
        assert tasks[0]['id'] == '1.2'
        assert tasks[0]['description'] == 'Define TaskStatus enum'
        assert tasks[0]['done'] is False
    
    def test_parse_mixed_tasks(self, harness_manager, temp_change_dir):
        """Test parsing mixed completed and pending tasks."""
        tasks_md = temp_change_dir / 'tasks.md'
        tasks_md.write_text(
            "- [x] 1.1 Setup project structure\n"
            "- [ ] 1.2 Define TaskStatus enum\n"
            "- [x] 2.1 Implement core logic\n"
        )
        
        tasks = harness_manager.parse_tasks_md()
        
        assert len(tasks) == 3
        assert tasks[0]['done'] is True
        assert tasks[1]['done'] is False
        assert tasks[2]['done'] is True
    
    def test_parse_nonexistent_file(self, harness_manager):
        """Test parsing when tasks.md doesn't exist."""
        tasks = harness_manager.parse_tasks_md()
        assert tasks == []


class TestInitChange:
    """Tests for init_change method."""
    
    def test_init_creates_tasks_json(self, harness_manager, temp_change_dir):
        """Test that init_change creates tasks.json."""
        tasks = [
            {'id': '1.1', 'description': 'Task 1', 'done': False}
        ]
        
        harness_manager.init_change('test-change', tasks)
        
        assert (temp_change_dir / 'tasks.json').exists()
    
    def test_init_creates_progress_md(self, harness_manager, temp_change_dir):
        """Test that init_change creates PROGRESS.md."""
        tasks = []
        
        harness_manager.init_change('test-change', tasks)
        
        assert (temp_change_dir / 'PROGRESS.md').exists()
    
    def test_init_converts_tasks_md(self, harness_manager, temp_change_dir):
        """Test that init_change converts tasks.md if provided."""
        tasks_md = temp_change_dir / 'tasks.md'
        tasks_md.write_text(
            "- [x] 1.1 Completed task\n"
            "- [ ] 2.1 Pending task\n"
        )
        
        harness_manager.init_change('test-change')
        
        # Check tasks.json was created with correct content
        tasks_json = temp_change_dir / 'tasks.json'
        with open(tasks_json, 'r') as f:
            tasks = json.load(f)
        
        assert len(tasks) == 2
        assert tasks[0]['id'] == '1.1'
        assert tasks[0]['done'] is True
        assert tasks[1]['id'] == '2.1'
        assert tasks[1]['done'] is False
        
        # Check backup was created
        assert (temp_change_dir / 'tasks.md.bak').exists()


class TestCompleteTask:
    """Tests for complete_task method."""
    
    def test_complete_updates_done_flag(self, harness_manager, temp_change_dir):
        """Test that complete_task updates done flag."""
        tasks = [
            {'id': '1.1', 'description': 'Task 1', 'done': False, 'started_at': None, 'completed_at': None, 'notes': ''}
        ]
        
        # Initialize first
        harness_manager.init_change('test-change', tasks)
        
        # Complete the task
        harness_manager.complete_task('1.1', 'Test notes')
        
        # Verify
        with open(temp_change_dir / 'tasks.json', 'r') as f:
            updated_tasks = json.load(f)
        
        assert updated_tasks[0]['done'] is True
        assert updated_tasks[0]['notes'] == 'Test notes'
        assert updated_tasks[0]['completed_at'] is not None
    
    def test_complete_raises_on_missing_task(self, harness_manager, temp_change_dir):
        """Test that complete_task raises ValueError for missing task."""
        tasks = []
        harness_manager.init_change('test-change', tasks)
        
        with pytest.raises(ValueError, match="Task 999 not found"):
            harness_manager.complete_task('999')


class TestLogSession:
    """Tests for log_session method."""
    
    def test_log_appends_to_progress_md(self, harness_manager, temp_change_dir):
        """Test that log_session appends session to PROGRESS.md."""
        # Initialize first
        harness_manager.init_change('test-change', [])
        
        # Log a session
        harness_manager.log_session(
            completed=['1.1', '1.2'],
            leftover='Task 2.1 in progress',
            failed_attempts=['Attempt 1 failed'],
            next_step='Continue with 2.1'
        )
        
        # Verify
        content = (temp_change_dir / 'PROGRESS.md').read_text()
        
        assert '## Session' in content
        assert '完成：task 1.1, 1.2' in content
        assert '遺留：Task 2.1 in progress' in content
        assert '失敗記錄：Attempt 1 failed' in content
        assert '下一步：Continue with 2.1' in content


class TestGetResumePoint:
    """Tests for get_resume_point method."""
    
    def test_get_resume_point_finds_next_task(self, harness_manager, temp_change_dir):
        """Test that get_resume_point finds next incomplete task."""
        tasks = [
            {'id': '1.1', 'description': 'Done', 'done': True},
            {'id': '2.1', 'description': 'Next', 'done': False},
        ]
        harness_manager.init_change('test-change', tasks)
        
        rp = harness_manager.get_resume_point()
        
        assert rp.next_task_id == '2.1'
        assert rp.last_completed_id == '1.1'
    
    def test_get_resume_point_reads_context(self, harness_manager, temp_change_dir):
        """Test that get_resume_point reads context from PROGRESS.md."""
        # Initialize and log a session
        harness_manager.init_change('test-change', [])
        harness_manager.log_session(
            completed=['1.1'],
            leftover='Context from last session',
            failed_attempts=[],
            next_step='Next step'
        )
        
        rp = harness_manager.get_resume_point()
        
        assert 'Context from last session' in rp.context

    def test_all_tasks_done_returns_ALL_DONE(self, harness_manager, temp_change_dir):
        """Test that ALL_DONE is returned when all tasks complete."""
        tasks = [
        {'id': '1.1', 'description': 'Done', 'done': True},
        {'id': '1.2', 'description': 'Done', 'done': True},
        ]
        harness_manager.init_change('test-change', tasks)
        rp = harness_manager.get_resume_point()
        assert rp.next_task_id == 'ALL_DONE'

    def test_no_progress_md_returns_empty_context(self, harness_manager, temp_change_dir):
        """Test graceful handling when PROGRESS.md is empty."""
        tasks = [{'id': '1.1', 'description': 'Pending', 'done': False}]
        harness_manager.init_change('test-change', tasks)
        rp = harness_manager.get_resume_point()
        assert rp.context == ''
        assert rp.failed_attempts == []

    def test_no_completed_tasks_last_id_is_none(self, harness_manager, temp_change_dir):
        """Test last_completed_id when no tasks are done yet."""
        tasks = [
        {'id': '1.1', 'description': 'Pending', 'done': False},
        {'id': '1.2', 'description': 'Pending', 'done': False},
        ]
        harness_manager.init_change('test-change', tasks)
        rp = harness_manager.get_resume_point()
        assert rp.next_task_id == '1.1'
        assert rp.last_completed_id == 'none'

    def test_failed_attempts_parsed_correctly(self, harness_manager, temp_change_dir):
        """Test that failed_attempts are correctly parsed from PROGRESS.md."""
        harness_manager.init_change('test-change', [])
        harness_manager.log_session(
        completed=['1.1'],
        leftover='blocked on 2.1',
        failed_attempts=['httpx retry failed', 'tenacity v7 incompatible'],
        next_step='try tenacity v8'
        )
        rp = harness_manager.get_resume_point()
        assert len(rp.failed_attempts) == 2
        assert 'httpx retry failed' in rp.failed_attempts
        assert 'tenacity v7 incompatible' in rp.failed_attempts

    def test_empty_failed_attempts_returns_empty_list(self, harness_manager, temp_change_dir):
        """Test that empty failed_attempts returns empty list, not ['無']."""
        harness_manager.init_change('test-change', [])
        harness_manager.log_session(
        completed=['1.1'],
        leftover='ok',
        failed_attempts=[],
        next_step='continue'
        )
        rp = harness_manager.get_resume_point()
        assert rp.failed_attempts == []

    def test_multiple_sessions_reads_last_only(self, harness_manager, temp_change_dir):
        """Test that only the last session context is returned."""
        harness_manager.init_change('test-change', [])
        harness_manager.log_session(['1.1'], 'old context', [], 'old next')
        harness_manager.log_session(['1.2'], 'new context', [], 'new next')
        rp = harness_manager.get_resume_point()
        assert rp.context == 'new context'
        assert 'old context' not in rp.context

    def test_missing_tasks_json_raises_error(self, harness_manager):
        """Test that FileNotFoundError raised when tasks.json missing."""
        with pytest.raises(FileNotFoundError):
            harness_manager.get_resume_point()

    def test_last_completed_is_previous_task(self, harness_manager, temp_change_dir):
        """Test last_completed_id is the task before next_task, not last done overall."""
        tasks = [
        {'id': '1.1', 'description': 'Done', 'done': True},
        {'id': '1.2', 'description': 'Next', 'done': False},
        {'id': '1.3', 'description': 'Done later', 'done': True},
        ]
        harness_manager.init_change('test-change', tasks)
        rp = harness_manager.get_resume_point()
        assert rp.next_task_id == '1.2'
        assert rp.last_completed_id == '1.1'  # 不是 1.3

class TestGenerateStartupBrief:
    """Tests for generate_startup_brief method."""
    
    def test_brief_contains_required_sections(self, harness_manager, temp_change_dir):
        """Test that generated brief contains all required sections."""
        tasks = [
            {'id': '1.1', 'description': 'Done', 'done': True},
            {'id': '2.1', 'description': 'Next', 'done': False},
        ]
        harness_manager.init_change('test-change', tasks)
        
        brief = harness_manager.generate_startup_brief()
        
        assert 'RESUME BRIEF' in brief
        assert 'Change:' in brief
        assert 'Resume from:' in brief
        assert 'Last completed:' in brief
        assert 'Startup sequence:' in brief


class TestGetStatus:
    """Tests for get_status method."""
    
    def test_status_calculates_percentage(self, harness_manager, temp_change_dir):
        """Test that get_status calculates correct percentage."""
        tasks = [
            {'id': '1.1', 'description': 'Done', 'done': True},
            {'id': '2.1', 'description': 'Pending', 'done': False},
        ]
        harness_manager.init_change('test-change', tasks)
        
        status = harness_manager.get_status()
        
        assert status['total'] == 2
        assert status['done'] == 1
        assert status['percentage'] == 50.0


class TestGenerateStartupBriefWithTaskState:
    """Tests for generate_startup_brief() with TASK_STATE.md integration."""

    def _make_change_dir(self, tmp_path):
        change_dir = tmp_path / "openspec" / "changes" / "test-change"
        change_dir.mkdir(parents=True)
        tasks = [
            {"id": "1.1", "description": "Setup", "done": True,
             "started_at": None, "completed_at": "2026-04-03T10:00:00Z", "notes": ""},
            {"id": "1.2", "description": "Implement", "done": False,
             "started_at": None, "completed_at": None, "notes": ""},
        ]
        import json
        (change_dir / "tasks.json").write_text(json.dumps(tasks), encoding="utf-8")
        (change_dir / "PROGRESS.md").write_text("", encoding="utf-8")
        return change_dir

    def _make_task_state(self, tmp_path, step="PHASE-B", status="in_progress"):
        content = f"""當前步驟：{step}
狀態：{status}
上一步結果：Done
下一步動作：Continue
未解決問題：
最後更新：2026-04-03T10:00:00

## Done Conditions
- [ ] file:dummy.py
"""
        (tmp_path / "TASK_STATE.md").write_text(content, encoding="utf-8")

    def test_brief_includes_phase_when_task_state_exists(self, tmp_path):
        """brief に TASK_STATE.md の Phase が含まれること"""
        change_dir = self._make_change_dir(tmp_path)
        self._make_task_state(tmp_path, step="PHASE-B")

        from lingmaflow.core.harness import HarnessManager
        manager = HarnessManager(change_dir)
        brief = manager.generate_startup_brief(project_path=tmp_path)

        assert "PHASE-B" in brief
        assert "TASK_STATE.md" in brief

    def test_brief_excludes_phase_when_no_project_path(self, tmp_path):
        """project_path なしの場合、Phase 行が含まれないこと（後方互換）"""
        change_dir = self._make_change_dir(tmp_path)
        self._make_task_state(tmp_path, step="PHASE-B")

        from lingmaflow.core.harness import HarnessManager
        manager = HarnessManager(change_dir)
        brief = manager.generate_startup_brief()

        assert "PHASE-B" not in brief

    def test_brief_excludes_phase_when_task_state_missing(self, tmp_path):
        """TASK_STATE.md が存在しない場合、エラーにならず Phase 行が省略されること"""
        change_dir = self._make_change_dir(tmp_path)
        # TASK_STATE.md を作らない

        from lingmaflow.core.harness import HarnessManager
        manager = HarnessManager(change_dir)
        brief = manager.generate_startup_brief(project_path=tmp_path)

        assert "RESUME BRIEF" in brief
        assert "PHASE" not in brief

    def test_brief_still_works_when_task_state_malformed(self, tmp_path):
        """TASK_STATE.md が壊れていても brief 生成が成功すること"""
        change_dir = self._make_change_dir(tmp_path)
        (tmp_path / "TASK_STATE.md").write_text("壊れたコンテンツ", encoding="utf-8")

        from lingmaflow.core.harness import HarnessManager
        manager = HarnessManager(change_dir)
        brief = manager.generate_startup_brief(project_path=tmp_path)

        assert "RESUME BRIEF" in brief

    def test_startup_sequence_includes_task_state(self, tmp_path):
        """Startup sequence の最初のステップが TASK_STATE.md であること"""
        change_dir = self._make_change_dir(tmp_path)

        from lingmaflow.core.harness import HarnessManager
        manager = HarnessManager(change_dir)
        brief = manager.generate_startup_brief(project_path=tmp_path)

        lines = brief.splitlines()
        startup_start = next(i for i, l in enumerate(lines) if "Startup sequence" in l)
        first_step = lines[startup_start + 1]
        assert "TASK_STATE.md" in first_step
