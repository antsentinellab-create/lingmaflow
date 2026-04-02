## Why

Phase 1 和 Phase 2 已經完成了核心模組（task_state.py、skill_registry.py、agents_injector.py）和 CLI 工具，但 skills 目錄中的 5 個 SKILL.md 都是空檔案，缺乏實際內容。Agent 無法讀懂如何使用這些技能。Phase 3 將填充所有 5 個核心技能的完整內容，包括 YAML frontmatter 中繼資料和 agent 可執行的詳細說明。

## What Changes

- **修改** `lingmaflow/skills/brainstorming/SKILL.md`：從空檔案升級為完整技能說明
  - YAML frontmatter：name, version, triggers, priority
  - 正文：需求釐清流程、提問技巧、設計選項分析

- **修改** `lingmaflow/skills/writing-plans/SKILL.md`：從空檔案升級為完整技能說明
  - YAML frontmatter：name, version, triggers, priority
  - 正文：任務拆解原則、done condition 定義、進度追蹤方法

- **修改** `lingmaflow/skills/test-driven-development/SKILL.md`：從空檔案升級為完整技能說明
  - YAML frontmatter：name, version, triggers, priority
  - 正文：RED-GREEN-REFACTOR 循環、TDD 紀律

- **修改** `lingmaflow/skills/systematic-debugging/SKILL.md`：從空檔案升級為完整技能說明
  - YAML frontmatter：name, version, triggers, priority
  - 正文：系統化除錯步驟、問題重現、範圍縮小

- **修改** `lingmaflow/skills/subagent-driven/SKILL.md`：從空檔案升級為完整技能說明
  - YAML frontmatter：name, version, triggers, priority
  - 正文：TASK_STATE.md 讀取、進度更新、done condition 檢查

## Capabilities

### New Capabilities
- `skill-content-brainstorming`: 提供規格討論和需求釐清的完整指導
- `skill-content-writing-plans`: 提供任務拆解和計劃撰寫的完整指導
- `skill-content-tdd`: 提供測試驅動開發的完整流程和紀律
- `skill-content-debugging`: 提供系統化除錯的標準流程
- `skill-content-subagent`: 提供 subagent 執行任務的標準作業程序

### Modified Capabilities
- 無（此為內容填充，不改變技能格式或載入機制）

## Impact

- **Skills 目錄**: 5 個 SKILL.md 將包含完整的 agent 可執行內容
- **SkillRegistry**: scan() 現在會載入有意義的技能內容
- **CLI**: `lingmaflow skill find/list` 現在會顯示有用的技能
- **AgentsInjector**: 生成的 AGENTS.md 會包含 5 個實際可用的技能
- **用戶體驗**: Agent 現在可以真正使用這些技能來協助開發
