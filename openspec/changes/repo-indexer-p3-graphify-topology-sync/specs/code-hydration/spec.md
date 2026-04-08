## ADDED Requirements

### Requirement: Code Hydration from Filesystem
The system SHALL read actual source code snippets from the filesystem for graph nodes to provide meaningful context to LLMs.

#### Scenario: Hydrate function code
- **WHEN** _hydrate_code() is called with a function node_id
- **THEN** the system reads the file and returns the exact lines from start_line to end_line

#### Scenario: Relative path resolution
- **WHEN** hydrating code in a different working directory
- **THEN** the system dynamically resolves the full path using repo_root + relative_path
