## ADDED Requirements

### Requirement: CLI skill find command
系統 SHALL 提供 `lingmaflow skill find <keyword>` 命令來查詢技能

#### Scenario: Find skills by keyword
- **WHEN** 用戶執行 `lingmaflow skill find pytest`
- **THEN** 顯示所有 triggers 包含 "pytest" 的技能

#### Scenario: Find with no matches
- **WHEN** 用戶執行 `lingmaflow skill find nonexistent` 但沒有匹配的技能
- **THEN** 顯示 "No skills found" 訊息

#### Scenario: Find is case-insensitive
- **WHEN** 用戶執行 `lingmaflow skill find PYTEST`
- **THEN** 仍然匹配到包含 "pytest" 的技能

### Requirement: CLI skill list command
系統 SHALL 提供 `lingmaflow skill list` 命令來列出所有技能

#### Scenario: List all skills
- **WHEN** 用戶執行 `lingmaflow skill list`
- **THEN** 顯示所有已註冊技能的名稱

#### Scenario: List empty registry
- **WHEN** 用戶執行 `lingmaflow skill list` 但 skills 目錄為空
- **THEN** 顯示 "No skills registered" 訊息

#### Scenario: List shows skill count
- **WHEN** 用戶執行 `lingmaflow skill list`
- **THEN** 顯示技能總數（例如：Found 5 skills）
