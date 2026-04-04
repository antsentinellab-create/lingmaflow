## ADDED Requirements

### Requirement: PROGRESS.md 格式規範

PROGRESS.md 應使用標準化的 Markdown 格式記錄每個 session 的決策記憶。

#### Scenario: Session 標題格式
- **WHEN** 建立新的 session 記錄
- **THEN** 使用 "## Session {ISO8601 timestamp}" 格式（例如：## Session 2026-04-03T14:30）

#### Scenario: Session 內容結構
- **WHEN** 記錄 session
- **THEN** 必須包含四個章節：完成、遺留、失敗記錄、下一步
- **THEN** 「完成」章節列出所有完成的 task IDs（例如：完成：task 3.1, 3.2）
- **THEN** 「遺留」章節描述中斷點的狀態（例如：遺留：task 3.3 開始到一半，auth module 尚未 import）
- **THEN** 「失敗記錄」章節列出嘗試過但失敗的方案（必填，例如：失敗記錄：嘗試用 httpx 直接 retry，發現和 existing middleware 衝突，改用 tenacity library）
- **THEN** 「下一步」章節提供具體指示（例如：下一步：從 task 3.3 繼續，注意 tenacity 版本需 >=8.2）

### Requirement: 失敗記錄必填規則

每個 session log 必須包含失敗記錄，即使為空也要明確標示。

#### Scenario: 有失敗記錄
- **WHEN** session 期間有嘗試過失敗的方案
- **THEN** 失敗記錄章節必須詳細描述失敗原因與替代方案

#### Scenario: 無失敗記錄
- **WHEN** session 期間所有嘗試都成功
- **THEN** 失敗記錄章節應寫「無」或保持空白但仍保留章節標題

### Requirement: PROGRESS.md 追加寫入模式

PROGRESS.md 應使用追加寫入模式，不修改歷史記錄。

#### Scenario: 追加新 session
- **WHEN** 呼叫 `log_session()`
- **THEN** 在檔案末尾追加新的 session 記錄
- **THEN** 不修改既有的 session 記錄

#### Scenario: 讀取最後一個 session
- **WHEN** 呼叫 `get_resume_point()`
- **THEN** 只解析最後一個 session 的內容
- **THEN** 忽略歷史 session 記錄
