## Context

目前 LingmaFlow 的 skills 目錄結構已經存在，但缺乏統一的格式和載入機制：
- 5 個 skill 資料夾，但 SKILL.md 都是空的
- 沒有標準的中繼資料格式
- 沒有自動發現和查詢機制
- Agent 無法動態使用 skills

這是一個全新的核心功能，需要從零開始設計。

## Goals / Non-Goals

**Goals:**
- 定義 SKILL.md 的 YAML frontmatter 格式
- 實作 SkillRegistry 類別，提供 scan/get/find/list 方法
- 支援關鍵字模糊比對（不区分大小寫）
- 完整的錯誤處理（MalformedSkillError）
- 100% 測試覆蓋率，使用 tmp_path 隔離

**Non-Goals:**
- Skill 執行邏輯（僅管理，不執行）
- Skill 之間的依賴關係管理
- 熱重載或動態更新
- 效能優化（skills 數量少，記憶體操作即可）
- 資料庫持久化（純檔案操作）

## Decisions

### 1. SKILL.md 格式：YAML Frontmatter + Markdown Body

**選擇**: 使用 YAML frontmatter 儲存中繼資料，Markdown 正文儲存說明內容

```yaml
---
name: test-driven-development
version: 1.0
triggers:
  - 寫測試
  - pytest
  - TDD
priority: high
---
正文為 agent 可讀的說明內容
```

**原因**:
- Frontmatter 是靜態網站生成器的標準做法（如 Jekyll、Hugo）
- 人類可讀可寫
- PyYAML 已安裝，無需新增依賴
- 分離中繼資料和內容，易於解析和管理

**替代方案考慮**:
- 純 JSON/YAML 檔案：不利於人類閱讀和編寫
- TOML：較少人熟悉，無明顯優勢
- Python 模組：增加複雜性，不利于非程式設計師維護

### 2. 關鍵字比對邏輯：簡單包含匹配

**選擇**: `keyword in trigger.lower()` 簡單字符串包含匹配

**原因**:
- 實作簡單，易於理解
- 效能足夠（skills 數量少）
- 符合直覺（"pytest" 匹配 "寫 pytest 測試"）

**替代方案考慮**:
- 正則表達式：過於複雜，效能差
- 全文搜尋（BM25）：殺雞用牛刀
- 語義相似度：需要 ML 模型，過度設計

### 3. Priority 欄位：列舉型別

**選擇**: 限制為 `high` / `normal` / `low` 三個值

**原因**:
- 簡單明確，易於排序
- 未來可用於優先級調度
- 避免自由字串的不一致性

**驗證**: 可在未來增加枚舉驗證，但目前保持寬鬆

### 4. 錯誤處理策略：早期失敗

**選擇**: 在 scan() 時立即拋出 MalformedSkillError，而不是跳過錯誤檔案

**原因**:
- 早期發現問題，避免隱藏錯誤
- 強制開發者修正格式
- 符合 Python "fail fast" 哲學

**例外**: get() 返回 None 而不是拋異常，因為查詢不存在的是合理操作

### 5. 測試策略：完全隔離

**選擇**: 所有測試使用 tmp_path fixture，不依賴真實 skills/ 目錄

**原因**:
- 測試獨立，不受專案狀態影響
- 可精確控制測試情境
- 符合 pytest 最佳實踐

## Risks / Trade-offs

### [Risk] YAML Frontmatter 解析錯誤
**緩解**: 
- 使用成熟的 pyyaml 庫
- 詳細的錯誤訊息指出缺少的欄位
- 提供格式範例

### [Risk] 關鍵字比對過於寬鬆
**風險**: "test" 可能匹配到不相關的 skill

**緩解**:
- 文件說明建議使用具體的 triggers
- 未來可增加權重或評分機制
- 返回多個結果讓使用者選擇

### [Trade-off] 功能完整性 vs 簡單性
**選擇**: 優先保持簡單，暫不實作：
- Skill 依賴關係
- 版本相容性檢查
- 懶載入優化

**原因**: 
- MVP 思維，先解決核心問題
- 可透過後續迭代增強
- 避免過度設計

### [Risk] 編碼問題
**風險**: SKILL.md 可能使用不同編碼（UTF-8, Big5, etc.）

**緩解**:
- 統一使用 UTF-8 編碼讀取
- 錯誤訊息提示編碼問題
- 文件規範要求 UTF-8

## Migration Plan

### 階段 1: 核心實作（本次）
1. 實作 `lingmaflow/core/skill_registry.py`
2. 編寫完整測試
3. 確保 100% 通過

### 階段 2: 格式遷移（後續任務）
1. 更新現有 5 個 SKILL.md 為新格式
2. 添加實際的 skill 說明內容
3. 驗證 registry 可正確載入

### 階段 3: 整合（後續任務）
1. CLI 工具整合 `lingmaflow skill find <keyword>`
2. Agent 工作流整合
3. 文件更新

**回滾策略**: 
- 純新增功能，不影響現有代碼
- 測試失敗時刪除檔案即可
- 使用 git revert

## Open Questions

1. **Priority 是否需要驗證？** 
   - 目前是自由字串，未來可能需要 Enum 驗證
   
2. **Version 欄位的用途？**
   - 目前未使用，未來可能用於相容性檢查或更新提示

3. **是否支援多語言 triggers？**
   - 目前是簡單的字符串匹配，未來可能需要 i18n 支援

4. **Skill 之間如何協作？**
   - 目前是獨立的，未來可能需要依賴注入或組合機制
