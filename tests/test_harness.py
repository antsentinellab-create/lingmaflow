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
