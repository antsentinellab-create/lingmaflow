"""
Unit tests for Agents Injector module.

Tests cover all AGENTS.md generation, injection, and validation functionality.
"""

import pytest
from pathlib import Path
import os

from lingmaflow.core.agents_injector import (
    AgentsInjector,
    InjectionError,
)
from lingmaflow.core.skill_registry import Skill, SkillRegistry


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def tmp_agents_dir(tmp_path):
    """Create a temporary directory for AGENTS.md output."""
    return tmp_path / "agents"


@pytest.fixture
def mock_registry_with_skills(tmp_path):
    """Create a mock SkillRegistry with sample skills."""
    registry = SkillRegistry(tmp_path / "skills")
    
    # Create mock skills manually (without scanning)
    skill1 = Skill(
        name="test-driven-development",
        triggers=["寫測試", "pytest", "TDD"],
        content="TDD methodology",
        path=tmp_path / "skills/tdd/SKILL.md",
        version="1.0",
        priority="high"
    )
    
    skill2 = Skill(
        name="systematic-debugging",
        triggers=["debug", "除錯", "fix bugs"],
        content="Debug systematically",
        path=tmp_path / "skills/debug/SKILL.md",
        version="2.0",
        priority="normal"
    )
    
    skill3 = Skill(
        name="brainstorming",
        triggers=["創意", "ideas", "brainstorm"],
        content="Generate ideas",
        path=tmp_path / "skills/brainstorm/SKILL.md"
    )
    
    registry.skills = [skill1, skill2, skill3]
    return registry


@pytest.fixture
def mock_registry_empty(tmp_path):
    """Create an empty mock SkillRegistry."""
    registry = SkillRegistry(tmp_path / "skills")
    registry.skills = []
    return registry


@pytest.fixture
def injector(mock_registry_with_skills, tmp_path):
    """Create an AgentsInjector with mock registry."""
    task_state_path = tmp_path / "TASK_STATE.md"
    return AgentsInjector(mock_registry_with_skills, task_state_path)


@pytest.fixture
def injector_empty(mock_registry_empty, tmp_path):
    """Create an AgentsInjector with empty registry."""
    task_state_path = tmp_path / "TASK_STATE.md"
    return AgentsInjector(mock_registry_empty, task_state_path)


# ============================================================================
# Test InjectionError Exception
# ============================================================================

class TestInjectionError:
    """Test InjectionError exception behavior."""
    
    def test_inherits_from_exception(self):
        """Test InjectionError can be caught as Exception."""
        try:
            raise InjectionError("Test error")
        except Exception as e:
            assert isinstance(e, InjectionError)
            assert str(e) == "Test error"
    
    def test_descriptive_error_message(self):
        """Test InjectionError includes descriptive message."""
        error = InjectionError("Cannot write to /path: Permission denied")
        assert "Cannot write to" in str(error)
        assert "/path" in str(error)


# ============================================================================
# Test Generate Method - Basic Functionality
# ============================================================================

class TestGenerateMethod:
    """Test AgentsInjector.generate() method."""
    
    def test_generate_includes_all_skill_names(self, injector):
        """Test generate() includes all skill names from registry."""
        content = injector.generate()
        
        assert "test-driven-development" in content
        assert "systematic-debugging" in content
        assert "brainstorming" in content
    
    def test_generate_includes_fixed_sections(self, injector):
        """Test generate() includes fixed sections text."""
        content = injector.generate()
        
        # Check title
        assert "# LingmaFlow — Agent 執行規則" in content
        
        # Check startup section
        assert "## 每次啟動必做" in content
        assert "cat TASK_STATE.md" in content
        
        # Check done condition section
        assert "## Done Condition 規則" in content
        
        # Check error handling section
        assert "## 錯誤處置" in content
    
    def test_generate_with_empty_registry(self, injector_empty):
        """Test generate() with empty registry still works."""
        content = injector_empty.generate()
        
        # Should still have all fixed sections
        assert "# LingmaFlow — Agent 執行規則" in content
        assert "## 可用 Skill 清單" in content
        
        # Skills section should indicate no skills available
        assert "目前沒有可用的技能" in content or "## 可用 Skill 清單" in content
    
    def test_generate_formats_skill_list_correctly(self, injector):
        """Test generate() formats skill list correctly."""
        content = injector.generate()
        
        # Check markdown list format: `- **name**: trigger1, trigger2`
        assert "- **test-driven-development**:" in content
        assert "寫測試" in content
        assert "pytest" in content
        assert "TDD" in content
    
    def test_generate_returns_consistent_content(self, injector):
        """Test generate() returns consistent content across multiple calls."""
        content1 = injector.generate()
        content2 = injector.generate()
        content3 = injector.generate()
        
        assert content1 == content2 == content3


