"""
Unit tests for LingmaFlow CLI tool.

Tests cover all CLI commands including task management, skill queries,
agents generation, and project initialization.
"""

import pytest
from pathlib import Path
from click.testing import CliRunner

from lingmaflow.cli.lingmaflow import cli
from lingmaflow.core.task_state import TaskStateManager, TaskStatus


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def runner():
    """Create a Click CliRunner for testing."""
    return CliRunner()


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary directory for test projects."""
    return tmp_path


@pytest.fixture
def initialized_project(tmp_project):
    """Create an initialized LingmaFlow project with TASK_STATE.md."""
    task_state_content = """# TASK_STATE

當前步驟：STEP-02
狀態：in_progress
上一步結果：Implementation complete
下一步動作：Write tests
未解決問題：
最後更新：2024-01-01T00:00:00"""
    
    task_state_file = tmp_project / "TASK_STATE.md"
    task_state_file.write_text(task_state_content, encoding='utf-8')
    
    # Create skills directory
    skills_dir = tmp_project / "skills"
    skills_dir.mkdir()
    
    return tmp_project


@pytest.fixture
def project_with_skills(tmp_project):
    """Create a project with sample skills."""
    import yaml
    
    # Create skills directory
    skills_dir = tmp_project / "skills"
    skills_dir.mkdir()
    
    # Create skill 1
    skill1_dir = skills_dir / "test-driven-development"
    skill1_dir.mkdir()
    frontmatter1 = {
        'name': 'test-driven-development',
        'version': '1.0',
        'triggers': ['寫測試', 'pytest', 'TDD'],
        'priority': 'high'
    }
    content1 = f"---\n{yaml.dump(frontmatter1)}---\nTDD methodology"
    (skill1_dir / "SKILL.md").write_text(content1, encoding='utf-8')
    
    # Create skill 2
    skill2_dir = skills_dir / "systematic-debugging"
    skill2_dir.mkdir()
    frontmatter2 = {
        'name': 'systematic-debugging',
        'triggers': ['debug', '除錯', 'fix bugs']
    }
    content2 = f"---\n{yaml.dump(frontmatter2)}---\nDebug systematically"
    (skill2_dir / "SKILL.md").write_text(content2, encoding='utf-8')
    
    return tmp_project


# ============================================================================
# Test Main CLI
# ============================================================================

class TestMainCLI:
    """Test main CLI group and help."""
    
    def test_cli_help(self, runner):
        """Test CLI displays help message."""
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "LingmaFlow" in result.output
        assert "status" in result.output
        assert "advance" in result.output
        assert "skill" in result.output
        assert "agents" in result.output
        assert "init" in result.output
    
    def test_cli_version(self, runner):
        """Test CLI version option."""
        result = runner.invoke(cli, ['--version'])
        
        assert result.exit_code == 0
        assert "0.2.0" in result.output


# ============================================================================
# Test Status Command
# ============================================================================

class TestStatusCommand:
    """Test `lingmaflow status` command."""
    
    def test_status_displays_correct_information(self, runner, initialized_project):
        """Test status command displays correct information."""
        result = runner.invoke(cli, ['status', '--path', str(initialized_project)])
        
        assert result.exit_code == 0
        assert "Current Step: STEP-02" in result.output
        assert "Status: in_progress" in result.output
        assert "Last Result: Implementation complete" in result.output
        assert "Next Action: Write tests" in result.output
    
    def test_status_with_custom_path(self, runner, tmp_project):
        """Test status with custom path."""
        # Create TASK_STATE.md in custom location
        task_state_content = """# TASK_STATE

當前步驟：STEP-01
狀態：not_started
上一步結果：
下一步動作：Initialize
未解決問題：
最後更新：2024-01-01T00:00:00"""
        
        task_state_file = tmp_project / "TASK_STATE.md"
        task_state_file.write_text(task_state_content, encoding='utf-8')
        
        result = runner.invoke(cli, ['status', '--path', str(tmp_project)])
        
        assert result.exit_code == 0
        assert "Current Step: STEP-01" in result.output
        assert "Status: not_started" in result.output
    
    def test_status_handles_missing_files(self, runner, tmp_project):
        """Test status handles missing TASK_STATE.md gracefully."""
        result = runner.invoke(cli, ['status', '--path', str(tmp_project)])
        
        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "TASK_STATE.md not found" in result.output
    
    def test_status_with_unresolved_issues(self, runner, tmp_project):
        """Test status displays unresolved issues."""
        task_state_content = """# TASK_STATE

