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
        # Create sentinel file inside tmp_project — self-contained, no cwd dependency
        sentinel_file = tmp_project / 'sentinel.txt'
        sentinel_file.write_text('exists')

        task_state_content = f"""當前步驟：STEP-01
狀態：in_progress
上一步結果：Testing
下一步動作：Continue
未解決問題：
最後更新：2024-01-01T00:00:00

## Done Conditions
    - [x] file:{sentinel_file}
"""
        task_state_file = tmp_project / 'TASK_STATE.md'
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
    
    def test_checkpoint_calls_prepare_on_success(self, runner, tmp_project):
        """Test checkpoint auto-executes prepare on success."""
        import json
        
        # Create TASK_STATE.md with passing condition
        task_state_content = """當前步驟：STEP-01
狀態：in_progress
上一步結果：Done
下一步動作：Write tests
未解決問題：
最後更新：2024-01-01T00:00:00

## Done Conditions
- [x] file:tests/test_cli.py
"""
        task_state_file = tmp_project / "TASK_STATE.md"
        task_state_file.write_text(task_state_content, encoding='utf-8')
        
        # Create skills directory
        skills_dir = tmp_project / 'skills' / 'test-driven-development'
        skills_dir.mkdir(parents=True)
        (skills_dir / 'SKILL.md').write_text("---\nname: test-driven-development\ntriggers:\n  - 測試\n  - pytest\n---\n\nTDD content")
        
        result = runner.invoke(
            cli,
            ['checkpoint', 'STEP-02', '--path', str(tmp_project)]
        )
        
        assert result.exit_code == 0
        assert "Advanced to STEP-02" in result.output
        assert "current_task.md 已自動更新" in result.output
        
        # Verify current_task.md was created
        current_task_file = tmp_project / '.lingmaflow' / 'current_task.md'
        assert current_task_file.exists()
        
        content = current_task_file.read_text(encoding='utf-8')
        assert "STEP-02" in content
        assert "Write tests" in content
    
    def test_checkpoint_succeeds_even_if_prepare_fails(self, runner, tmp_project):
        """Test checkpoint succeeds even when prepare fails.
        
        Uses mock.patch instead of chmod(0o000) to avoid root-environment false positives.
        """
        from unittest.mock import patch

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

        # Mock _run_prepare to raise PermissionError — avoids chmod root bypass
        with patch(
            "lingmaflow.cli.lingmaflow._run_prepare",
            side_effect=PermissionError("mocked permission denied")
        ):
            result = runner.invoke(
                cli,
                ['checkpoint', 'STEP-02', '--path', str(tmp_project)]
            )

        # Checkpoint should still succeed
        assert result.exit_code == 0
        assert "Advanced to STEP-02" in result.output
        # Should show warning about prepare failure
        assert "prepare" in result.output.lower() and ("失敗" in result.output or "fail" in result.output.lower())

        # Verify state was still updated despite prepare failure
        manager = TaskStateManager(task_state_file)
        manager.load()
        assert manager.state.current_step == "STEP-02"


# ============================================================================
# Tests for harness CLI commands
# ============================================================================

class TestHarnessInitCommand:
    """Test harness init command."""

    def test_harness_init_creates_files(self, runner, tmp_project):
        """Test harness init creates tasks.json and PROGRESS.md."""
        change_dir = tmp_project / 'openspec' / 'changes' / 'test-change'
        change_dir.mkdir(parents=True)

        tasks_md = change_dir / 'tasks.md'
        tasks_md.write_text(
            "- [x] 1.1 Setup\n"
            "- [ ] 1.2 Implement\n",
            encoding='utf-8'
        )

        result = runner.invoke(cli, [
            'harness', 'init', 'test-change',
            '--path', str(tmp_project)
        ])

        assert result.exit_code == 0
        assert (change_dir / 'tasks.json').exists()
        assert (change_dir / 'PROGRESS.md').exists()

    def test_harness_init_missing_change_dir(self, runner, tmp_project):
        """Test harness init fails when change dir doesn't exist."""
        result = runner.invoke(cli, [
            'harness', 'init', 'nonexistent-change',
            '--path', str(tmp_project)
        ])

        assert result.exit_code == 1
        assert 'Error' in result.output

    def test_harness_init_converts_tasks_correctly(self, runner, tmp_project):
        """Test harness init converts tasks.md to correct JSON."""
        import json
        change_dir = tmp_project / 'openspec' / 'changes' / 'test-change'
        change_dir.mkdir(parents=True)
        (change_dir / 'tasks.md').write_text(
            "- [x] 1.1 Done task\n"
            "- [ ] 1.2 Pending task\n",
            encoding='utf-8'
        )

        runner.invoke(cli, ['harness', 'init', 'test-change', '--path', str(tmp_project)])

        tasks = json.loads((change_dir / 'tasks.json').read_text())
        assert len(tasks) == 2
        assert tasks[0]['done'] is True
        assert tasks[1]['done'] is False


