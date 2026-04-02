## Context

目前 AGENTS.md 是手動維護的靜態檔案，存在以下問題：
- 無法反映 SkillRegistry 中實際可用的 skills
- 新增 skill 後需要手動更新 AGENTS.md
- 容易遺漏或過時
- 缺乏統一的生成機制

這是一個全新的自動化 generation 功能，需要與 SkillRegistry 整合。

## Goals / Non-Goals

**Goals:**
- 實作 AgentsInjector 類別，提供 generate/inject/update 方法
- 動態從 SkillRegistry 讀取可用技能清單
- 產生標準化的 AGENTS.md 格式（固定內容 + 動態技能清單）
- 完整的錯誤處理（InjectionError）
- 100% 測試覆蓋率，使用 tmp_path 隔離

**Non-Goals:**
- 修改現有 AGENTS.md 的內容結構（僅自動生成）
- 複雜的模板系統（使用簡單字串組合）
- 版本控制整合（git add/commit）
- 增量更新（每次都重新生成完整檔案）

## Decisions

### 1. AGENTS.md 結構：固定章節 + 動態技能清單

**選擇**: AGENTS.md 包含四個主要章節

```markdown
# LingmaFlow — Agent 執行規則

## 每次啟動必做（固定內容）
1. 執行：cat TASK_STATE.md
2. 確認「當前步驟」與「狀態」
...

## 可用 Skill 清單（動態產生）
- test-driven-development: 寫測試、pytest、TDD
- systematic-debugging: debug、除錯
...

## Done Condition 規則（固定內容）
每個步驟必須全部達成才能推進
...

## 錯誤處置（固定內容）
測試失敗：只修當前步驟，不往前推進
...
```

**原因**:
- 分離固定內容和動態內容
- 保持人類可讀性
- 易於實作和維護
- 符合現有 AGENTS.md 結構

**替代方案考慮**:
- 完全動態生成（包括固定內容）：靈活性高但複雜
- Jinja2 模板：增加依賴，殺雞用牛刀
- 純文字組合：簡單直接，已足夠

### 2. 技能清單格式：Markdown 列表

**選擇**: 使用 Markdown 無序列表呈現技能

```markdown
## 可用 Skill 清單

- **skill-name**: trigger1, trigger2, trigger3
- **another-skill**: trigger4, trigger5
```

**原因**:
- 簡單清晰
- 符合 Markdown 慣例
- 易於解析和生成
- 視覺上易於掃描

**替代方案考慮**:
- 表格格式：過於正式，不易維護
- JSON/YAML block：機器友好但人類不友好
- 純文字段落：缺乏結構

### 3. 寫入策略：覆蓋式更新

**選擇**: update() 方法總是覆蓋現有檔案

**原因**:
- 簡單可靠
- 確保內容完全同步
- 避免合併衝突
- 符合 "source of truth" 原則

**例外**: inject() 用於初次建立，update() 用於後續更新

### 4. 錯誤處理策略：早期失敗

**選擇**: 在寫入前驗證路徑可寫性，無法寫入時拋出 InjectionError

**原因**:
- 早期發現問題
- 明確的錯誤語義
- 符合 Python "fail fast" 哲學
- 提供詳細的錯誤訊息

### 5. 測試策略：完全隔離

**選擇**: 所有測試使用 tmp_path fixture，不依賴真實 AGENTS.md

**原因**:
- 測試獨立，不受專案狀態影響
- 可精確控制測試情境
- 符合 pytest 最佳實踐
- 與 SkillRegistry 測試風格一致

## Risks / Trade-offs

### [Risk] 固定內容過時
**風險**: 硬編碼的固定內容可能與实际需求脫節

**緩解**:
- 將固定內容提取為常數或模板
- 未來可改為從外部檔案讀取
- 定期審查和更新

### [Risk] 技能清單過長
**風險**: 當 skills 很多時，AGENTS.md 會變得冗長

**緩解**:
- 文件建議保持 skills 精簡
- 未來可增加分類或分頁機制
- 使用摺疊區塊（details/summary）

### [Trade-off] 靈活性 vs 簡單性
**選擇**: 優先保持簡單，暫不實作：
- 自訂模板
- 條件式內容
- 多語言支援

**原因**: 
- MVP 思維，先解決核心問題
- 可透過後續迭代增強
- 避免過度設計

### [Risk] 編碼問題
**風險**: 寫入檔案時可能遇到編碼問題

**緩解**:
- 統一使用 UTF-8 編碼
- 錯誤訊息提示編碼問題
- 文件規範要求 UTF-8

## Migration Plan

### 階段 1: 核心實作（本次）
1. 實作 `lingmaflow/core/agents_injector.py`
2. 編寫完整測試
3. 確保 100% 通過

### 階段 2: 整合（後續任務）
1. 在 CLI 工具中加入 `lingmaflow agents` 命令
2. 初始化時自動生成 AGENTS.md
3. 提供手動更新命令

### 階段 3: 優化（未來可能的增強）
1. 增加模板系統
2. 支援自訂固定內容
3. 增加 git commit 選項

**回滾策略**: 
- 純新增功能，不影響現有代碼
- 測試失敗時刪除檔案即可
- 使用 git revert

## Open Questions

1. **是否需要支援多語言 AGENTS.md？**
   - 目前是英文標題 + 中文內容
   - 未來可能需要 i18n 支援

2. **固定內容是否應該外部化？**
   - 目前是硬編碼在程式碼中
   - 未來可改為從模板檔案讀取

3. **是否需要支援部分更新？**
   - 目前是完整覆蓋
   - 未來可能需要增量更新特定章節

4. **如何處理 skill 的描述？**
   - 目前只显示 triggers
   - 未來可能需要從 SKILL.md body 提取簡介
