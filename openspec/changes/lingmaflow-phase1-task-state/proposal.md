## Why

LingmaFlow 需要一個防迷路核心模組來確保 AI agents 在執行複雜任務時能夠保持清晰的進度追蹤。目前的 TASK_STATE.md 檔案缺乏結構化的狀態管理，容易導致進度混亂、重複執行已完成步驟，或在遇到錯誤時無法正確恢復。這個模組將提供堅實的狀態管理基礎。

## What Changes

- **新增** `lingmaflow/core/task_state.py`：核心狀態管理模組
  - `TaskStatus` 枚舉：定義 NOT_STARTED、IN_PROGRESS、BLOCKED、DONE 四種狀態
  - `TaskStateManager` 類別：負責載入、保存、推進任務狀態
  - 狀態轉換邏輯與驗證
  - 自訂異常處理（InvalidStateError、MalformedStateFileError）

- **新增** `tests/test_task_state.py`：完整的單元測試覆蓋
  - 測試所有狀態轉換路徑
  - 測試邊界條件與錯誤情況
  - 使用 pytest fixture (tmp_path) 進行隔離測試

- **修改** `TASK_STATE.md`：更新為新的格式規範
  - 標準化欄位定義
  - ISO8601 時間戳記
  - 結構化的未解決問題列表

## Capabilities

### New Capabilities
- `task-state-management`: 任務狀態的生命週期管理，包含載入、保存、推進、阻擋、解除、完成等操作
- `state-validation`: 狀態轉換的驗證與錯誤處理，確保狀態機的一致性
- `file-persistence`: TASK_STATE.md 檔案的讀寫與格式解析

### Modified Capabilities
- 無（此為全新功能，不影響現有需求）

## Impact

- **核心模組**: `lingmaflow/core/task_state.py` 將被 `skill_registry.py` 和 `agents_injector.py` 使用
- **CLI 工具**: `lingmaflow/cli/lingmaflow.py` 可能需要整合狀態查詢命令
- **現有測試**: `tests/test_skill_registry.py` 和 `tests/test_task_state.py` 需通過
- **依賴**: 僅依賴 Python 標準庫 (enum, datetime, pathlib)，無外部依賴
