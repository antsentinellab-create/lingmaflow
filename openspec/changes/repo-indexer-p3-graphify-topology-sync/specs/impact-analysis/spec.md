## ADDED Requirements

### Requirement: Impact Analysis via Topology Traversal
The system SHALL traverse the graph to find callers and callees of a given node for impact analysis.

#### Scenario: 1-hop neighborhood
- **WHEN** get_filtered_neighbors() is called with hop=1
- **THEN** direct callers and callees are returned (excluding high-degree nodes)

#### Scenario: 2-hop neighborhood
- **WHEN** get_filtered_neighbors() is called with hop=2
- **THEN** indirect dependencies are included in the result
