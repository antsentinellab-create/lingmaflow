## ADDED Requirements

### Requirement: Harness init writes active_change file
When `harness init` is executed, the system SHALL write the change name to `.lingmaflow/active_change` file. The file content MUST be a single line containing only the change name.

#### Scenario: First time harness init
- **WHEN** user runs `lingmaflow harness init --change my-feature`
- **THEN** system creates `.lingmaflow/active_change` with content `my-feature`

#### Scenario: Overwrite existing active_change
- **WHEN** `.lingmaflow/active_change` already contains `old-change` and user runs `lingmaflow harness init --change new-change`
- **THEN** system overwrites `.lingmaflow/active_change` with content `new-change`

### Requirement: Status command reads active_change and displays harness block
When `lingmaflow status` is executed and `.lingmaflow/active_change` exists, the system SHALL read the change name and display a harness status block after the PHASE status.

#### Scenario: Active change exists and displays harness block
- **WHEN** `.lingmaflow/active_change` contains `ai-factory-phase-b` and user runs `lingmaflow status`
- **THEN** system displays harness block with change name, progress percentage, current task ID, and last session time

#### Scenario: No active_change file (backward compatibility)
- **WHEN** `.lingmaflow/active_change` does not exist and user runs `lingmaflow status`
- **THEN** system displays only PHASE status without harness block (no error)

#### Scenario: Active change with no tasks completed
- **WHEN** `.lingmaflow/active_change` contains a change with 0 completed tasks out of 10 total
- **THEN** system displays `Progress: 0/10 tasks (0%)` in harness block

#### Scenario: Active change with all tasks completed
- **WHEN** `.lingmaflow/active_change` contains a change with 23 completed tasks out of 23 total
- **THEN** system displays `Progress: 23/23 tasks (100%)` in harness block

### Requirement: Harness block format consistency
The harness block displayed by `lingmaflow status` SHALL follow a consistent format with visual separators and standardized field labels.

#### Scenario: Standard harness block format
- **WHEN** harness block is displayed
- **THEN** output follows this exact format:
  ```
  ── Harness ──────────────────────
  Change: <change-name>
  Progress: <completed>/<total> tasks (<percentage>%)
  Current task: <task-id>
  Last session: <timestamp or "None">
  ─────────────────────────────────
  ```

#### Scenario: Last session timestamp formatting
- **WHEN** last session time is available from HarnessManager
- **THEN** timestamp is formatted as `YYYY-MM-DD HH:MM` (e.g., `2026-04-03 14:30`)

#### Scenario: No last session recorded
- **WHEN** no session log exists for the change
- **THEN** system displays `Last session: None`
