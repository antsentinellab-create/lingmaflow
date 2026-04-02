## 1. ConditionChecker Core Implementation

- [x] 1.1 Create `lingmaflow/core/condition_checker.py` module structure
- [x] 1.2 Implement `ConditionResult` dataclass with passed, condition, message fields
- [x] 1.3 Implement `UnknownConditionTypeError` exception class
- [x] 1.4 Implement `check_file(path)` method using os.path.exists()
- [x] 1.5 Implement `check_pytest(path)` method using subprocess.run()
- [x] 1.6 Implement `check_func(module_path)` method using importlib
- [x] 1.7 Implement `parse_condition(condition_str)` helper method
- [x] 1.8 Implement `check_all(conditions)` method to check all conditions
- [x] 1.9 Implement `all_passed(conditions)` convenience method

## 2. TaskStateManager Extension

- [x] 2.1 Add `get_conditions()` method to parse ## Done Conditions block
- [x] 2.2 Add regex pattern to extract checkbox items from markdown
- [x] 2.3 Add `mark_condition_done(condition)` method to update checkbox
- [x] 2.4 Add `all_conditions_done()` method to check if all are [x]
- [x] 2.5 Ensure backward compatibility (no Done Conditions block = empty list)
- [x] 2.6 Update save() to preserve Done Conditions block format

## 3. CLI Prepare Command

- [x] 3.1 Add `@cli.command('prepare')` decorator
- [x] 3.2 Implement reading TASK_STATE.md current_step and next_action
- [x] 3.3 Implement skill matching logic based on triggers
- [x] 3.4 Create `.lingmaflow/` directory if not exists
- [x] 3.5 Generate `.lingmaflow/current_task.md` with proper format
- [x] 3.6 Display success message with file path
- [x] 3.7 Handle missing TASK_STATE.md with error message

## 4. CLI Verify Command

- [x] 4.1 Add `@cli.command('verify')` decorator
- [x] 4.2 Implement reading Done Conditions from TASK_STATE.md
- [x] 4.3 Instantiate ConditionChecker and call check_all()
- [x] 4.4 Format output with ✅/❌ emojis for each condition
- [x] 4.5 Return exit_code 0 if all pass, 1 if any fail
- [x] 4.6 Handle missing Done Conditions block gracefully

## 5. CLI Checkpoint Command

- [x] 5.1 Add `@cli.command('checkpoint')` decorator
- [x] 5.2 Add `next_step` argument and `--commit` flag
- [x] 5.3 Call verify logic first before proceeding
- [x] 5.4 If verify passes, call advance() method
- [x] 5.5 If --commit flag is set, execute git add and git commit
- [x] 5.6 Handle git failures gracefully (warn but continue)
- [x] 5.7 Display appropriate success/failure messages

## 6. Testing - ConditionChecker

- [x] 6.1 Write test for check_file with existing file
- [x] 6.2 Write test for check_file with non-existing file
- [x] 6.3 Write test for check_pytest with passing tests
- [x] 6.4 Write test for check_pytest with failing tests
- [x] 6.5 Write test for check_func with existing module.class
- [x] 6.6 Write test for check_func with non-existing module
- [x] 6.7 Write test for UnknownConditionTypeError
- [x] 6.8 Write test for check_all with mixed results
- [x] 6.9 Write integration test for complete workflow

## 7. Testing - TaskStateManager Extension

- [x] 7.1 Write test for get_conditions() parsing
- [x] 7.2 Write test for get_conditions() with no block
- [x] 7.3 Write test for mark_condition_done() successful update
- [x] 7.4 Write test for mark_condition_done() with invalid condition
- [x] 7.5 Write test for all_conditions_done() all checked
- [x] 7.6 Write test for all_conditions_done() partially checked
- [x] 7.7 Write test for all_conditions_done() with empty block

## 8. Testing - CLI Commands

- [x] 8.1 Write test for prepare command success case
- [x] 8.2 Write test for prepare command missing TASK_STATE.md
- [x] 8.3 Write test for prepare command skill matching
- [x] 8.4 Write test for verify command all pass (exit_code 0)
- [x] 8.5 Write test for verify command some fail (exit_code 1)
- [x] 8.6 Write test for verify command no Done Conditions
- [x] 8.7 Write test for checkpoint command verify pass and advance
- [x] 8.8 Write test for checkpoint command verify fail no advance
- [x] 8.9 Write test for checkpoint command with --commit flag
- [x] 8.10 Write test for checkpoint command missing next_step argument

## 9. Integration Testing and Validation

- [x] 9.1 Run full pytest suite and ensure all tests pass
- [x] 9.2 Test lingmaflow prepare in real scenario
- [x] 9.3 Test lingmaflow verify with sample Done Conditions
- [x] 9.4 Test lingmaflow checkpoint end-to-end
- [x] 9.5 Verify backward compatibility with old TASK_STATE.md
- [ ] 9.6 Document usage examples in README.md

## 10. Documentation and Archive

- [ ] 10.1 Update TASK_STATE.md to PHASE-4-done
- [ ] 10.2 Verify all done conditions for this phase
- [ ] 10.3 Prepare for openspec-archive-change
