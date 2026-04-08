## ADDED Requirements

### Requirement: Graph Persistence with Atomic Write
The system SHALL persist the code topology graph to JSON format using atomic write operations to prevent data corruption during concurrent access or system crashes.

#### Scenario: Successful graph save
- **WHEN** GraphManager.save() is called
- **THEN** system writes to a temporary file first, then atomically replaces the target file using os.replace()

#### Scenario: Concurrent write protection
- **WHEN** two processes attempt to save the graph simultaneously
- **THEN** the second process waits for the file lock to be released before proceeding

#### Scenario: Stale lock detection
- **WHEN** a .lock file exists for more than 5 minutes and the owning PID is no longer running
- **THEN** the system automatically removes the stale lock and proceeds with the write operation

### Requirement: JSON Format Serialization
The system SHALL use NetworkX node_link_data format for graph serialization to support complex Python data structures (List, Dict) as node attributes.

#### Scenario: Serialize graph with vector_ids list
- **WHEN** graph contains nodes with vector_ids attribute (Python List)
- **THEN** the JSON file correctly preserves the list structure without type conversion errors

#### Scenario: Load and rebuild index
- **WHEN** graph is loaded from JSON file
- **THEN** the system rebuilds the vector_to_nodes reverse index from node attributes

### Requirement: Strict Type Assertion for Node IDs
The system SHALL enforce that all node_id values are strings to prevent type drift during JSON serialization.

#### Scenario: Add node with string ID
- **WHEN** add_node() is called with a string node_id
- **THEN** the node is successfully added to the graph

#### Scenario: Reject non-string node ID
- **WHEN** add_node() is called with a non-string node_id (e.g., tuple, int)
- **THEN** the system raises TypeError with a descriptive error message
