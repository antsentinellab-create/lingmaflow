## ADDED Requirements

### Requirement: tasks.json schema

tasks.json 應使用標準化的 JSON schema 記錄每個 task 的狀態。

#### Scenario: Task 物件結構
- **WHEN** 建立 tasks.json
- **THEN** 每個 task 必須包含以下欄位：id (string), description (string), done (boolean), started_at (string|null), completed_at (string|null), notes (string)

#### Scenario: ID 格式規範
- **WHEN** 設定 task id
- **THEN** 使用 kebab-case 或數字編號（例如："1.1", "3.2", "phase-b-retry"）
- **THEN** ID 在整個 change 中必須唯一

#### Scenario: Timestamp 格式
- **WHEN** 記錄 started_at 或 completed_at
- **THEN** 使用 ISO 8601 格式（例如："2026-04-03T14:30:00Z"）

#### Scenario: Done flag 語義
- **WHEN** task 尚未開始
- **THEN** done=false, started_at=null, completed_at=null
- **WHEN** task 進行中
- **THEN** done=false, started_at="timestamp", completed_at=null
- **WHEN** task 已完成
- **THEN** done=true, completed_at="timestamp"

### Requirement: tasks.md → tasks.json 轉換邏輯

harness init 命令應能自動將現有 tasks.md 轉換為 tasks.json 格式。

#### Scenario: 解析 Markdown checkbox
- **WHEN** tasks.md 包含 `- [x] 1.1 建立目錄結構`
- **THEN** 轉換為 `{"id": "1.1", "description": "建立目錄結構", "done": true}`

#### Scenario: 處理未完成的 task
- **WHEN** tasks.md 包含 `- [ ] 1.2 定義 TaskStatus Enum`
- **THEN** 轉換為 `{"id": "1.2", "description": "定義 TaskStatus Enum", "done": false}`

#### Scenario: 保留備份檔案
- **WHEN** 轉換完成後
- **THEN** 建立 tasks.md.bak 作為備份
- **THEN** 保留原始 tasks.md 不刪除

### Requirement: tasks.json 修改限制

為了保持穩定性，tasks.json 的修改應受到嚴格限制。

#### Scenario: 允許的修改
- **WHEN** agent 執行 harness done 命令
- **THEN** 只允許修改 done, started_at, completed_at, notes 欄位
- **THEN** 不允許修改 id 和 description 欄位

#### Scenario: 禁止新增或删除 task
- **WHEN** agent 嘗試修改 tasks.json
- **THEN** 禁止新增任何 task 條目
- **THEN** 禁止刪除任何 task 條目
- **THEN** 只能透過 harness init 從 tasks.md 轉換時建立初始清單

### Requirement: tasks.json 驗證規則

每次讀寫 tasks.json 時應驗證其格式正確性。

#### Scenario: Schema 驗證
- **WHEN** 讀取或寫入 tasks.json
- **THEN** 驗證所有必要欄位存在（id, description, done）
- **THEN** 驗證 done 為 boolean 類型
- **THEN** 驗證 id 和 description 為 string 類型

#### Scenario: 唯一性驗證
- **WHEN** 初始化或修改 tasks.json
- **THEN** 驗證所有 task IDs 唯一
- **THEN** 如果發現重複 ID，拋出錯誤並停止