當前步驟：STEP-03
狀態：blocked
上一步結果：Testing failed
下一步動作：Fix issues
未解決問題：
- Database connection timeout
- API rate limiting
最後更新：2024-01-01T00:00:00"""
        
        task_state_file = tmp_project / "TASK_STATE.md"
        task_state_file.write_text(task_state_content, encoding='utf-8')
        
        result = runner.invoke(cli, ['status', '--path', str(tmp_project)])
        
        assert result.exit_code == 0
        assert "Unresolved Issues (2):" in result.output
        assert "Database connection timeout" in result.output
        assert "API rate limiting" in result.output


# ============================================================================
# Test Advance Command
# ============================================================================

class TestAdvanceCommand:
    """Test `lingmaflow advance` command."""
    
    def test_advance_command_updates_task_state(self, runner, initialized_project):
        """Test advance command updates TASK_STATE.md."""
        result = runner.invoke(
            cli, 
            ['advance', 'STEP-03', 'Tests completed', '--path', str(initialized_project)]
        )
        
        assert result.exit_code == 0
        assert "Advanced to STEP-03" in result.output
        assert "Result: Tests completed" in result.output
        
        # Verify file was updated
        task_state_file = initialized_project / "TASK_STATE.md"
        content = task_state_file.read_text(encoding='utf-8')
        assert "STEP-03" in content
        assert "Tests completed" in content
    
    def test_advance_handles_missing_files(self, runner, tmp_project):
        """Test advance handles missing TASK_STATE.md gracefully."""
        result = runner.invoke(cli, ['advance', 'STEP-02', 'Done', '--path', str(tmp_project)])
        
        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "TASK_STATE.md not found" in result.output


# ============================================================================
# Test Block Command
# ============================================================================

class TestBlockCommand:
    """Test `lingmaflow block` command."""
    
    def test_block_command_adds_unresolved_issue(self, runner, initialized_project):
        """Test block command adds unresolved issue."""
        result = runner.invoke(
            cli, 
            ['block', 'Database timeout', '--path', str(initialized_project)]
        )
        
        assert result.exit_code == 0
        assert "Task marked as blocked" in result.output
        assert "Issue: Database timeout" in result.output
        
        # Verify issue was added
        task_state_file = initialized_project / "TASK_STATE.md"
        manager = TaskStateManager(task_state_file)
        manager.load()
        assert "Database timeout" in manager.state.unresolved
    
    def test_block_handles_missing_files(self, runner, tmp_project):
        """Test block handles missing TASK_STATE.md gracefully."""
        result = runner.invoke(cli, ['block', 'Issue', '--path', str(tmp_project)])
        
        assert result.exit_code == 1
        assert "Error:" in result.output


# ============================================================================
# Test Resolve Command
# ============================================================================

class TestResolveCommand:
    """Test `lingmaflow resolve` command."""
    
    def test_resolve_command_removes_issue(self, runner, tmp_project):
        """Test resolve command removes issue."""
        # Create TASK_STATE.md with unresolved issues
        task_state_content = """# TASK_STATE

當前步驟：STEP-03
狀態：blocked
上一步結果：Failed
下一步動作：Fix
未解決問題：
- Issue 1
- Issue 2
最後更新：2024-01-01T00:00:00"""
        
        task_state_file = tmp_project / "TASK_STATE.md"
        task_state_file.write_text(task_state_content, encoding='utf-8')
        
        result = runner.invoke(
            cli, 
            ['resolve', '1', '--path', str(tmp_project)]
        )
        
        assert result.exit_code == 0
        assert "Resolved issue #1: Issue 1" in result.output
        
        # Verify issue was removed
        manager = TaskStateManager(task_state_file)
        manager.load()
        assert len(manager.state.unresolved) == 1
        assert "Issue 1" not in manager.state.unresolved
    
    def test_resolve_invalid_number(self, runner, tmp_project):
        """Test resolve with invalid issue number."""
        # Create TASK_STATE.md with one issue
        task_state_content = """# TASK_STATE