# ============================================================================
# Test Inject Method
# ============================================================================

class TestInjectMethod:
    """Test AgentsInjector.inject() method."""
    
    def test_inject_writes_file_with_correct_content(self, injector, tmp_agents_dir):
        """Test inject() writes file with correct content."""
        output_path = tmp_agents_dir / "AGENTS.md"
        
        injector.inject(output_path)
        
        # Verify file exists
        assert output_path.exists()
        
        # Verify content matches generate()
        expected_content = injector.generate()
        actual_content = output_path.read_text(encoding='utf-8')
        
        assert actual_content == expected_content
    
    def test_inject_creates_file_if_doesnt_exist(self, injector, tmp_agents_dir):
        """Test inject() creates file if it doesn't exist."""
        output_path = tmp_agents_dir / "AGENTS.md"
        
        # Ensure file doesn't exist
        assert not output_path.exists()
        
        # Inject should create it
        injector.inject(output_path)
        
        assert output_path.exists()
    
    def test_inject_uses_utf8_encoding(self, injector, tmp_agents_dir):
        """Test inject() uses UTF-8 encoding."""
        output_path = tmp_agents_dir / "AGENTS.md"
        
        injector.inject(output_path)
        
        # Read raw bytes to verify UTF-8 encoding
        content_bytes = output_path.read_bytes()
        
        # Chinese characters should be properly encoded
        assert b'\xe5\xaf\xab' in content_bytes  # "寫" in UTF-8
        assert b'\xe9\x99\xa4\xe9\x8c\xaf' in content_bytes  # "除錯" in UTF-8
    
    def test_inject_creates_parent_directories(self, injector, tmp_agents_dir):
        """Test inject() creates parent directories if needed."""
        output_path = tmp_agents_dir / "nested/deep/path/AGENTS.md"
        
        # Ensure parent directories don't exist
        assert not output_path.parent.exists()
        
        # Inject should create them
        injector.inject(output_path)
        
        assert output_path.exists()
        assert output_path.parent.exists()
    
    def test_inject_unwritable_path_raises_error(self, injector, tmp_path):
        """Test inject() to unwritable path raises InjectionError."""
        # Try to write to a path that's likely unwritable
        # Using root directory which typically requires sudo
        output_path = Path("/root/cannot_write_here_AGENTS.md")
        
        with pytest.raises(InjectionError, match="Cannot write to"):
            injector.inject(output_path)
    
    def test_injected_file_content_matches_generate_output(self, injector, tmp_agents_dir):
        """Test injected file content matches generate() output."""
        output_path = tmp_agents_dir / "AGENTS.md"
        
        generated = injector.generate()
        injector.inject(output_path)
        written = output_path.read_text(encoding='utf-8')
        
        assert written == generated


# ============================================================================
# Test Update Method
# ============================================================================

