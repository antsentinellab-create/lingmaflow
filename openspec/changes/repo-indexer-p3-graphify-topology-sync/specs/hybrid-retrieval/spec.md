## ADDED Requirements

### Requirement: Hybrid Retrieval with Graph Expansion
The system SHALL combine vector search with graph topology expansion when --with-graph flag is enabled.

#### Scenario: Vector-only search (default)
- **WHEN** query is executed without --with-graph flag
- **THEN** only Chroma vector results are returned

#### Scenario: Hybrid search with graph
- **WHEN** query is executed with --with-graph flag
- **THEN** system returns both vector_results and graph_context from 1-hop neighbors

### Requirement: Degree Filtering for Context Control
The system SHALL filter out high-degree nodes (in_degree > threshold) during graph expansion to prevent context window explosion.

#### Scenario: Skip utility functions
- **WHEN** neighbor node has in_degree > 10 (e.g., logger.info, utils.helper)
- **THEN** the node is excluded from graph_context expansion