當前步驟：STEP-03
狀態：blocked
上一步結果：Failed
下一步動作：Fix
未解決問題：
- Issue 1
最後更新：2024-01-01T00:00:00"""
        
        task_state_file = tmp_project / "TASK_STATE.md"
        task_state_file.write_text(task_state_content, encoding='utf-8')
        
        result = runner.invoke(
            cli, 
            ['resolve', '999', '--path', str(tmp_project)]
        )
        
        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "Invalid issue number" in result.output
    
    def test_resolve_no_issues(self, runner, initialized_project):
        """Test resolve when no issues exist."""
        result = runner.invoke(
            cli, 
            ['resolve', '1', '--path', str(initialized_project)]
        )
        
        assert result.exit_code == 0
        assert "No unresolved issues" in result.output


# ============================================================================
# Test Skill Find Command
# ============================================================================

class TestSkillFindCommand:
    """Test `lingmaflow skill find` command."""
    
    def test_skill_find_with_matching_keyword(self, runner, project_with_skills):
        """Test skill find with matching keyword."""
        result = runner.invoke(
            cli, 
            ['skill', 'find', 'pytest', '--path', str(project_with_skills)]
        )
        
        assert result.exit_code == 0
        assert "Found 1 skill(s)" in result.output
        assert "test-driven-development" in result.output
    
    def test_skill_find_with_no_matches(self, runner, project_with_skills):
        """Test skill find with no matches."""
        result = runner.invoke(
            cli, 
            ['skill', 'find', 'nonexistent', '--path', str(project_with_skills)]
        )
        
        assert result.exit_code == 0
        assert "No skills found matching" in result.output
    
    def test_skill_find_is_case_insensitive(self, runner, project_with_skills):
        """Test skill find is case-insensitive."""
        result_upper = runner.invoke(
            cli, 
            ['skill', 'find', 'PYTEST', '--path', str(project_with_skills)]
        )
        
        result_lower = runner.invoke(
            cli, 
            ['skill', 'find', 'pytest', '--path', str(project_with_skills)]
        )
        
        assert result_upper.exit_code == 0
        assert result_lower.exit_code == 0
        assert "test-driven-development" in result_upper.output
        assert "test-driven-development" in result_lower.output


# ============================================================================
# Test Skill List Command
# ============================================================================

class TestSkillListCommand:
    """Test `lingmaflow skill list` command."""
    
    def test_skill_list_shows_all_skills(self, runner, project_with_skills):
        """Test skill list shows all skills."""
        result = runner.invoke(
            cli, 
            ['skill', 'list', '--path', str(project_with_skills)]
        )
        
        assert result.exit_code == 0
        assert "Found 2 skill(s)" in result.output
        assert "test-driven-development" in result.output
        assert "systematic-debugging" in result.output
    
    def test_skill_list_with_empty_registry(self, runner, tmp_project):
        """Test skill list with empty registry."""
        skills_dir = tmp_project / "skills"
        skills_dir.mkdir()
        
        result = runner.invoke(
            cli, 
            ['skill', 'list', '--path', str(skills_dir)]
        )
        
        assert result.exit_code == 0
        assert "No skills registered" in result.output


# ============================================================================
# Test Agents Generate Command
# ============================================================================

class TestAgentsGenerateCommand:
    """Test `lingmaflow agents generate` command."""
    
    def test_agents_generate_creates_agents_md(self, runner, project_with_skills):
        """Test agents generate creates AGENTS.md."""
        output_path = project_with_skills / "AGENTS.md"
        
        # Use project path (not skills path) for --path option
        result = runner.invoke(
            cli, 
            ['agents', 'generate', '--path', str(project_with_skills), '--force']
        )
        
        assert result.exit_code == 0
        assert "Generated" in result.output
        assert output_path.exists(), f"Output file not created. Exit code: {result.exit_code}, Output: {result.output}"
    
    def test_agents_generate_with_custom_output_path(self, runner, project_with_skills):
        """Test agents generate with custom output path."""
        output_path = project_with_skills / "custom_AGENTS.md"
        
        result = runner.invoke(
            cli, 
            [
                'agents', 'generate',
                '--output', str(output_path),
                '--path', str(project_with_skills / 'skills'),
                '--force'
            ]
        )
        
        assert result.exit_code == 0
        assert output_path.exists()
    
    def test_agents_generate_includes_all_skills(self, runner, project_with_skills):
        """Test agents generate includes all skills."""
        output_path = project_with_skills / "AGENTS.md"
        
        # Use project path (not skills path) for --path option
        result = runner.invoke(
            cli, 
            ['agents', 'generate', '--path', str(project_with_skills), '--force']
        )
        
        assert result.exit_code == 0
        
        content = output_path.read_text(encoding='utf-8')
        assert "test-driven-development" in content
        assert "systematic-debugging" in content


# ============================================================================
# Test Init Command
# ============================================================================

class TestInitCommand:
    """Test `lingmaflow init` command."""
    
    def test_init_creates_directory_structure(self, runner, tmp_project):
        """Test init creates directory structure."""
        result = runner.invoke(cli, ['init', '--path', str(tmp_project)])
        
        assert result.exit_code == 0
        assert (tmp_project / "skills").exists()
        assert (tmp_project / ".lingma").exists()
    
    def test_init_generates_correct_task_state(self, runner, tmp_project):
        """Test init generates correct TASK_STATE.md."""
        result = runner.invoke(cli, ['init', '--path', str(tmp_project)])
        
        assert result.exit_code == 0
        
        task_state_file = tmp_project / "TASK_STATE.md"
        assert task_state_file.exists()
        
        content = task_state_file.read_text(encoding='utf-8')
        assert "# TASK_STATE" in content
        assert "STEP-01" in content
        assert "not_started" in content
    
    def test_init_handles_existing_files_safely(self, runner, tmp_project):
        """Test init handles existing files safely."""
        # Create existing file
        task_state_file = tmp_project / "TASK_STATE.md"
        task_state_file.write_text("Existing content", encoding='utf-8')
        
        # Should prompt for confirmation
        result = runner.invoke(
            cli, 
            ['init', '--path', str(tmp_project)],
            input='n\n'  # Answer 'no' to confirmation
        )
        
        assert result.exit_code == 0
        assert "Warning:" in result.output
        assert "already exist" in result.output


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegrationWorkflow:
    """Test complete CLI workflow scenarios."""
    
    def test_full_workflow_init_status_advance(self, runner, tmp_project):
        """Test complete workflow: init → status → advance."""
        # Initialize
        result = runner.invoke(cli, ['init', '--path', str(tmp_project)])
        assert result.exit_code == 0
        
        # Check status
        result = runner.invoke(cli, ['status', '--path', str(tmp_project)])
        assert result.exit_code == 0
        assert "STEP-01" in result.output
        
        # Advance
        result = runner.invoke(
            cli, 
            ['advance', 'STEP-02', 'Initialized', '--path', str(tmp_project)]
        )
        assert result.exit_code == 0
        
        # Verify status changed
        result = runner.invoke(cli, ['status', '--path', str(tmp_project)])
        assert result.exit_code == 0
        assert "STEP-02" in result.output
        assert "Initialized" in result.output


# ============================================================================
# Tests for Execution Engine Commands (Phase 4)
# ============================================================================

class TestPrepareCommand:
    """Test prepare command."""
    
    def test_prepare_command_success_case(self, runner, project_with_skills):
        """Test prepare generates current_task.md."""
        # Create TASK_STATE.md with Done Conditions
        task_state_content = """當前步驟：STEP-01
