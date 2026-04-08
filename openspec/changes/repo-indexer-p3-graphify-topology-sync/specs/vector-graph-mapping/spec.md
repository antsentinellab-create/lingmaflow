## ADDED Requirements

### Requirement: Precision Line Number Mapping via Char Offset
The system SHALL track character offsets during code chunking to calculate exact line numbers, preventing "ghost mapping" errors caused by boilerplate code.

#### Scenario: Accurate line number for identical functions
- **WHEN** three identical `def hello(): pass` functions exist at different lines in a file
- **THEN** each chunk is mapped to the correct function node with accurate start_line and end_line

#### Scenario: Cross-platform newline handling
- **WHEN** processing files on Windows (CRLF) or Linux (LF)
- **THEN** the system normalizes all newlines to LF before calculating line numbers to ensure consistency

### Requirement: Many-to-Many Vector-Node Mapping
The system SHALL support many-to-many relationships between Chroma vector_ids and AST nodes based on line number intersection.

#### Scenario: Chunk spans multiple functions
- **WHEN** a chunk covers lines 30-70 and overlaps with func_A (lines 10-50) and func_B (lines 40-80)
- **THEN** the vector_id is linked to both func_A and func_B nodes

#### Scenario: Link vector to node by intersection
- **WHEN** link_vector_to_node() is called with chunk_start=30, chunk_end=70
- **THEN** all nodes with [start_line, end_line] intersecting [30, 70] are updated with the vector_id
