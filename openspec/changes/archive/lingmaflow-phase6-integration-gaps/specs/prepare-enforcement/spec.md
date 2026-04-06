## ADDED Requirements

### Requirement: Checkpoint 完成後自動執行 Prepare
當 `lingmaflow checkpoint` 指令成功更新 TASK_STATE.md 後,系統 SHALL 自動呼叫 `lingmaflow prepare` 指令,確保 current_task.md 保持最新狀態。

#### Scenario: Checkpoint 後自動生成 current_task.md
- **WHEN** agent 執行 `lingmaflow checkpoint` 且 TASK_STATE.md 更新成功
- **THEN** 系統自動執行 `lingmaflow prepare`
- **AND** `.lingmaflow/current_task.md` 被更新為當前 Phase 的資訊
- **AND** 輸出顯示「🔄 自動執行 prepare...」提示使用者

#### Scenario: Prepare 失敗不影響 Checkpoint
- **WHEN** checkpoint 成功但自動執行的 prepare 失敗
- **THEN** checkpoint 仍標示為成功
- **AND** 系統顯示警告訊息「⚠️ Prepare 執行失敗,請手動執行 lingmaflow prepare」
- **AND** 不阻礙後續工作流程

### Requirement: AGENTS.md 強制讀取 current_task.md
AGENTS.md SHALL 在「每次啟動強制執行」章節中加入讀取 `.lingmaflow/current_task.md` 的步驟,確保 agent 開始工作前獲得完整上下文。

#### Scenario: Agent 啟動時讀取 current_task.md
- **WHEN** agent 開始新的 session
- **THEN** AGENTS.md 要求 agent 執行 `cat .lingmaflow/current_task.md` (若檔案存在)
- **AND** agent 從中獲取上一步結果、Done Conditions、匹配的 Skill 參考

#### Scenario: current_task.md 不存在時跳過
- **WHEN** agent 執行 `cat .lingmaflow/current_task.md` 但檔案不存在
- **THEN** agent 記錄警告但繼續執行其他步驟
- **AND** 不中斷工作流程

### Requirement: Prepare 指令輸出標準化格式
`lingmaflow prepare` 指令 SHALL 生成結構化的 current_task.md,包含 Phase 資訊、Done Conditions、Skill 參考等關鍵內容。

#### Scenario: Generate current_task.md with structured content
- **WHEN** agent 執行 `lingmaflow prepare`
- **THEN** 系統讀取 TASK_STATE.md 獲取當前 Phase
- **AND** 寫入 `.lingmaflow/current_task.md` 包含:
  - 當前 Phase ID 與描述
  - Last Result (上一步結果)
  - Done Conditions 清單
  - 匹配的 Skill 參考 (若有)
