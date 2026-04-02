## ADDED Requirements

### Requirement: Inject AGENTS.md to file
AgentsInjector SHALL 提供 inject() 方法來將生成的內容寫入指定路徑

#### Scenario: Inject to new file
- **WHEN** 呼叫 inject(output_path) 且檔案不存在
- **THEN** 建立新檔案並寫入 generate() 的內容

#### Scenario: Inject preserves content
- **WHEN** 呼叫 inject(output_path)
- **THEN** 寫入的檔案內容與 generate() 返回的字串完全一致

#### Scenario: Inject uses UTF-8 encoding
- **WHEN** 呼叫 inject(output_path)
- **THEN** 檔案應使用 UTF-8 編碼寫入

### Requirement: Update existing AGENTS.md
AgentsInjector SHALL 提供 update() 方法來更新已存在的檔案

#### Scenario: Update overwrites existing file
- **WHEN** 呼叫 update(output_path) 且檔案已存在
- **THEN** 覆蓋原有內容，寫入新的 generate() 結果

#### Scenario: Update creates if not exists
- **WHEN** 呼叫 update(output_path) 且檔案不存在
- **THEN** 建立新檔案（行為與 inject() 相同）

### Requirement: Handle write errors
inject() 和 update() SHALL 在無法寫入時拋出 InjectionError

#### Scenario: Unwritable path raises error
- **WHEN** 呼叫 inject(output_path) 但路徑無法寫入（如權限不足）
- **THEN** 拋出 InjectionError 並包含描述性訊息

#### Scenario: Parent directory does not exist
- **WHEN** 呼叫 inject(output_path) 但 parent directory 不存在且無法建立
- **THEN** 拋出 InjectionError