class TestUpdateMethod:
    """Test AgentsInjector.update() method."""
    
    def test_update_overwrites_existing_file(self, injector, tmp_agents_dir):
        """Test update() overwrites existing file."""
        output_path = tmp_agents_dir / "AGENTS.md"
        
        # Create parent directory first
        tmp_agents_dir.mkdir(exist_ok=True)
        
        # Create initial file
        initial_content = "Initial content"
        output_path.write_text(initial_content, encoding='utf-8')
        
        # Update should overwrite
        injector.update(output_path)
        
        # Content should be different now
        new_content = output_path.read_text(encoding='utf-8')
        assert new_content != initial_content
        assert new_content == injector.generate()
    
    def test_update_creates_file_if_doesnt_exist(self, injector, tmp_agents_dir):
        """Test update() creates file if it doesn't exist."""
        output_path = tmp_agents_dir / "AGENTS.md"
        
        # Ensure file doesn't exist
        assert not output_path.exists()
        
        # Update should create it
        injector.update(output_path)
        
        assert output_path.exists()
        assert output_path.read_text(encoding='utf-8') == injector.generate()
    
    def test_update_unwritable_path_raises_error(self, injector, tmp_path):
        """Test update() to unwritable path raises InjectionError."""
        output_path = Path("/root/cannot_write_here_AGENTS.md")
        
        with pytest.raises(InjectionError, match="Cannot write to"):
            injector.update(output_path)


# ============================================================================
# Test Skill List Generation
# ============================================================================

class TestSkillListGeneration:
    """Test dynamic skill list generation."""
    
    def test_single_skill_format(self, tmp_path):
        """Test formatting of a single skill."""
        registry = SkillRegistry(tmp_path / "skills")
        skill = Skill(
            name="single-skill",
            triggers=["trigger1"],
            content="",
            path=tmp_path / "skills/single/SKILL.md"
        )
        registry.skills = [skill]
        
        injector = AgentsInjector(registry, tmp_path / "TASK_STATE.md")
        content = injector.generate()
        
        assert "- **single-skill**: trigger1" in content
    
    def test_multiple_triggers_format(self, tmp_path):
        """Test formatting of skill with multiple triggers."""
        registry = SkillRegistry(tmp_path / "skills")
        skill = Skill(
            name="multi-trigger-skill",
            triggers=["t1", "t2", "t3"],
            content="",
            path=tmp_path / "skills/multi/SKILL.md"
        )
        registry.skills = [skill]
        
        injector = AgentsInjector(registry, tmp_path / "TASK_STATE.md")
        content = injector.generate()
        
        assert "- **multi-trigger-skill**: t1, t2, t3" in content
    
    def test_chinese_triggers_preserved(self, tmp_path):
        """Test that Chinese triggers are preserved correctly."""
        registry = SkillRegistry(tmp_path / "skills")
        skill = Skill(
            name="chinese-skill",
            triggers=["寫測試", "除錯", "創意"],
            content="",
            path=tmp_path / "skills/chinese/SKILL.md"
        )
        registry.skills = [skill]
        
        injector = AgentsInjector(registry, tmp_path / "TASK_STATE.md")
        content = injector.generate()
        
        # Check that Chinese characters are present (separated by comma and space)
        assert "- **chinese-skill**:" in content
        assert "寫測試" in content
        assert "除錯" in content
        assert "創意" in content


# ============================================================================
# Test Fixed Content Sections
# ============================================================================

class TestFixedContentSections:
    """Test that fixed content sections are always present."""
    
    def test_title_always_present(self, injector):
        """Test title is always present."""
        content = injector.generate()
        assert content.startswith("# LingmaFlow — Agent 執行規則")
    
    def test_startup_section_order(self, injector):
        """Test startup section appears after title."""
        content = injector.generate()
        
        title_pos = content.find("# LingmaFlow — Agent 執行規則")
        startup_pos = content.find("## 每次啟動必做")
        
        assert title_pos < startup_pos
    
    def test_skills_section_between_startup_and_done(self, injector):
        """Test skills section appears between startup and done condition."""
        content = injector.generate()
        
        startup_pos = content.find("## 每次啟動必做")
        skills_pos = content.find("## 可用 Skill 清單")
        done_pos = content.find("## Done Condition 規則")
        
        assert startup_pos < skills_pos < done_pos
    
    def test_error_handling_section_last(self, injector):
        """Test error handling section appears last."""
        content = injector.generate()
        
        done_pos = content.find("## Done Condition 規則")
        error_pos = content.find("## 錯誤處置")
        
        assert done_pos < error_pos


