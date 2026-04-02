## ADDED Requirements

### Requirement: Prepare 命令 - 任務上下文準備

Prepare 命令讀取 TASK_STATE.md 的當前步驟，自動匹配對應的 SKILL.md，生成 `.lingmaflow/current_task.md` 文件。

#### Scenario: 成功生成任務上下文
- **WHEN** 執行 `lingmaflow prepare` 且 TASK_STATE.md 存在
- **THEN** 生成 `.lingmaflow/current_task.md` 包含當前步驟、說明、Done Conditions 和參考技能

#### Scenario: 自動匹配技能
- **WHEN** TASK_STATE.md 的 `next_action` 包含 "測試" 或 "pytest"
- **THEN** 自動匹配 `test-driven-development` 技能並包含其內容

#### Scenario: 無匹配的skill
- **WHEN** 沒有技能的 triggers 匹配 `next_action`
- **THEN** 在輸出文件中顯示「無匹配的技能」但不失敗

#### Scenario: 缺少 TASK_STATE.md
- **WHEN** 執行 `lingmaflow prepare` 但 TASK_STATE.md 不存在
- **THEN** 顯示錯誤訊息並返回 exit_code 1

#### Scenario: 創建 .lingmaflow 目錄
- **WHEN** `.lingmaflow` 目錄不存在時執行 prepare
- **THEN** 自動創建該目錄後再生成文件
