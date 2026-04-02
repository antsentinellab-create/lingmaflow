## 1. Setup and Structure

- [x] 1.1 Create `lingmaflow/core/task_state.py` module structure with imports
- [x] 1.2 Define `TaskStatus` Enum with NOT_STARTED, IN_PROGRESS, BLOCKED, DONE
- [x] 1.3 Define custom exceptions: `InvalidStateError`, `MalformedStateFileError`
- [x] 1.4 Define `TaskState` dataclass with all required fields

## 2. Core Implementation - TaskStateManager

- [x] 2.1 Implement `__init__(path: Path)` constructor
- [x] 2.2 Implement `_parse_file(content: str) -> dict` private method for file parsing
- [x] 2.3 Implement `_format_state(state: TaskState) -> str` private method for file writing
- [x] 2.4 Implement `load() -> TaskState` method (create initial state if file doesn't exist)
- [x] 2.5 Implement `save(state: TaskState)` method (write to TASK_STATE.md)

## 3. State Transition Methods

- [x] 3.1 Implement `advance(next_step: str, result: str)` method with validation
- [x] 3.2 Implement `block(reason: str)` method with validation
- [x] 3.3 Implement `resolve(reason: str)` method with validation
- [x] 3.4 Implement `complete()` method with validation
- [x] 3.5 Implement helper methods: `is_blocked() -> bool`, `is_done() -> bool`

## 4. Error Handling and Validation

- [x] 4.1 Add state transition validation in all transition methods
- [x] 4.2 Add malformed file detection in _parse_file with detailed error messages
- [x] 4.3 Add proper exception raising with descriptive error messages

## 5. Testing Infrastructure

- [x] 5.1 Create `tests/test_task_state.py` test file
- [x] 5.2 Set up pytest fixtures using tmp_path
- [x] 5.3 Create helper functions for common test setups

## 6. Unit Tests - Basic Functionality

- [x] 6.1 Test `load()` non-existent file returns status == NOT_STARTED
- [x] 6.2 Test `load()` existing file parses correctly
- [x] 6.3 Test `save()` writes correct format with all fields
- [x] 6.4 Test timestamp format is ISO8601

## 7. Unit Tests - State Transitions

- [x] 7.1 Test `advance()` updates step, status stays IN_PROGRESS
- [x] 7.2 Test `block()` changes status to BLOCKED, adds to unresolved
- [x] 7.3 Test `resolve()` changes status to IN_PROGRESS, removes from unresolved
- [x] 7.4 Test `complete()` changes status to DONE
- [x] 7.5 Test `advance()` from DONE raises InvalidStateError
- [x] 7.6 Test `block()` from DONE raises InvalidStateError
- [x] 7.7 Test `complete()` from DONE raises InvalidStateError

## 8. Unit Tests - Error Cases

- [x] 8.1 Test malformed file missing required fields raises MalformedStateFileError
- [x] 8.2 Test invalid status value raises MalformedStateFileError
- [x] 8.3 Test multiple blocks add multiple unresolved issues
- [x] 8.4 Test resolve with non-existent reason handles gracefully

## 9. Integration and Documentation

- [x] 9.1 Run full test suite and ensure 100% pass rate
- [x] 9.2 Update `TASK_STATE.md` in project root with new format
- [x] 9.3 Add docstrings to all public methods
- [x] 9.4 Verify done conditions: file exists, tests green, TASK_STATE.md updated
