## ADDED Requirements

### Requirement: Get skill by name
SkillRegistry SHALL 提供 get(name) 方法來依名稱查詢技能

#### Scenario: Get existing skill
- **WHEN** 呼叫 get("test-driven-development") 且該 skill 存在
- **THEN** 返回對應的 Skill 物件

#### Scenario: Get non-existent skill
- **WHEN** 呼叫 get("不存在的 skill") 
- **THEN** 返回 None，不拋出異常

#### Scenario: Case-sensitive matching
- **WHEN** 呼叫 get("Test-Driven-Development")（大小寫不同）
- **THEN** 返回 None（名稱比對區分大小寫）

### Requirement: Find skills by keyword
SkillRegistry SHALL 提供 find(keyword) 方法來依關鍵字搜尋技能

#### Scenario: Find by exact trigger match
- **WHEN** 呼叫 find("pytest") 且有 skill 的 trigger 包含 "pytest"
- **THEN** 返回包含該 skill 的列表

#### Scenario: Find by partial trigger match
- **WHEN** 呼叫 find("測試") 且有 skill 的 trigger 為 "寫測試"
- **THEN** 返回包含該 skill 的列表（部分匹配）

#### Scenario: Case-insensitive search
- **WHEN** 呼叫 find("PYTEST") 
- **THEN** 返回與 find("pytest") 相同的結果（不分大小寫）

#### Scenario: No matching skills
- **WHEN** 呼叫 find("不相關的關鍵字") 且無匹配的 skill
- **THEN** 返回空列表 []

#### Scenario: Multiple matches
- **WHEN** 呼叫 find("測試") 且多個 skill 的 triggers 都包含 "測試"
- **THEN** 返回所有匹配的 skill 列表

### Requirement: List all skills
SkillRegistry SHALL 提供 list() 方法來列出所有已載入的技能

#### Scenario: List empty registry
- **WHEN** registry 中沒有技能
- **THEN** 返回空列表 []

#### Scenario: List loaded skills
- **WHEN** registry 中已載入 N 個技能
- **THEN** 返回包含 N 個 skill 名稱的列表

#### Scenario: Return skill names only
- **WHEN** 呼叫 list()
- **THEN** 只返回 skill.name，不返回完整 Skill 物件
