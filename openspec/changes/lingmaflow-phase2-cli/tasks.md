## 1. Setup and Structure

- [x] 1.1 Update `lingmaflow/cli/lingmaflow.py` with Click imports
- [x] 1.2 Create main CLI group with @click.group()
- [x] 1.3 Add version option (--version)
- [x] 1.4 Add help text for main command

## 2. Task Management Commands

- [x] 2.1 Implement `status` command to display TASK_STATE.md content
- [x] 2.2 Implement `advance` command to advance to next step
- [x] 2.3 Implement `block` command to mark task as blocked
- [x] 2.4 Implement `resolve` command to resolve issues
- [x] 2.5 Add --path/-p option to all task commands

## 3. Skill Query Commands

- [x] 3.1 Create skill subcommand group (@cli.group())
- [x] 3.2 Implement `skill find <keyword>` command
- [x] 3.3 Implement `skill list` command
- [x] 3.4 Add formatting for skill results

## 4. Agents Generation Command

- [x] 4.1 Create agents subcommand group (@cli.group())
- [x] 4.2 Implement `agents generate` command
- [x] 4.3 Add --output/-o option for custom output path
- [x] 4.4 Add overwrite confirmation or --force option

## 5. Project Initialization Command

- [x] 5.1 Implement `init` command
- [x] 5.2 Create default directory structure (skills/, .lingma/)
- [x] 5.3 Generate initial TASK_STATE.md
- [x] 5.4 Generate initial AGENTS.md
- [x] 5.5 Add safety check for existing files

## 6. Error Handling and User Experience

- [x] 6.1 Add proper error messages using click.echo(err=True)
- [x] 6.2 Handle file not found errors gracefully
- [x] 6.3 Add success messages after operations
- [x] 6.4 Return correct exit codes (0 for success, 1 for error)

## 7. Testing Infrastructure

- [x] 7.1 Create `tests/test_cli.py` test file
- [x] 7.2 Set up Click CliRunner fixture
- [x] 7.3 Create temporary directory fixtures
- [x] 7.4 Create helper functions to initialize test projects

## 8. Unit Tests - Task Management Commands

- [x] 8.1 Test status command displays correct information
- [x] 8.2 Test status with custom path
- [x] 8.3 Test advance command updates TASK_STATE.md
- [x] 8.4 Test block command adds unresolved issue
- [x] 8.5 Test resolve command removes issue
- [x] 8.6 Test commands handle missing files gracefully

## 9. Unit Tests - Skill Query Commands

- [x] 9.1 Test skill find with matching keyword
- [x] 9.2 Test skill find with no matches
- [x] 9.3 Test skill find is case-insensitive
- [x] 9.4 Test skill list shows all skills
- [x] 9.5 Test skill list with empty registry

## 10. Unit Tests - Agents and Init Commands

- [x] 10.1 Test agents generate creates AGENTS.md
- [x] 10.2 Test agents generate with custom output path
- [x] 10.3 Test agents generate includes all skills
- [x] 10.4 Test init creates directory structure
- [x] 10.5 Test init generates correct TASK_STATE.md
- [x] 10.6 Test init handles existing files safely

## 11. Integration and Packaging

- [x] 11.1 Update pyproject.toml with entry point
- [x] 11.2 Run full test suite and ensure 100% pass rate
- [x] 11.3 Update `TASK_STATE.md` to PHASE-3
- [x] 11.4 Verify done conditions: file exists, tests green, TASK_STATE.md updated