class TestHarnessDoneCommand:
    """Test harness done command."""

    def _setup_change(self, tmp_project):
        """Helper to create initialized change dir."""
        import json
        change_dir = tmp_project / 'openspec' / 'changes' / 'test-change'
        change_dir.mkdir(parents=True)
        tasks = [
            {'id': '1.1', 'description': 'Task one', 'done': False,
             'started_at': None, 'completed_at': None, 'notes': ''},
            {'id': '1.2', 'description': 'Task two', 'done': False,
             'started_at': None, 'completed_at': None, 'notes': ''},
        ]
        (change_dir / 'tasks.json').write_text(json.dumps(tasks), encoding='utf-8')
        (change_dir / 'PROGRESS.md').write_text('', encoding='utf-8')
        return change_dir

    def test_harness_done_marks_task(self, runner, tmp_project):
        """Test harness done marks task as complete."""
        import json
        change_dir = self._setup_change(tmp_project)

        result = runner.invoke(cli, [
            'harness', 'done', '1.1',
            '--change', 'test-change',
            '--path', str(tmp_project)
        ])

        assert result.exit_code == 0
        tasks = json.loads((change_dir / 'tasks.json').read_text())
        assert tasks[0]['done'] is True

    def test_harness_done_with_notes(self, runner, tmp_project):
        """Test harness done saves notes."""
        import json
        change_dir = self._setup_change(tmp_project)

        runner.invoke(cli, [
            'harness', 'done', '1.1',
            '--change', 'test-change',
            '--notes', 'used tenacity v8',
            '--path', str(tmp_project)
        ])

        tasks = json.loads((change_dir / 'tasks.json').read_text())
        assert tasks[0]['notes'] == 'used tenacity v8'

    def test_harness_done_invalid_task_id(self, runner, tmp_project):
        """Test harness done fails for non-existent task."""
        self._setup_change(tmp_project)

        result = runner.invoke(cli, [
            'harness', 'done', '9.9',
            '--change', 'test-change',
            '--path', str(tmp_project)
        ])

        assert result.exit_code == 1
        assert 'Error' in result.output


class TestHarnessResumeCommand:
    """Test harness resume command."""

    def _setup_change(self, tmp_project, tasks):
        """Helper to create initialized change dir."""
        import json
        change_dir = tmp_project / 'openspec' / 'changes' / 'test-change'
        change_dir.mkdir(parents=True)
        (change_dir / 'tasks.json').write_text(json.dumps(tasks), encoding='utf-8')
        (change_dir / 'PROGRESS.md').write_text('', encoding='utf-8')
        return change_dir

    def test_harness_resume_shows_brief(self, runner, tmp_project):
        """Test harness resume outputs RESUME BRIEF."""
        self._setup_change(tmp_project, [
            {'id': '1.1', 'description': 'Done', 'done': True,
             'started_at': None, 'completed_at': None, 'notes': ''},
            {'id': '1.2', 'description': 'Next', 'done': False,
             'started_at': None, 'completed_at': None, 'notes': ''},
        ])

        result = runner.invoke(cli, [
            'harness', 'resume',
            '--change', 'test-change',
            '--path', str(tmp_project)
        ])

        assert result.exit_code == 0
        assert 'RESUME BRIEF' in result.output
        assert 'task 1.2' in result.output

    def test_harness_resume_missing_change(self, runner, tmp_project):
        """Test harness resume fails when change not found."""
        result = runner.invoke(cli, [
            'harness', 'resume',
            '--change', 'nonexistent',
            '--path', str(tmp_project)
        ])

        assert result.exit_code == 1


class TestHarnessStatusCommand:
    """Test harness status command."""

    def test_harness_status_shows_progress(self, runner, tmp_project):
        """Test harness status shows correct progress."""
        import json
        change_dir = tmp_project / 'openspec' / 'changes' / 'test-change'
        change_dir.mkdir(parents=True)
        tasks = [
            {'id': '1.1', 'description': 'Done', 'done': True,
             'started_at': None, 'completed_at': None, 'notes': ''},
            {'id': '1.2', 'description': 'Pending', 'done': False,
             'started_at': None, 'completed_at': None, 'notes': ''},
        ]
        (change_dir / 'tasks.json').write_text(json.dumps(tasks), encoding='utf-8')
        (change_dir / 'PROGRESS.md').write_text('', encoding='utf-8')

        result = runner.invoke(cli, [
            'harness', 'status',
            '--change', 'test-change',
            '--path', str(tmp_project)
        ])

        assert result.exit_code == 0
        assert '1/2' in result.output
        assert '50%' in result.output


