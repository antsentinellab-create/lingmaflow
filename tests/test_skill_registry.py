"""
Unit tests for Skill Registry module.

Tests cover all skill discovery, query, and validation functionality.
"""

import pytest
from pathlib import Path
import yaml

from lingmaflow.core.skill_registry import (
    Skill,
    SkillRegistry,
    MalformedSkillError,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def tmp_skills_dir(tmp_path):
    """Create a temporary directory for skills."""
    return tmp_path / "skills"


@pytest.fixture
def registry(tmp_skills_dir):
    """Create a SkillRegistry with a temporary directory."""
    return SkillRegistry(tmp_skills_dir)


def create_skill_file(path: Path, frontmatter: dict, body: str = "") -> None:
    """Helper function to create a SKILL.md file with YAML frontmatter.
    
    Args:
        path: Directory path where SKILL.md will be created
        frontmatter: Dictionary of frontmatter fields
        body: Optional markdown body content
    """
    path.mkdir(parents=True, exist_ok=True)
    skill_file = path / "SKILL.md"
    
    # Build frontmatter section
    frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
    content = f"---\n{frontmatter_yaml}---\n{body}"
    
    skill_file.write_text(content, encoding='utf-8')


# ============================================================================
# Test Skill Dataclass
# ============================================================================

class TestSkillDataclass:
    """Test Skill dataclass initialization and defaults."""
    
    def test_create_skill_with_all_fields(self):
        """Test creating Skill object with all required fields."""
        skill = Skill(
            name="test-skill",
            triggers=["test", "testing"],
            content="Skill content",
            path=Path("/tmp/test/SKILL.md"),
            version="2.0",
            priority="high"
        )
        
        assert skill.name == "test-skill"
        assert skill.triggers == ["test", "testing"]
        assert skill.content == "Skill content"
        assert skill.version == "2.0"
        assert skill.priority == "high"
    
    def test_default_values(self):
        """Test default values for optional fields."""
        skill = Skill(
            name="minimal-skill",
            triggers=["trigger"],
            content="",
            path=Path("/tmp/test/SKILL.md")
        )
        
        assert skill.version == "1.0"
        assert skill.priority == "normal"


# ============================================================================
# Test Scan Functionality
# ============================================================================

class TestScanFunctionality:
    """Test SkillRegistry.scan() method."""
    
    def test_scan_empty_directory(self, registry, tmp_skills_dir):
        """Test scan() empty directory returns empty list."""
        tmp_skills_dir.mkdir(exist_ok=True)
        skills = registry.scan()
        
        assert skills == []
        assert len(registry.list()) == 0
    
    def test_scan_directory_with_skills(self, registry, tmp_skills_dir):
        """Test scan() directory with N skills returns N Skill objects."""
        # Create 3 skills
        create_skill_file(tmp_skills_dir / "skill-a", {
            "name": "skill-a",
            "triggers": ["test"]
        }, "Content A")
        
        create_skill_file(tmp_skills_dir / "skill-b", {
            "name": "skill-b",
            "triggers": ["test"]
        }, "Content B")
        
        create_skill_file(tmp_skills_dir / "skill-c", {
            "name": "skill-c",
            "triggers": ["test"]
        }, "Content C")
        
        skills = registry.scan()
        
        assert len(skills) == 3
        assert len(registry.list()) == 3
        # Check names as a set since directory iteration order is not guaranteed
        skill_names = {s.name for s in skills}
        assert skill_names == {"skill-a", "skill-b", "skill-c"}
    
    def test_scan_nested_directories_not_recursive(self, registry, tmp_skills_dir):
        """Test scan() only scans immediate subdirectories, not recursive."""
        # Create skill in immediate subdirectory
        create_skill_file(tmp_skills_dir / "immediate", {
            "name": "immediate-skill",
            "triggers": ["test"]
        })
        
        # Create skill in nested subdirectory (should be ignored)
        nested_dir = tmp_skills_dir / "parent" / "child"
        create_skill_file(nested_dir, {
            "name": "nested-skill",
            "triggers": ["test"]
        })
        
        skills = registry.scan()
        
        assert len(skills) == 1
        assert skills[0].name == "immediate-skill"
    
    def test_scan_parses_yaml_frontmatter(self, registry, tmp_skills_dir):
        """Test scan() correctly parses YAML frontmatter."""
        create_skill_file(tmp_skills_dir / "test-skill", {
            "name": "test-driven-development",
            "version": "2.0",
            "triggers": ["寫測試", "pytest", "TDD"],
            "priority": "high"
        }, "This is the body content")
        
        skills = registry.scan()
        
        assert len(skills) == 1
        skill = skills[0]
        assert skill.name == "test-driven-development"
        assert skill.version == "2.0"
        assert skill.triggers == ["寫測試", "pytest", "TDD"]
        assert skill.priority == "high"
        assert skill.content == "This is the body content"
    
    def test_scan_extracts_markdown_body(self, registry, tmp_skills_dir):
        """Test scan() correctly extracts markdown body after frontmatter."""
        body_content = """# Skill Title

This is the skill description.

## Section

- List item 1
- List item 2
"""
        create_skill_file(tmp_skills_dir / "test-skill", {
            "name": "test-skill",
            "triggers": ["test"]
        }, body_content)
        
        skills = registry.scan()
        skill = skills[0]
        
        assert "# Skill Title" in skill.content
        assert "List item 1" in skill.content


# ============================================================================
# Test Get Method
# ============================================================================

class TestGetMethod:
    """Test SkillRegistry.get() method."""
    
    def test_get_existing_skill(self, registry, tmp_skills_dir):
        """Test get() existing skill returns correct Skill object."""
        create_skill_file(tmp_skills_dir / "test-skill", {
            "name": "test-driven-development",
            "triggers": ["test"]
        }, "TDD content")
        
        registry.scan()
        skill = registry.get("test-driven-development")
        
        assert skill is not None
        assert skill.name == "test-driven-development"
        assert skill.content == "TDD content"
    
    def test_get_non_existent_skill(self, registry, tmp_skills_dir):
        """Test get() non-existent skill returns None."""
        create_skill_file(tmp_skills_dir / "test-skill", {
            "name": "existing-skill",
            "triggers": ["test"]
        })
        
        registry.scan()
        skill = registry.get("non-existent-skill")
        
        assert skill is None
    
    def test_get_case_sensitive(self, registry, tmp_skills_dir):
        """Test get() is case-sensitive."""
        create_skill_file(tmp_skills_dir / "test-skill", {
            "name": "Test-Skill",
            "triggers": ["test"]
        })
        
        registry.scan()
        
        # Exact match works
        assert registry.get("Test-Skill") is not None
        
        # Different case returns None
        assert registry.get("test-skill") is None
        assert registry.get("TEST-SKILL") is None


# ============================================================================
# Test Find Method
# ============================================================================

class TestFindMethod:
    """Test SkillRegistry.find() method."""
    
    def test_find_by_exact_trigger_match(self, registry, tmp_skills_dir):
        """Test find() by exact trigger match."""
        create_skill_file(tmp_skills_dir / "pytest-skill", {
            "name": "pytest-skill",
            "triggers": ["pytest", "testing"]
        })
        
        registry.scan()
        skills = registry.find("pytest")
        
        assert len(skills) == 1
        assert skills[0].name == "pytest-skill"
    
    def test_find_by_partial_trigger_match(self, registry, tmp_skills_dir):
        """Test find() by partial trigger match."""
        create_skill_file(tmp_skills_dir / "test-skill", {
            "name": "test-skill",
            "triggers": ["寫測試", "測試驅動"]
        })
        
        registry.scan()
        skills = registry.find("測試")
        
        assert len(skills) == 1
        assert skills[0].name == "test-skill"
    
    def test_find_is_case_insensitive(self, registry, tmp_skills_dir):
        """Test find() is case-insensitive."""
        create_skill_file(tmp_skills_dir / "pytest-skill", {
            "name": "pytest-skill",
            "triggers": ["PyTest", "TESTING"]
        })
        
        registry.scan()
        
        # All cases should match
        skills_upper = registry.find("PYTEST")
        skills_lower = registry.find("pytest")
        skills_mixed = registry.find("PyTeSt")
        
        assert len(skills_upper) == 1
        assert len(skills_lower) == 1
        assert len(skills_mixed) == 1
        assert skills_upper[0].name == "pytest-skill"
    
    def test_find_no_matches_returns_empty_list(self, registry, tmp_skills_dir):
        """Test find() no matches returns empty list."""
        create_skill_file(tmp_skills_dir / "test-skill", {
            "name": "test-skill",
            "triggers": ["test", "pytest"]
        })
        
        registry.scan()
        skills = registry.find("unrelated-keyword")
        
        assert skills == []
        assert len(skills) == 0
    
    def test_find_multiple_matches(self, registry, tmp_skills_dir):
        """Test find() multiple matches returns all matching skills."""
        create_skill_file(tmp_skills_dir / "skill-a", {
            "name": "skill-a",
            "triggers": ["測試", "pytest"]
        })
        
        create_skill_file(tmp_skills_dir / "skill-b", {
            "name": "skill-b",
            "triggers": ["測試", "debug"]
        })
        
        create_skill_file(tmp_skills_dir / "skill-c", {
            "name": "skill-c",
            "triggers": ["linting"]
        })
        
        registry.scan()
        skills = registry.find("測試")
        
        assert len(skills) == 2
        skill_names = [s.name for s in skills]
        assert "skill-a" in skill_names
        assert "skill-b" in skill_names
        assert "skill-c" not in skill_names


# ============================================================================
# Test List Method
# ============================================================================

class TestListMethod:
    """Test SkillRegistry.list() method."""
    
    def test_list_empty_registry(self, registry):
        """Test list() empty registry returns empty list."""
        names = registry.list()
        
        assert names == []
        assert len(names) == 0
    
    def test_list_loaded_skills(self, registry, tmp_skills_dir):
        """Test list() loaded skills returns skill names only."""
        create_skill_file(tmp_skills_dir / "skill-a", {
            "name": "skill-a",
            "triggers": ["test"]
        })
        
        create_skill_file(tmp_skills_dir / "skill-b", {
            "name": "skill-b",
            "triggers": ["test"]
        })
        
        registry.scan()
        names = registry.list()
        
        assert len(names) == 2
        assert "skill-a" in names
        assert "skill-b" in names
        # Should return strings, not Skill objects
        assert all(isinstance(name, str) for name in names)


# ============================================================================
# Test Error Cases
# ============================================================================

class TestErrorCases:
    """Test error handling and validation."""
    
    def test_missing_name_field_raises_error(self, registry, tmp_skills_dir):
        """Test missing name field raises MalformedSkillError."""
        # Create skill without name field
        tmp_skills_dir.mkdir(exist_ok=True)
        skill_dir = tmp_skills_dir / "bad-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        
        frontmatter_yaml = yaml.dump({
            "triggers": ["test"]
        }, default_flow_style=False)
        content = f"---\n{frontmatter_yaml}---\nBody"
        
        skill_file.write_text(content, encoding='utf-8')
        
        with pytest.raises(MalformedSkillError, match="Missing required field: 'name'"):
            registry.scan()
    
    def test_missing_triggers_field_raises_error(self, registry, tmp_skills_dir):
        """Test missing triggers field raises MalformedSkillError."""
        create_skill_file(tmp_skills_dir / "bad-skill", {
            "name": "bad-skill",
            "version": "1.0"
            # Missing triggers
        })
        
        with pytest.raises(MalformedSkillError, match="Missing required field: 'triggers'"):
            registry.scan()
    
    def test_triggers_not_list_raises_error(self, registry, tmp_skills_dir):
        """Test triggers field must be a list."""
        tmp_skills_dir.mkdir(exist_ok=True)
        skill_dir = tmp_skills_dir / "bad-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        
        frontmatter_yaml = yaml.dump({
            "name": "bad-skill",
            "triggers": "not-a-list"  # Should be a list
        }, default_flow_style=False)
        content = f"---\n{frontmatter_yaml}---\nBody"
        
        skill_file.write_text(content, encoding='utf-8')
        
        with pytest.raises(MalformedSkillError, match="must be a list"):
            registry.scan()
    
    def test_invalid_yaml_syntax_raises_error(self, registry, tmp_skills_dir):
        """Test invalid YAML syntax raises MalformedSkillError."""
        tmp_skills_dir.mkdir(exist_ok=True)
        skill_dir = tmp_skills_dir / "bad-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        
        # Invalid YAML (missing colon)
        content = """---
name bad-skill
triggers:
  - test
---
Body"""
        
        skill_file.write_text(content, encoding='utf-8')
        
        with pytest.raises(MalformedSkillError, match="Invalid YAML syntax"):
            registry.scan()
    
    def test_missing_optional_fields_use_defaults(self, registry, tmp_skills_dir):
        """Test missing optional fields use default values."""
        create_skill_file(tmp_skills_dir / "minimal-skill", {
            "name": "minimal-skill",
            "triggers": ["test"]
            # Missing version and priority
        })
        
        skills = registry.scan()
        skill = skills[0]
        
        assert skill.version == "1.0"
        assert skill.priority == "normal"
    
    def test_empty_body_is_valid(self, registry, tmp_skills_dir):
        """Test SKILL.md with only frontmatter and no body is valid."""
        create_skill_file(tmp_skills_dir / "empty-body", {
            "name": "empty-body-skill",
            "triggers": ["test"]
        }, "")  # Empty body
        
        skills = registry.scan()
        
        assert len(skills) == 1
        assert skills[0].content == ""


# ============================================================================
# Test MalformedSkillError Exception
# ============================================================================

class TestMalformedSkillError:
    """Test MalformedSkillError exception behavior."""
    
    def test_inherits_from_exception(self):
        """Test MalformedSkillError can be caught as Exception."""
        try:
            raise MalformedSkillError("Test error")
        except Exception as e:
            assert isinstance(e, MalformedSkillError)
            assert str(e) == "Test error"
    
    def test_descriptive_error_message(self):
        """Test MalformedSkillError includes descriptive message."""
        error = MalformedSkillError("Missing field: name")
        assert "Missing field: name" in str(error)


# ============================================================================
# Integration Test - Complete Workflow
# ============================================================================

class TestIntegrationWorkflow:
    """Test complete workflow scenarios."""
    
    def test_full_workflow_scan_get_find_list(self, registry, tmp_skills_dir):
        """Test complete workflow: scan → get → find → list."""
        # Create multiple skills
        create_skill_file(tmp_skills_dir / "tdd", {
            "name": "test-driven-development",
            "version": "1.0",
            "triggers": ["寫測試", "pytest", "TDD"],
            "priority": "high"
        }, "TDD methodology")
        
        create_skill_file(tmp_skills_dir / "debugging", {
            "name": "systematic-debugging",
            "version": "2.0",
            "triggers": ["debug", "除錯", "fix bugs"],
            "priority": "normal"
        }, "Debug systematically")
        
        create_skill_file(tmp_skills_dir / "brainstorming", {
            "name": "brainstorming",
            "triggers": ["創意", "ideas", "brainstorm"]
        }, "Generate ideas")
        
        # Scan
        skills = registry.scan()
        assert len(skills) == 3
        
        # Get by exact name
        tdd_skill = registry.get("test-driven-development")
        assert tdd_skill is not None
        assert tdd_skill.version == "1.0"
        assert tdd_skill.priority == "high"
        
        # Find by keyword
        debugging_skills = registry.find("debug")
        assert len(debugging_skills) == 1
        assert debugging_skills[0].name == "systematic-debugging"
        
        # Find with partial match (Chinese)
        chinese_skills = registry.find("除錯")
        assert len(chinese_skills) == 1
        
        # List all
        all_names = registry.list()
        assert len(all_names) == 3
        assert "test-driven-development" in all_names
        assert "systematic-debugging" in all_names
        assert "brainstorming" in all_names