狀態：in_progress
上一步結果：Setup done
下一步動作：Write tests for authentication
未解決問題：
最後更新：2024-01-01T00:00:00

## Done Conditions
- [ ] file:lingmaflow/core/auth.py
- [ ] pytest:tests/test_auth.py
"""
        task_state_file = project_with_skills / "TASK_STATE.md"
        task_state_file.write_text(task_state_content, encoding='utf-8')
        
        result = runner.invoke(
            cli,
            ['prepare', '--path', str(project_with_skills)]
        )
        
        assert result.exit_code == 0
        assert "Generated" in result.output
        
        # Check output file exists
        output_file = project_with_skills / ".lingmaflow" / "current_task.md"
        assert output_file.exists()
        
        content = output_file.read_text(encoding='utf-8')
        assert "STEP-01" in content
        assert "Write tests" in content
        assert "file:lingmaflow/core/auth.py" in content
    
    def test_prepare_command_missing_task_state(self, runner, tmp_project):
        """Test prepare with missing TASK_STATE.md."""
        result = runner.invoke(
            cli,
            ['prepare', '--path', str(tmp_project)]
        )
        
        assert result.exit_code == 1
        assert "Error:" in result.output
        assert "TASK_STATE.md not found" in result.output
    
    def test_prepare_command_skill_matching(self, runner, project_with_skills):
        """Test prepare matches skills based on next_action."""
        task_state_content = """當前步驟：STEP-01
