## MODIFIED Requirements

### Requirement: Enhanced Query with Graph Context
The system SHALL support --with-graph CLI flag to enable topology expansion and return both vector results and hydrated graph context.

#### Scenario: CLI with graph flag
- **WHEN** enhanced_query.py is run with --with-graph argument
- **THEN** output includes vector_results and graph_context sections

#### Scenario: Configurable degree threshold
- **WHEN** --max-in-degree parameter is provided
- **THEN** nodes with in_degree exceeding the threshold are filtered out during expansion
