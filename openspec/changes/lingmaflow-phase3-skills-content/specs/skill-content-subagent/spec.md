## ADDED Requirements

### Requirement: Subagent-driven skill content
系統 SHALL 提供完整的 subagent-driven 技能說明，指導 agent 如何執行計劃和管理進度

#### Scenario: Start task execution
- **WHEN** agent 開始執行任務時
- **THEN** 必須先讀取 TASK_STATE.md，了解當前步驟和狀態

#### Scenario: Complete individual task
- **WHEN** 完成每個 task 後
- **THEN** 更新 TASK_STATE.md，記錄上一步結果和下一步動作

#### Scenario: Check done conditions
- **WHEN** 準備推進到下一步時
- **THEN** 必須確認所有 done conditions 都已達成

#### Scenario: Encounter blocker
- **WHEN** 遇到無法解決的問題時
- **THEN** 標記為 BLOCKED，停止等待並記錄未解決問題
