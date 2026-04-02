## ADDED Requirements

### Requirement: CLI status command
系統 SHALL 提供 `lingmaflow status` 命令來顯示當前任務狀態

#### Scenario: Display current task status
- **WHEN** 用戶執行 `lingmaflow status`
- **THEN** 顯示當前步驟、狀態、上一步結果、下一步動作和未解決問題

#### Scenario: Status with default path
- **WHEN** 用戶執行 `lingmaflow status` 且未指定路徑
- **THEN** 讀取當前工作目錄的 TASK_STATE.md

#### Scenario: Status with custom path
- **WHEN** 用戶執行 `lingmaflow status --path /some/dir`
- **THEN** 讀取指定路徑的 TASK_STATE.md

### Requirement: CLI advance command
系統 SHALL 提供 `lingmaflow advance` 命令來推進任務到下一步

#### Scenario: Advance to next step
- **WHEN** 用戶執行 `lingmaflow advance STEP-03 "Implementation complete"`
- **THEN** 更新 TASK_STATE.md，將狀態改為 in_progress，記錄上一步結果

#### Scenario: Advance requires result description
- **WHEN** 用戶執行 `lingmaflow advance` 但未提供結果描述
- **THEN** 使用預設訊息或提示用戶輸入

### Requirement: CLI block command
系統 SHALL 提供 `lingmaflow block` 命令來標記任務為 blocked

#### Scenario: Block with issue description
- **WHEN** 用戶執行 `lingmaflow block "Database connection timeout"`
- **THEN** 將狀態改為 blocked，並將問題加入 unresolved issues

#### Scenario: Multiple blocks add multiple issues
- **WHEN** 用戶多次執行 `lingmaflow block`
- **THEN** 所有問題都加入 unresolved issues 列表

### Requirement: CLI resolve command
系統 SHALL 提供 `lingmaflow resolve` 命令來解決未解決的問題

#### Scenario: Resolve existing issue
- **WHEN** 用戶執行 `lingmaflow resolve 1`（問題編號）
- **THEN** 從 unresolved issues 中移除該問題

#### Scenario: Resolve non-existent issue
- **WHEN** 用戶執行 `lingmaflow resolve 999` 但不存在該編號的問題
- **THEN** 顯示錯誤訊息，不修改檔案
