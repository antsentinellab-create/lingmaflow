## Context

目前 skills 目錄結構已經存在，包含 5 個技能資料夾：
- brainstorming/
- writing-plans/
- test-driven-development/
- systematic-debugging/
- subagent-driven/

但所有 SKILL.md 都是空檔案，缺乏：
- YAML frontmatter（name, version, triggers, priority）
- agent 可執行的具體說明內容

這是一個內容填充任務，不需要修改程式碼或格式規範。

## Goals / Non-Goals

**Goals:**
- 為 5 個技能建立完整的 YAML frontmatter
- 撰寫 agent 可直接讀懂並執行的詳細說明
- 每個技能的正文包含清晰的流程和檢查清單
- 確保所有 triggers 都能被 SkillRegistry.find() 正確匹配
- 保持 Markdown 格式的人類可讀性

**Non-Goals:**
- 修改 SKILL.md 格式規範（YAML frontmatter 格式不變）
- 新增或刪除技能（維持現有 5 個）
- 修改 SkillRegistry 載入邏輯
- 複雜的模板系統（使用純 Markdown）

## Decisions

### 1. SKILL.md 結構：Frontmatter + Body

**選擇**: 維持現有的 YAML frontmatter + Markdown body 結構

```yaml
---
name: skill-name
version: 1.0
triggers:
  - trigger1
  - trigger2
priority: high
---

# 技能標題

正文內容...
```

**原因**:
- 與現有 SkillRegistry.scan() 完全相容
- 人類可讀可寫
- 分離中繼資料和內容，易於維護

### 2. 正文結構：章節化 + 檢查清單

**選擇**: 使用 Markdown 章節和 unordered list

```markdown
## 核心原則

- 原則 1
- 原則 2

## 執行流程

1. 步驟 1
2. 步驟 2
3. 步驟 3

## 禁止行為

- ❌ 不要做 X
- ❌ 不要做 Y
```

**原因**:
- 清晰易讀
- Agent 容易解析和執行
- 符合技術文件慣例

### 3. Triggers 設計：多語言 + 同義詞

**選擇**: 包含中文、英文和常見同義詞

```yaml
triggers:
  - 寫測試
  - pytest
  - TDD
  - 單元測試
  - 測試
```

**原因**:
- 支援多語言使用者
- 提高匹配成功率
- 符合實際使用情境

### 4. Priority 分配：高優先級技能

**選擇**: 
- **high**: brainstorming, writing-plans, test-driven-development
- **normal**: systematic-debugging, subagent-driven

**原因**:
- 高優先級技能是基礎工作流程
- debug 和 subagent 是被動觸發（遇到問題才用）
- 未來可用於優先級調度

### 5. 內容長度：精簡但完整

**選擇**: 每個技能 500-1000 字

**原因**:
- 太短：資訊不足
- 太長：Agent 難以快速吸收
- 保持聚焦在核心流程和關鍵檢查點

## Risks / Trade-offs

### [Risk] 內容過於簡化
**風險**: 某些複雜情境可能未被涵蓋

**緩解**:
- 聚焦在常見使用情境
- 未來可迭代增強
- 提供參考資源連結

### [Risk] Triggers 不夠全面
**風險**: 用戶使用不同的措辭時無法匹配

**緩解**:
- 文件建議常見的 triggers
- 未來可根據使用數據調整
- 支持用戶自訂 triggers

### [Trade-off] 通用性 vs 特定性
**選擇**: 優先保持通用性，適用於多種專案類型

**原因**: 
- LingmaFlow 是通用框架
- 可透過後續迭代增加領域特定技能
- 避免過度特化

### [Risk] 內容過時
**風險**: 隨著框架演進，技能內容可能需要更新

**緩解**:
- 使用語意化版本號（version field）
- 定期審查和更新
- 在 AGENTS.md 中顯示版本資訊

## Migration Plan

### 階段 1: 內容撰寫（本次）
1. 撰寫 5 個 SKILL.md 的完整內容
2. 確保 YAML frontmatter 格式正確
3. 驗證 SkillRegistry 可正確載入

### 階段 2: 驗證（本次）
1. `lingmaflow skill list` 顯示 5 個技能
2. `lingmaflow skill find <keyword>` 正確匹配
3. `lingmaflow agents generate` 生成包含所有技能的 AGENTS.md

### 階段 3: 使用回饋（未來）
1. 收集 agent 使用數據
2. 優化 triggers 和內容
3. 增加更多實用技能

**回滾策略**: 
- 純內容更新，不影響程式碼
- 測試失敗時使用 git revert
- 保持 backward compatible（舊格式仍有效）

## Open Questions

1. **是否需要增加更多技能？**
   - 例如：code-review, documentation, refactoring
   - 可在未來 Phase 增加

2. **是否需要多語言版本？**
   - 目前是繁體中文 + 英文術語
   - 未來可增加 i18n 支援

3. **是否需要互動式元素？**
   - 例如：提問模板、檢查表工具
   - 目前是靜態內容

4. **如何處理技能之間的依賴？**
   - 例如：TDD 需要使用 writing-plans
   - 目前是獨立技能，未來可增加 cross-reference
