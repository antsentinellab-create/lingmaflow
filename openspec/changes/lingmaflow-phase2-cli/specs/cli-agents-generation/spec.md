## ADDED Requirements

### Requirement: CLI agents generate command
系統 SHALL 提供 `lingmaflow agents generate` 命令來生成 AGENTS.md

#### Scenario: Generate AGENTS.md to default path
- **WHEN** 用戶執行 `lingmaflow agents generate`
- **THEN** 在當前工作目錄生成 AGENTS.md 檔案

#### Scenario: Generate with custom output path
- **WHEN** 用戶執行 `lingmaflow agents generate --output /some/path/AGENTS.md`
- **THEN** 在指定路徑生成 AGENTS.md

#### Scenario: Generate includes all skills
- **WHEN** 用戶執行 `lingmaflow agents generate`
- **THEN** 生成的內容包含 SkillRegistry 中所有技能

#### Scenario: Generate overwrites existing file
- **WHEN** 用戶執行 `lingmaflow agents generate` 且 AGENTS.md 已存在
- **THEN** 覆蓋原有檔案，顯示確認訊息或需要 --force 選項