class TestHarnessLogCommand:
    """Test harness log command."""

    def test_harness_log_writes_progress(self, runner, tmp_project):
        """Test harness log writes session to PROGRESS.md."""
        change_dir = tmp_project / 'openspec' / 'changes' / 'test-change'
        change_dir.mkdir(parents=True)
        (change_dir / 'tasks.json').write_text('[]', encoding='utf-8')
        (change_dir / 'PROGRESS.md').write_text('', encoding='utf-8')

        result = runner.invoke(cli, [
            'harness', 'log',
            '--change', 'test-change',
            '--completed', '1.1,1.2',
            '--leftover', 'task 1.3 in progress',
            '--failed', 'attempt 1 failed',
            '--next', 'continue 1.3',
            '--path', str(tmp_project)
        ])

        assert result.exit_code == 0
        content = (change_dir / 'PROGRESS.md').read_text()
        assert '## Session' in content
        assert 'task 1.3 in progress' in content


class TestHarnessInitActiveChange:
    """Tests for harness init writing active_change file."""

    def test_harness_init_writes_active_change(self, runner, tmp_project):
        """harness init 後 .lingmaflow/active_change 存在且內容正確。"""
        change_dir = tmp_project / 'openspec' / 'changes' / 'my-change'
        change_dir.mkdir(parents=True)
        (change_dir / 'tasks.md').write_text("- [ ] 1.1 Setup\n", encoding='utf-8')

        result = runner.invoke(cli, ['harness', 'init', 'my-change', '--path', str(tmp_project)])

        assert result.exit_code == 0
        active_change_file = tmp_project / '.lingmaflow' / 'active_change'
        assert active_change_file.exists()
        assert active_change_file.read_text(encoding='utf-8').strip() == 'my-change'

    def test_harness_init_overwrites_active_change(self, runner, tmp_project):
        """harness init 覆蓋已存在的 active_change。"""
        # 先建立舊的 active_change
        lingmaflow_dir = tmp_project / '.lingmaflow'
        lingmaflow_dir.mkdir()
        (lingmaflow_dir / 'active_change').write_text('old-change', encoding='utf-8')

        change_dir = tmp_project / 'openspec' / 'changes' / 'new-change'
        change_dir.mkdir(parents=True)
        (change_dir / 'tasks.md').write_text("- [ ] 1.1 Setup\n", encoding='utf-8')

        result = runner.invoke(cli, ['harness', 'init', 'new-change', '--path', str(tmp_project)])

        assert result.exit_code == 0
        active = (tmp_project / '.lingmaflow' / 'active_change').read_text(encoding='utf-8').strip()
        assert active == 'new-change'


class TestStatusHarnessBlock:
    """Tests for status command harness block integration."""

    def _setup_task_state(self, tmp_project):
        content = """當前步驟：PHASE-6
狀態：in_progress
上一步結果：Done
下一步動作：Continue
未解決問題：
最後更新：2026-04-03T10:00:00

## Done Conditions
- [ ] file:dummy.py
"""
        (tmp_project / 'TASK_STATE.md').write_text(content, encoding='utf-8')

    def _setup_harness(self, tmp_project, change_name='my-change'):
        import json
        change_dir = tmp_project / 'openspec' / 'changes' / change_name
        change_dir.mkdir(parents=True)
        tasks = [
            {"id": "1.1", "description": "Setup", "done": True,
             "started_at": None, "completed_at": "2026-04-03T10:00:00Z", "notes": ""},
            {"id": "1.2", "description": "Implement", "done": False,
             "started_at": None, "completed_at": None, "notes": ""},
        ]
        (change_dir / 'tasks.json').write_text(json.dumps(tasks), encoding='utf-8')
        (change_dir / 'PROGRESS.md').write_text('', encoding='utf-8')

        lingmaflow_dir = tmp_project / '.lingmaflow'
        lingmaflow_dir.mkdir(exist_ok=True)
        (lingmaflow_dir / 'active_change').write_text(change_name, encoding='utf-8')

    def test_status_shows_harness_block_when_active_change_exists(self, runner, tmp_project):
        """active_change 存在時 status 顯示 harness 區塊。"""
        self._setup_task_state(tmp_project)
        self._setup_harness(tmp_project)

        result = runner.invoke(cli, ['status', '--path', str(tmp_project)])

        assert result.exit_code == 0
        assert '── Harness' in result.output
        assert 'my-change' in result.output
        assert '1/2 tasks' in result.output
        assert 'Current task: 1.2' in result.output

    def test_status_no_harness_block_without_active_change(self, runner, tmp_project):
        """active_change 不存在時 status 不顯示 harness 區塊（向後相容）。"""
        self._setup_task_state(tmp_project)

        result = runner.invoke(cli, ['status', '--path', str(tmp_project)])

        assert result.exit_code == 0
        assert '── Harness' not in result.output
        assert 'Unresolved Issues: None' in result.output
