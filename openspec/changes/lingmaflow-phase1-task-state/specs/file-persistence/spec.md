## ADDED Requirements

### Requirement: TASK_STATE.md format
系統 SHALL 使用標準化的 Markdown 格式來持久化任務狀態

#### Scenario: Standard file structure
- **WHEN** save() 被呼叫
- **THEN** 產生包含所有必要欄位的 Markdown 檔案

#### Scenario: Field format
- **WHEN** 寫入欄位
- **THEN** 使用 `Key: Value` 格式，每行一個欄位

#### Scenario: Timestamp format
- **WHEN** 寫入最後更新時間
- **THEN** 使用 ISO8601 格式（YYYY-MM-DDTHH:MM:SS.ffffff）

#### Scenario: Unresolved issues list
- **WHEN** 存在多個未解決問題
- **THEN** 每個問題佔一行，使用 `- ` 前綴

### Requirement: File parsing
系統 SHALL 正確解析現有的 TASK_STATE.md 檔案

#### Scenario: Parse valid file
- **WHEN** load() 被呼叫且檔案存在
- **THEN** 返回包含所有欄位的 TaskState 物件

#### Scenario: Handle missing optional fields
- **WHEN** 檔案缺少 last_result 或 next_action
- **THEN** 使用空字串預設值

#### Scenario: Handle missing unresolved
- **WHEN** 檔案沒有未解決問題區塊
- **THEN** 使用空列表預設值

### Requirement: File writing
系統 SHALL 以可讀的格式寫入檔案

#### Scenario: Write complete state
- **WHEN** save() 被呼叫
- **THEN** 寫入所有欄位，包含時間戳記

#### Scenario: Preserve field order
- **WHEN** 寫入檔案
- **THEN** 按照標準順序：當前步驟、狀態、上一步結果、下一步動作、未解決問題、最後更新

#### Scenario: Encoding
- **WHEN** 寫入檔案
- **THEN** 使用 UTF-8 編碼