# ============================================================================
# Integration Test - Complete Workflow
# ============================================================================

class TestIntegrationWorkflow:
    """Test complete workflow scenarios."""
    
    def test_full_workflow_generate_inject_verify(self, injector, tmp_agents_dir):
        """Test complete workflow: generate → inject → verify."""
        output_path = tmp_agents_dir / "AGENTS.md"
        
        # Generate
        generated = injector.generate()
        
        # Inject
        injector.inject(output_path)
        
        # Verify
        assert output_path.exists()
        
        written = output_path.read_text(encoding='utf-8')
        assert written == generated
        
        # Verify all skills are listed
        for skill in injector.registry.skills:
            assert skill.name in written
    
    def test_update_after_registry_change(self, tmp_path):
        """Test updating AGENTS.md after registry changes."""
        registry = SkillRegistry(tmp_path / "skills")
        
        # Initial skill
        skill1 = Skill(
            name="initial-skill",
            triggers=["test"],
            content="",
            path=tmp_path / "skills/initial/SKILL.md"
        )
        registry.skills = [skill1]
        
        injector = AgentsInjector(registry, tmp_path / "TASK_STATE.md")
        output_path = tmp_path / "AGENTS.md"
        
        # First injection
        injector.inject(output_path)
        content1 = output_path.read_text(encoding='utf-8')
        
        # Add new skill
        skill2 = Skill(
            name="new-skill",
            triggers=["new"],
            content="",
            path=tmp_path / "skills/new/SKILL.md"
        )
        registry.skills.append(skill2)
        
        # Update
        injector.update(output_path)
        content2 = output_path.read_text(encoding='utf-8')
        
        # Content should be different
        assert content1 != content2
        
        # New skill should be present
        assert "new-skill" in content2
        
        # Old skill should still be present
        assert "initial-skill" in content2


# ============================================================================
# Harness Detection Tests (NEW for P0 improvements)
# ============================================================================

class TestHarnessDetection:
    """Tests for _has_harness method."""
    
    def test_has_harness_returns_false_when_no_tasks_json(self, tmp_path):
        """Test _has_harness returns False when no tasks.json exists."""
        registry = SkillRegistry(tmp_path / "skills")
        injector = AgentsInjector(registry, tmp_path / "TASK_STATE.md")
        
        # Create openspec structure without tasks.json
        openspec_changes = tmp_path / "openspec" / "changes"
        openspec_changes.mkdir(parents=True)
        
        result = injector._has_harness(tmp_path)
        assert result is False
    
    def test_has_harness_returns_true_when_tasks_json_exists(self, tmp_path):
        """Test _has_harness returns True when tasks.json exists."""
        registry = SkillRegistry(tmp_path / "skills")
        injector = AgentsInjector(registry, tmp_path / "TASK_STATE.md")
        
        # Create openspec structure with tasks.json
        change_dir = tmp_path / "openspec" / "changes" / "test-change"
        change_dir.mkdir(parents=True)
        (change_dir / "tasks.json").write_text("[]")
        
        result = injector._has_harness(tmp_path)
        assert result is True
    
    def test_has_harness_returns_false_when_no_openspec_dir(self, tmp_path):
        """Test _has_harness returns False when openspec directory doesn't exist."""
        registry = SkillRegistry(tmp_path / "skills")
        injector = AgentsInjector(registry, tmp_path / "TASK_STATE.md")

        result = injector._has_harness(tmp_path)
        assert result is False

    def test_has_harness_returns_false_on_permission_error(self, tmp_path):
        """Test _has_harness returns False when openspec dir is not readable."""
        from unittest.mock import patch

        registry = SkillRegistry(tmp_path / "skills")
        injector = AgentsInjector(registry, tmp_path / "TASK_STATE.md")

        openspec_path = tmp_path / "openspec" / "changes"
        openspec_path.mkdir(parents=True)

        with patch("pathlib.Path.iterdir", side_effect=PermissionError("mocked")):
            result = injector._has_harness(tmp_path)

        assert result is False

    def test_has_harness_ignores_files_in_changes_dir(self, tmp_path):
        """Test _has_harness skips non-directory entries in changes/."""
        registry = SkillRegistry(tmp_path / "skills")
        injector = AgentsInjector(registry, tmp_path / "TASK_STATE.md")

        openspec_path = tmp_path / "openspec" / "changes"
        openspec_path.mkdir(parents=True)
        # Place a file (not a dir) named tasks.json directly in changes/
        (openspec_path / "tasks.json").write_text("[]")

        result = injector._has_harness(tmp_path)
        assert result is False