狀態：in_progress
上一步結果：Setup done
下一步動作：開始寫 pytest 測試
未解決問題：
最後更新：2024-01-01T00:00:00
"""
        task_state_file = project_with_skills / "TASK_STATE.md"
        task_state_file.write_text(task_state_content, encoding='utf-8')
        
        result = runner.invoke(
            cli,
            ['prepare', '--path', str(project_with_skills)]
        )
        
        assert result.exit_code == 0
        
        output_file = project_with_skills / ".lingmaflow" / "current_task.md"
        content = output_file.read_text(encoding='utf-8')
        
        # Should match test-driven-development skill (contains "pytest")
        assert "test-driven-development" in content.lower() or "參考 Skill" in content


class TestVerifyCommand:
    """Test verify command."""
    
    def test_verify_command_all_pass(self, runner, tmp_project):
        """Test verify with all passing conditions."""
        # Create TASK_STATE.md with existing files
        task_state_content = """當前步驟：STEP-01
狀態：in_progress
上一步結果：Testing
下一步動作：Continue
未解決問題：
最後更新：2024-01-01T00:00:00

## Done Conditions
- [x] file:tests/test_cli.py
"""
        task_state_file = tmp_project / "TASK_STATE.md"
        task_state_file.write_text(task_state_content, encoding='utf-8')
        
        result = runner.invoke(
            cli,
            ['verify', '--path', str(tmp_project)]
        )
        
        assert result.exit_code == 0
        assert "✅" in result.output
    
    def test_verify_command_some_fail(self, runner, tmp_project):
        """Test verify with some failing conditions."""
        task_state_content = """當前步驟：STEP-01
狀態：in_progress
上一步結果：Testing
下一步動作：Continue
未解決問題：
最後更新：2024-01-01T00:00:00

## Done Conditions
- [ ] file:nonexistent_file.txt
"""
        task_state_file = tmp_project / "TASK_STATE.md"
        task_state_file.write_text(task_state_content, encoding='utf-8')
        
        result = runner.invoke(
            cli,
            ['verify', '--path', str(tmp_project)]
        )
        
        assert result.exit_code == 1
        assert "❌" in result.output
    
    def test_verify_command_no_done_conditions(self, runner, initialized_project):
        """Test verify with no Done Conditions block."""
        result = runner.invoke(
            cli,
            ['verify', '--path', str(initialized_project)]
        )
        
        assert result.exit_code == 0
        assert "無 Done Conditions" in result.output or "No" in result.output


class TestCheckpointCommand:
    """Test checkpoint command."""
    
    def test_checkpoint_command_verify_pass_and_advance(self, runner, tmp_project):
        """Test checkpoint advances when verify passes."""
        # Create TASK_STATE.md with passing condition
        task_state_content = """當前步驟：STEP-01
狀態：in_progress
上一步結果：Done
下一步動作：Next step
未解決問題：
最後更新：2024-01-01T00:00:00

## Done Conditions
- [x] file:tests/test_cli.py
"""
        task_state_file = tmp_project / "TASK_STATE.md"
        task_state_file.write_text(task_state_content, encoding='utf-8')
        
        result = runner.invoke(
            cli,
            ['checkpoint', 'STEP-02', '--path', str(tmp_project)]
        )
        
        assert result.exit_code == 0
        assert "Advanced to STEP-02" in result.output
        
        # Verify state was updated
        manager = TaskStateManager(task_state_file)
        manager.load()
        assert manager.state.current_step == "STEP-02"
    
    def test_checkpoint_command_verify_fail_no_advance(self, runner, tmp_project):
        """Test checkpoint doesn't advance when verify fails."""
        task_state_content = """當前步驟：STEP-01
狀態：in_progress
上一步結果：Done
下一步動作：Next step
未解決問題：
最後更新：2024-01-01T00:00:00

## Done Conditions
- [ ] file:nonexistent.txt
"""
        task_state_file = tmp_project / "TASK_STATE.md"
        task_state_file.write_text(task_state_content, encoding='utf-8')
        
        result = runner.invoke(
            cli,
            ['checkpoint', 'STEP-02', '--path', str(tmp_project)]
        )
        
        assert result.exit_code == 1
        assert "❌" in result.output
        assert "Cannot advance" in result.output or "Not all conditions" in result.output
        
        # Verify state was NOT updated
        manager = TaskStateManager(task_state_file)
        manager.load()
        assert manager.state.current_step == "STEP-01"  # Still at original step
    
    def test_checkpoint_command_missing_next_step(self, runner, initialized_project):
        """Test checkpoint without next_step argument."""
        result = runner.invoke(
            cli,
            ['checkpoint', '--path', str(initialized_project)]
        )
        
        # Click should show usage error for missing required argument
        assert result.exit_code != 0
        assert "Usage:" in result.output or "Missing" in result.output
