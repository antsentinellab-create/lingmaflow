## ADDED Requirements

### Requirement: Systematic debugging skill content
系統 SHALL 提供完整的 systematic-debugging 技能說明，指導 agent 系統化地除錯

#### Scenario: Encounter bug or error
- **WHEN** 遇到錯誤或 bug 時
- **THEN** agent 應先重現問題，確認錯誤訊息

#### Scenario: Analyze error message
- **WHEN** 讀取錯誤訊息時
- **THEN** 完整閱讀並理解錯誤訊息，不跳過任何細節

#### Scenario: Fix and verify
- **WHEN** 修復問題後
- **THEN** 必須確認所有相關測試通過，確保問題已解決
