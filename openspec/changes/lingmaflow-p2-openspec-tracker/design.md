## Context

目前 LingmaFlow 專案使用兩個獨立指令追蹤進度：
- `lingmaflow status`：顯示 PHASE 級別狀態（從 TASK_STATE.md 讀取）
- `lingmaflow harness status --change <name>`：顯示 task 級別狀態（從 openspec/changes/<name>/tasks.json 讀取）

開發者在中斷後恢復工作時，需要執行兩次指令才能了解完整狀態。此設計提案透過 `active_change` 檔案機制，將兩者整合到單一 `lingmaflow status` 指令中。

**Constraints:**
- 不修改現有 `harness done`、`harness log`、`harness resume` 的行為
- 不新增 CLI 參數（`status` 維持零參數）
- 向後相容：舊專案無 `active_change` 時行為不變

## Goals / Non-Goals

**Goals:**
- `lingmaflow status` 在有 active change 時自動顯示 harness 區塊
- `harness init` 寫入 `.lingmaflow/active_change` 檔案
- 提供清晰的雙層進度視角：PHASE + task
- 向後相容舊專案

**Non-Goals:**
- 不修改 `harness done` / `log` / `resume` 的行為
- 不實作 AGENTS.md 規則遵守率監控（另立 proposal）
- 不新增任何 CLI 參數

## Decisions

### Decision 1: 採用 `active_change` 檔案機制（方案 C）

**Rationale:**
- **簡單性**：純文字檔案，易於讀取與維護
- **隱式關聯**：無需使用者手動指定 `--change` 參數
- **覆蓋安全**：`harness init` 覆蓋執行時更新檔案，符合預期行為
- **向後相容**：檔案不存在時，`status` 指令行為不變

**Alternatives considered:**
- **方案 A**：在 `TASK_STATE.md` 中新增欄位 → 耦合過高，違反關注點分離
- **方案 B**：CLI 參數 `--with-harness` → 增加使用者負擔，不符合「單一指令」目標
- **方案 D**：自動掃描所有 changes 找 in_progress → 效能差，可能多個 change 同時進行時產生歧義

### Decision 2: `active_change` 檔案位置與格式

**Location:** `.lingmaflow/active_change`
**Format:** 純文字，單行，內容為 change 名稱（例如：`ai-factory-phase-b`）

**Rationale:**
- `.lingmaflow/` 已是專案專屬目錄，符合既有慣例
- 純文字格式易於除錯與手動修正（如有需要）
- 單行內容簡化讀取邏輯

### Decision 3: Harness 區塊顯示格式

```
── Harness ──────────────────────
Change: ai-factory-phase-b
Progress: 12/23 tasks (52%)
Current task: 3.3
Last session: 2026-04-03 14:30
─────────────────────────────────
```

**Rationale:**
- 使用分隔線視覺區隔 PHASE 與 harness 資訊
- 顯示關鍵指標：change 名稱、進度百分比、當前 task、最後 session 時間
- 簡潔明瞭，不過度詳細（詳細 task 列表仍可用 `harness status` 查看）

### Decision 4: 資料來源

- **Change 名稱**：從 `.lingmaflow/active_change` 讀取
- **Task 進度**：呼叫 `HarnessManager.get_status(change_name)` 取得
- **最後 session 時間**：從 `HarnessManager.get_status()` 回傳的 `last_session` 欄位取得

**Rationale:**
- 重用現有 `HarnessManager` 邏輯，避免重複實作
- `get_status()` 已封裝 tasks.json 解析邏輯

## Risks / Trade-offs

### Risk 1: `active_change` 檔案遺失或損毀
**Impact:** `status` 指令無法顯示 harness 區塊，但不影響其他功能  
**Mitigation:** 
- 檔案不存在時，`status` 靜默忽略（不報錯）
- 使用者可重新執行 `harness init` 重建檔案

### Risk 2: 多個 change 同時進行時的混淆
**Impact:** `active_change` 只能記錄一個 change，可能與其他進行中的 change 不同步  
**Mitigation:** 
- 文件明確說明：此功能針對「主要進行中的 change」
- 如需查看其他 change，仍可使用 `harness status --change <name>`

### Trade-off: 隱式 vs 顯式關聯
- **隱式（選擇的方案）**：使用者無需記憶 change 名稱，但可能不清楚当前 active 是哪個
- **顯式（需參數）**：使用者需每次指定 `--change`，但完全可控

**Decision:** 選擇隱式，因為大多數情況只有一個 active change，且可透過 `status` 輸出確認
