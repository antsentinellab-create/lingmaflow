---
name: writing-plans
version: 1.0
triggers:
  - 計劃
  - 拆解任務
  - 實作計劃
  - plan
  - 步驟
  - 任務列表
  - work breakdown
priority: high
---

# Writing Plans - 任務拆解與計劃撰寫

## 核心原則

**將大型任務拆解為小型、可管理的步驟**。每個任務應該在 2-5 分鐘內完成，並有明確的完成標準。

### 為什麼需要任務拆解？

- ❌ **不要**試圖一次理解整個系統
- ❌ **不要**同時處理多個複雜問題
- ✅ **要**將大問題拆成小問題
- ✅ **要**專注於當前任務

## 任務拆解原則

### 1. 2-5 分鐘法則

每個任務應該：
- 可以在 2-5 分鐘內完成
- 有單一明確的目標
- 不依賴其他未完成的任務
- 產出可驗證的結果

### 2. 任務粒度範例

```
❌ 太大：「實作用戶認證系統」
✅ 剛好：「建立 User model 包含 email 和 password 欄位」
✅ 剛好：「實作 user registration API endpoint」
✅ 剛好：「編寫 registration 測試涵蓋成功和失敗情境」

❌ 太大：「優化資料庫效能」
✅ 剛好：「為 users 表的 email 欄位建立索引」
✅ 剛好：「使用 EXPLAIN 分析 slow query」
✅ 剛好：「將 N+1 query 改為 JOIN」
```

### 3. 任務依賴關係

```
任務 A（基礎）→ 任務 B（依賴 A）→ 任務 C（依賴 B）

確保：
- 依賴關係清晰
- 沒有循環依賴
- 基礎任務優先完成
```

## Done Condition 定義

每個任務必須有明確、可驗證的完成標準：

### SMART 原則

- **S**pecific（具體）：明確描述要完成什麼
- **M**easurable（可衡量）：可以客觀驗證是否完成
- **A**chievable（可達成）：在能力範圍內
- **R**elevant（相關）：與整體目標一致
- **T**ime-bound（有時限）：可在短時間內完成

### 好的 Done Condition 範例

```
✅ 「User model 包含 email, password, created_at 欄位」
✅ 「POST /api/register endpoint 接受 email 和 password」
✅ 「Registration 測試覆蓋率達到 90%」
✅ 「API response time < 200ms for 95th percentile」

❌ 「完成用戶系統」（太模糊）
❌ 「優化效能」（不可衡量）
❌ 「寫一些測試」（不具體）
```

## 進度追蹤

### Checkbox 語法

使用 Markdown checkbox 追蹤進度：

```markdown
## 實作計劃

### Phase 1: 基礎建設

- [x] 建立專案結構
- [x] 設定開發環境
- [ ] 建立 database schema
  - [x] 設計 ER diagram
  - [ ] 建立 migration files
  - [ ] 執行 migration

### Phase 2: 核心功能

- [ ] 實作 User model
- [ ] 實作 authentication
- [ ] 實作 authorization
```

### 狀態標記

- `- [ ]` - 未開始
- `- [x]` - 已完成
- `[-]` - 進行中（可選）
- `[!]` - 受阻（可選）

## 儲存規範

### 檔案位置

```
docs/plans/YYYY-MM-DD-<plan-name>.md

例如：
docs/plans/2026-04-02-user-authentication.md
docs/plans/2026-04-03-api-design.md
docs/plans/2026-04-04-database-migration.md
```

### 計劃文件結構

```markdown
# [計劃名稱]

**日期:** YYYY-MM-DD  
**負責人:** [姓名]  
**狀態:** [規劃中/進行中/已完成]

## 目標

[簡短描述這個計劃要達成什麼]

## 範圍

### In Scope
- [項目 1]
- [項目 2]

### Out of Scope
- [項目 1]
- [項目 2]

## 實作計劃

### Phase 1: [階段名稱]
- [ ] Task 1
- [ ] Task 2

### Phase 2: [階段名稱]
- [ ] Task 1
- [ ] Task 2

## 技術決策

- **決策 1:** [描述] - [原因]
- **決策 2:** [描述] - [原因]

## 參考資源

- [連結 1]
- [連結 2]

## 備註

[其他需要注意的事項]
```

## 工作流程檢查清單

在開始實作之前，確認：

- [ ] 所有任務都符合 2-5 分鐘法則
- [ ] 每個任務都有明確的 done condition
- [ ] 任務依賴關係已釐清
- [ ] 優先級已確定
- [ ] 已使用 checkbox 語法
- [ ] 計劃已儲存到 docs/plans/ 目錄
- [ ] 相關人員已審查並同意計劃

## 與其他技能的整合

### Brainstorming → Writing Plans

Brainstorming 確定了「做什麼」和「為什麼」，Writing Plans 定義「如何逐步完成」。

### Writing Plans → Subagent-Driven

計劃完成後，使用 `subagent-driven` skill 執行計劃，按照 checkbox 逐一完成任務。

### Writing Plans → TDD

每個任務的 done condition 應該包含測試要求，使用 `test-driven-development` skill 確保品質。

## 常見陷阱

### ❌ 任務太大

```
問題：「實作完整的電商平台」
解決：拆解為「建立 product catalog」、「實作 shopping cart」、「整合金流」等小任務
```

### ❌ 任務太模糊

```
問題：「改善程式碼」
解決：改為「extract method 超過 50 行的函式」、「移除重複的 validation logic」
```

### ❌ 忽略依賴關係

```
問題：同時開始多個相互依賴的任務
解決：建立清晰的依賴圖，從基礎任務開始
```

### ❌ 沒有 done condition

```
問題：「優化效能」
解決：改為「將 API response time 從 500ms 降低到 200ms」
```

## 下一步

計劃完成後：

1. **開始執行** → 使用 `subagent-driven` skill
2. **編寫測試** → 對每個任務使用 `test-driven-development`
3. **遇到問題** → 使用 `systematic-debugging` skill

---

**版本:** 1.0  
**最後更新:** 2026-04-02  
**相關技能:** brainstorming, test-driven-development, subagent-driven
