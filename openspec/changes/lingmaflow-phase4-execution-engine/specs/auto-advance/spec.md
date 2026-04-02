## ADDED Requirements

### Requirement: Checkpoint 命令 - 自動推進

Checkpoint 命令先執行 verify，如果所有條件通過則自動推進到下一步，支援可選的 git commit 功能。

#### Scenario: 驗證通過並自動推進
- **WHEN** 執行 `lingmaflow checkpoint STEP-XX "Result description"` 且所有 Done Conditions 通過
- **THEN** 自動調用 advance 方法推進到下一步，顯示成功訊息

#### Scenario: 驗證失敗停止推進
- **WHEN** 執行 checkpoint 但有 Done Conditions 失敗
- **THEN** 顯示失敗的條件，不推進任務，退出碼為 1

#### Scenario: 缺少 next_step 參數
- **WHEN** 執行 checkpoint 但未提供 next_step 參數
- **THEN** 顯示錯誤訊息「需要提供下一步驟名稱」，退出碼為 1

#### Scenario: 使用 --commit 旗標
- **WHEN** 執行 `lingmaflow checkpoint STEP-XX "Result" --commit` 且驗證通過
- **THEN** 執行 git add . 和 git commit -m "Complete current step" 後推進

#### Scenario: Git commit 失敗
- **WHEN** 使用 --commit 但 git commit 失敗（例如有未暫存的變更）
- **THEN** 顯示警告訊息但仍舊推進任務（不阻斷流程）
