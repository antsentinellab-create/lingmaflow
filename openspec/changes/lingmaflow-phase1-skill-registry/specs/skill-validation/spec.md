## ADDED Requirements

### Requirement: MalformedSkillError exception
系統 SHALL 定義 MalformedSkillError 異常類別

#### Scenario: Inherit from Exception
- **WHEN** 建立 MalformedSkillError 物件
- **THEN** 可作為一般 Exception 捕獲

#### Scenario: Descriptive error message
- **WHEN** 拋出 MalformedSkillError
- **THEN** 錯誤訊息應指出缺少的欄位或解析問題

### Requirement: Validate required fields
scan() SHALL 驗證每個 SKILL.md 包含必要欄位

#### Scenario: Validate name field exists
- **WHEN** 解析 SKILL.md frontmatter
- **THEN** 檢查 name 欄位存在且非空字串

#### Scenario: Validate triggers field exists
- **WHEN** 解析 SKILL.md frontmatter
- **THEN** 檢查 triggers 欄位存在且為列表

#### Scenario: Validate triggers is a list
- **WHEN** 解析 SKILL.md frontmatter 且 triggers 不是列表
- **THEN** 拋出 MalformedSkillError 指出 triggers 格式錯誤

### Requirement: Optional fields handling
系統 SHALL 正確處理選擇性欄位

#### Scenario: Missing version uses default
- **WHEN** SKILL.md 缺少 version 欄位
- **THEN** 使用預設值 "1.0"

#### Scenario: Missing priority uses default
- **WHEN** SKILL.md 缺少 priority 欄位
- **THEN** 使用預設值 "normal"

#### Scenario: Empty content is valid
- **WHEN** SKILL.md 只有 frontmatter，沒有正文
- **THEN** 視為有效，content 為空字串