class TestGenerateWithHarness:
    """Tests for generate method with harness detection."""
    
    def test_generate_injects_harness_rules_when_harness_detected(self, tmp_path):
        """Test generate includes HARNESS_RULES when harness is detected."""
        registry = SkillRegistry(tmp_path / "skills")
        injector = AgentsInjector(registry, tmp_path / "TASK_STATE.md")
        
        # Create openspec structure with tasks.json
        change_dir = tmp_path / "openspec" / "changes" / "test-change"
        change_dir.mkdir(parents=True)
        (change_dir / "tasks.json").write_text("[]")
        
        content = injector.generate(project_path=tmp_path)
        
        assert "harness 執行規則" in content
        assert "lingmaflow harness done" in content
        assert "lingmaflow harness log" in content
    
    def test_generate_backward_compatible_without_project_path(self, tmp_path):
        """Test generate works without project_path (backward compatibility)."""
        registry = SkillRegistry(tmp_path / "skills")
        injector = AgentsInjector(registry, tmp_path / "TASK_STATE.md")
        
        # Should work without project_path
        content = injector.generate()
        
        # Should not include harness rules when project_path is None
        assert "harness 執行規則" not in content
    
    def test_generate_no_harness_rules_when_no_harness(self, tmp_path):
        """Test generate doesn't include harness rules when harness not detected."""
        registry = SkillRegistry(tmp_path / "skills")
        injector = AgentsInjector(registry, tmp_path / "TASK_STATE.md")
        
        # Create openspec structure without tasks.json
        openspec_changes = tmp_path / "openspec" / "changes"
        openspec_changes.mkdir(parents=True)
        
        content = injector.generate(project_path=tmp_path)
        
        assert "harness 執行規則" not in content


class TestStartupSection:
    """Tests for startup_section content in generated AGENTS.md."""

    def test_startup_section_contains_task_state(self, tmp_path):
        """Test generated AGENTS.md instructs reading TASK_STATE.md."""
        registry = SkillRegistry(tmp_path / "skills")
        injector = AgentsInjector(registry, tmp_path / "TASK_STATE.md")
        content = injector.generate()
        assert "cat TASK_STATE.md" in content

    def test_startup_section_contains_current_task(self, tmp_path):
        """Test generated AGENTS.md instructs reading current_task.md."""
        registry = SkillRegistry(tmp_path / "skills")
        injector = AgentsInjector(registry, tmp_path / "TASK_STATE.md")
        content = injector.generate()
        assert "cat .lingmaflow/current_task.md" in content

    def test_startup_section_step_order(self, tmp_path):
        """Test current_task.md read comes before done condition check."""
        registry = SkillRegistry(tmp_path / "skills")
        injector = AgentsInjector(registry, tmp_path / "TASK_STATE.md")
        content = injector.generate()
        pos_task_state = content.index("cat TASK_STATE.md")
        pos_current_task = content.index("cat .lingmaflow/current_task.md")
        pos_done_cond = content.index("done condition")
        assert pos_task_state < pos_current_task < pos_done_cond
