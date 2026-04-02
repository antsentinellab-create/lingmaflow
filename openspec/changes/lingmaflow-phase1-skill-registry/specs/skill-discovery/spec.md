## ADDED Requirements

### Requirement: Skill data structure
系統 SHALL 提供一個 Skill dataclass 來承載技能資訊

#### Scenario: Create skill with all fields
- **WHEN** 建立 Skill 物件並提供所有必要欄位
- **THEN** 物件應包含 name, version, triggers, priority, content, path 屬性

#### Scenario: Default values
- **WHEN** 建立 Skill 物件時未提供預設值
- **THEN** version 預設為 "1.0"，priority 預設為 "normal"

### Requirement: Scan skills directory
SkillRegistry SHALL 提供 scan() 方法來掃描 skills 目錄

#### Scenario: Scan empty directory
- **WHEN** 掃描空的 skills 目錄
- **THEN** 返回空列表 []

#### Scenario: Scan directory with skills
- **WHEN** 掃描包含 N 個 SKILL.md 的目錄
- **THEN** 返回包含 N 個 Skill 物件的列表

#### Scenario: Scan nested directories
- **WHEN** 掃描包含多層子目錄的 skills 目錄
- **THEN** 只掃描直接子目錄下的 SKILL.md，不遞迴掃描

#### Scenario: Parse YAML frontmatter
- **WHEN** 解析包含 YAML frontmatter 的 SKILL.md
- **THEN** 正確提取 name, version, triggers, priority 等中繼資料

#### Scenario: Extract markdown body
- **WHEN** 解析 SKILL.md
- **THEN** 正確提取 frontmatter 之後的 Markdown 正文作為 content

### Requirement: Handle malformed skills
scan() SHALL 在遇到格式錯誤的 SKILL.md 時拋出 MalformedSkillError

#### Scenario: Missing name field
- **WHEN** SKILL.md 缺少 name 欄位
- **THEN** 拋出 MalformedSkillError 並指出缺少 name

#### Scenario: Missing triggers field
- **WHEN** SKILL.md 缺少 triggers 欄位
- **THEN** 拋出 MalformedSkillError 並指出缺少 triggers

#### Scenario: Invalid YAML syntax
- **WHEN** SKILL.md 的 YAML frontmatter 語法錯誤
- **THEN** 拋出 MalformedSkillError 並描述解析錯誤
