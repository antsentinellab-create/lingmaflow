## 1. Setup and Structure

- [x] 1.1 Create `lingmaflow/core/agents_injector.py` module with imports
- [x] 1.2 Define `InjectionError(Exception)` custom exception class
- [x] 1.3 Import SkillRegistry from skill_registry module

## 2. Core Implementation - AgentsInjector Class

- [x] 2.1 Implement `__init__(self, registry: SkillRegistry, task_state_path: Path)` constructor
- [x] 2.2 Implement `generate() -> str` method to generate AGENTS.md content
- [x] 2.3 Add fixed sections content (每次啟動必做，Done Condition, 錯誤處置)
- [x] 2.4 Add dynamic skill list generation from registry.skills
- [x] 2.5 Implement `inject(output_path: Path) -> None` method to write content
- [x] 2.6 Implement `update(output_path: Path) -> None` method for updating existing files

## 3. Error Handling and Validation

- [x] 3.1 Add InjectionError raising when path is not writable
- [x] 3.2 Add directory creation logic in inject() if parent directories don't exist
- [x] 3.3 Handle UTF-8 encoding properly in file writing
- [x] 3.4 Validate output path before writing

## 4. Testing Infrastructure

- [x] 4.1 Create `tests/test_agents_injector.py` test file
- [x] 4.2 Set up pytest fixtures using tmp_path
- [x] 4.3 Create helper function to create mock SkillRegistry with skills
- [x] 4.4 Create sample valid AGENTS.md content for testing

## 5. Unit Tests - Generate Method

- [x] 5.1 Test generate() includes all skill names from registry
- [x] 5.2 Test generate() includes fixed sections text
- [x] 5.3 Test generate() with empty registry still works
- [x] 5.4 Test generate() formats skill list correctly
- [x] 5.5 Test generate() returns consistent content across multiple calls

## 6. Unit Tests - Inject and Update Methods

- [x] 6.1 Test inject() writes file with correct content
- [x] 6.2 Test inject() creates file if it doesn't exist
- [x] 6.3 Test inject() uses UTF-8 encoding
- [x] 6.4 Test update() overwrites existing file
- [x] 6.5 Test update() creates file if it doesn't exist
- [x] 6.6 Test injected file content matches generate() output

## 7. Unit Tests - Error Cases

- [x] 7.1 Test inject() to unwritable path raises InjectionError
- [x] 7.2 Test update() to unwritable path raises InjectionError
- [x] 7.3 Test inject() creates parent directories if needed
- [x] 7.4 Test inject() fails gracefully when parent directory cannot be created

## 8. Integration and Documentation

- [x] 8.1 Run full test suite (test_skill_registry.py + test_agents_injector.py) and ensure 100% pass rate
- [x] 8.2 Update `TASK_STATE.md` to STEP-04
- [x] 8.3 Add docstrings to all public methods and classes
- [x] 8.4 Verify done conditions: file exists, tests green, TASK_STATE.md updated
