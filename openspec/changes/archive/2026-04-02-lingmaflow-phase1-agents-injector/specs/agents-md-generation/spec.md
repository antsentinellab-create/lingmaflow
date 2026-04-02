## ADDED Requirements

### Requirement: AgentsInjector class structure
系統 SHALL 提供一個 AgentsInjector 類別來管理 AGENTS.md 的生成

#### Scenario: Create injector with registry and task_state_path
- **WHEN** 建立 AgentsInjector 物件並提供 SkillRegistry 和 task_state_path
- **THEN** 物件應包含 registry 和 task_state_path 屬性

### Requirement: Generate AGENTS.md content
AgentsInjector SHALL 提供 generate() 方法來產生 AGENTS.md 內容

#### Scenario: Generate with skills
- **WHEN** 呼叫 generate() 且 registry 中有 N 個 skills
- **THEN** 返回的字串應包含所有 skill 名稱和 triggers

#### Scenario: Generate with empty registry
- **WHEN** 呼叫 generate() 且 registry 為空
- **THEN** 返回的字串仍應包含固定章節，技能清單為空或顯示提示

#### Scenario: Include fixed sections
- **WHEN** 呼叫 generate()
- **THEN** 返回的字串應包含「每次啟動必做」、「Done Condition 規則」、「錯誤處置」等固定章節

#### Scenario: Format skill list correctly
- **WHEN** 呼叫 generate() 且有 skills
- **THEN** 技能清單應使用 Markdown 列表格式：`- **name**: trigger1, trigger2`

### Requirement: AGENTS.md content structure
generate() SHALL 產生標準化的 AGENTS.md 格式

#### Scenario: Include title
- **WHEN** generate() 被呼叫
- **THEN** 開頭應包含 `# LingmaFlow — Agent 執行規則` 標題

#### Scenario: Include skills section header
- **WHEN** generate() 被呼叫
- **THEN** 應包含 `## 可用 Skill 清單` 章節標題

#### Scenario: Dynamic skill content
- **WHEN** generate() 被呼叫
- **THEN** 技能清單內容應從 registry.skills 動態提取
