## MODIFIED Requirements

### Requirement: AST-First Dual-Dimension Index Construction
The system SHALL build the graph structure from AST parsing BEFORE chunking and embedding, then bind Chroma UUIDs to AST nodes via line number intersection.

#### Scenario: Build order enforcement
- **WHEN** build_index.py is executed
- **THEN** Phase 1 parses AST and creates pure graph, Phase 2 chunks and embeds, Phase 3 binds vector_ids

#### Scenario: Relative path storage
- **WHEN** adding nodes to the graph
- **THEN** file_path attributes are stored as relative paths from repo root, not absolute paths
