## Context

LingmaFlow 目前缺乏統一的任務狀態管理機制。AI agents 在執行任務時，需要一個可靠的防迷路系統來：
- 追蹤當前進度
- 記錄歷史操作
- 處理錯誤與阻礙
- 確保不會重複執行已完成的步驟

目前的 `TASK_STATE.md` 是一個手動維護的 Markdown 檔案，缺乏格式驗證和狀態轉換邏輯。

## Goals / Non-Goals

**Goals:**
- 實作型別安全的狀態管理（使用 Enum）
- 提供清晰的狀態轉換 API
- 自動化的 TASK_STATE.md 讀寫
- 完整的錯誤處理與驗證
- 100% 測試覆蓋率

**Non-Goals:**
- 資料庫持久化（僅使用 Markdown 檔案）
- 分散式狀態同步
- 版本控制整合（git commit/push）
- UI 介面或可視化

## Decisions

### 1. 狀態機設計：有限狀態機 (FSM)

**選擇**: 使用明確的狀態枚舉和狀態轉換方法

**原因**:
- 簡單易懂，易於測試
- Python Enum 提供型別安全
- 避免複雜的狀態機庫依賴

**替代方案考慮**:
- 使用 `transitions` 庫：增加依賴，學習曲線
- 自訂字串狀態：缺乏型別檢查，易出錯

### 2. 檔案格式：Markdown with YAML-like sections

**選擇**: 結構化的 Markdown 格式，使用冒號分隔鍵值對

**原因**:
- 人類可讀可寫
- 與現有 TASK_STATE.md 相容
- 易於解析（正則表達式 + 逐行分析）

**替代方案考慮**:
- JSON/YAML: 機器友好但人類不友好
- TOML: 較少人熟悉

### 3. 異常處理：自訂異常類別

**選擇**: 定義 `InvalidStateError` 和 `MalformedStateFileError`

**原因**:
- 明確的錯誤語義
- 易於捕獲和處理
- 提供更好的錯誤訊息

**替代方案考慮**:
- 使用標準 `ValueError`: 語義不夠明確
- 返回錯誤代碼: Pythonic 不佳

### 4. 時間戳記：ISO8601 UTC

**選擇**: 使用 `datetime.now().isoformat()`

**原因**:
- 標準格式
- 包含時區資訊（可選）
- 易於排序和比較

## Risks / Trade-offs

### [Risk] Markdown 解析脆弱性
**緩解**: 
- 使用寬鬆的解析策略
- 提供預設值
- 詳細的錯誤訊息幫助除錯

### [Risk] 競合條件（多程序同時寫入）
**緩解**: 
- 文件鎖定（未來增強）
- 單一 agent 負責寫入
- 標記為已知限制

### [Trade-off] 效能 vs 可讀性
**選擇**: 優先考慮可讀性和易維護性

**原因**: 
- 狀態更新頻率低
- 檔案小（< 1KB）
- 開發者體驗優先

## Migration Plan

1. **建立新檔案**: `lingmaflow/core/task_state.py`
2. **編寫測試**: `tests/test_task_state.py`
3. **運行測試**: 確保所有測試通過
4. **更新文件**: 將現有 TASK_STATE.md 轉換為新格式
5. **整合**: 在其他模組中引入使用

**回滾策略**: 
- 保留原始 task_state.py.bak
- 測試失敗時刪除新檔案
- 使用 git revert

## Open Questions

1. 是否需要支援自訂步驟 ID 格式？（目前固定為 STEP-XX）
2. 是否需要支援多個未解決問題的標籤？（目前是純文字區塊）
3. 是否需要在 save() 時自動 git commit？（目前純粹檔案寫入）
