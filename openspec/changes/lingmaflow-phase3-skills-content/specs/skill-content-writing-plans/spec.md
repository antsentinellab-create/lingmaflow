## ADDED Requirements

### Requirement: Writing plans skill content
系統 SHALL 提供完整的 writing-plans 技能說明，指導 agent 拆解任務和撰寫計劃

#### Scenario: Large task needs breakdown
- **WHEN** 用戶提出一個大型任務或複雜功能
- **THEN** agent 應使用 writing-plans skill，將任務拆解為 2-5 分鐘可完成的小任務

#### Scenario: Define done conditions
- **WHEN** 定義每個任務的完成標準
- **THEN** 每個任務必須有明確、可驗證的 done condition

#### Scenario: Track progress
- **WHEN** 執行計劃時
- **THEN** 使用 checkbox 語法（- [ ]）追蹤進度，完成後標記為 - [x]
