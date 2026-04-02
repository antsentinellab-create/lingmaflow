## ADDED Requirements

### Requirement: Brainstorming skill content
系統 SHALL 提供完整的 brainstorming 技能說明，指導 agent 在實作前釐清需求

#### Scenario: Agent needs to clarify requirements
- **WHEN** 用戶提出模糊的需求或規格
- **THEN** agent 應使用 brainstorming skill，透過提問引導用戶說清楚目標

#### Scenario: Multiple design options exist
- **WHEN** 有多個可行的設計方案
- **THEN** agent 應列出所有選項並說明各自的優缺點和取捨

#### Scenario: Ready to implement
- **WHEN** 需求已釐清且設計已確定
- **THEN** agent 應確保已產出 proposal.md 後才開始實作
