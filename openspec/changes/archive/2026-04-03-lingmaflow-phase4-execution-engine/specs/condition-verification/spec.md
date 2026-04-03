## ADDED Requirements

### Requirement: Verify 命令 - 條件驗證

Verify 命令讀取 TASK_STATE.md 的 Done Conditions，使用 ConditionChecker 逐一驗證，並顯示每個條件的通過狀態（✅/❌）。

#### Scenario: 所有條件通過
- **WHEN** 執行 `lingmaflow verify` 且所有 Done Conditions 通過
- **THEN** 顯示每個條件的 ✅ 圖示，退出碼為 0

#### Scenario: 部分條件失敗
- **WHEN** 執行 `lingmaflow verify` 且有條件失敗
- **THEN** 顯示所有條件的結果（包含 ✅ 和 ❌），退出碼為 1

#### Scenario: 沒有 Done Conditions 區塊
- **WHEN** 執行 `lingmaflow verify` 但 TASK_STATE.md 沒有 Done Conditions 區塊
- **THEN** 顯示「無 Done Conditions」訊息，退出碼為 0

#### Scenario: 空的 Done Conditions
- **WHEN** Done Conditions 區塊存在但沒有任何條件
- **THEN** 視為所有條件通過，退出碼為 0

#### Scenario: 輸出格式正確
- **WHEN** 執行 verify 命令
- **THEN** 每個條件輸出一行，格式為 `✅ condition` 或 `❌ condition`
