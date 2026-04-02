## 1. Setup and Structure

- [x] 1.1 Create `lingmaflow/core/skill_registry.py` module with imports
- [x] 1.2 Define `MalformedSkillError(Exception)` custom exception class
- [x] 1.3 Define `Skill` dataclass with all required fields
- [x] 1.4 Add default values for optional fields (version="1.0", priority="normal")

## 2. Core Implementation - SkillRegistry Class

- [x] 2.1 Implement `__init__(self, skills_dir: Path)` constructor
- [x] 2.2 Implement `_parse_skill_file(path: Path) -> Skill` private method
- [x] 2.3 Implement `_extract_frontmatter(content: str) -> dict` private method
- [x] 2.4 Implement `scan() -> list[Skill]` method to scan skills directory
- [x] 2.5 Implement validation logic for required fields (name, triggers)

## 3. Query Methods

- [x] 3.1 Implement `get(name: str) -> Optional[Skill]` method
- [x] 3.2 Implement `find(keyword: str) -> list[Skill]` method with case-insensitive matching
- [x] 3.3 Implement `list() -> list[str]` method to return skill names only
- [x] 3.4 Add proper handling for non-existent skills (return None/empty list)

## 4. Error Handling and Validation

- [x] 4.1 Add MalformedSkillError raising for missing name field
- [x] 4.2 Add MalformedSkillError raising for missing triggers field
- [x] 4.3 Add YAML parsing error handling with descriptive messages
- [x] 4.4 Handle optional fields with default values

## 5. Testing Infrastructure

- [x] 5.1 Create `tests/test_skill_registry.py` test file
- [x] 5.2 Set up pytest fixtures using tmp_path
- [x] 5.3 Create helper function to create temporary SKILL.md files
- [x] 5.4 Create sample valid and invalid skill files for testing

## 6. Unit Tests - Basic Functionality

- [x] 6.1 Test scan() empty directory returns empty list
- [x] 6.2 Test scan() directory with N skills returns N Skill objects
- [x] 6.3 Test get() existing skill returns correct Skill object
- [x] 6.4 Test get() non-existent skill returns None
- [x] 6.5 Test list() returns list of skill names only

## 7. Unit Tests - Find Method

- [x] 7.1 Test find() by exact trigger match
- [x] 7.2 Test find() by partial trigger match
- [x] 7.3 Test find() is case-insensitive
- [x] 7.4 Test find() no matches returns empty list
- [x] 7.5 Test find() multiple matches returns all matching skills

## 8. Unit Tests - Error Cases

- [x] 8.1 Test missing name field raises MalformedSkillError
- [x] 8.2 Test missing triggers field raises MalformedSkillError
- [x] 8.3 Test invalid YAML syntax raises MalformedSkillError
- [x] 8.4 Test missing optional fields use default values

## 9. Integration and Documentation

- [x] 9.1 Run full test suite and ensure 100% pass rate
- [x] 9.2 Update `TASK_STATE.md` with new format
- [x] 9.3 Add docstrings to all public methods and classes
- [x] 9.4 Verify done conditions: file exists, tests green, TASK_STATE.md updated
