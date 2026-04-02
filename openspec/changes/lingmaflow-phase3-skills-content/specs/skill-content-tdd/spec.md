## ADDED Requirements

### Requirement: Test-driven development skill content
系統 SHALL 提供完整的 TDD 技能說明，指導 agent 遵循 RED-GREEN-REFACTOR 循環

#### Scenario: Start new feature
- **WHEN** 開始實作新功能時
- **THEN** agent 應先寫失敗的測試（RED），再寫最少程式碼讓測試通過（GREEN），最後重構（REFACTOR）

#### Scenario: Write tests first
- **WHEN** 實作任何功能前
- **THEN** 必須先寫測試，禁止先寫程式碼再補測試

#### Scenario: Refactor after tests pass
- **WHEN** 所有測試都通過後
- **THEN** 進行重構，改善程式碼品質但不改變行為
