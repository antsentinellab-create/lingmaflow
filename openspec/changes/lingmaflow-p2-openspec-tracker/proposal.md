## Why

目前 `lingmaflow status` 與 `lingmaflow harness status --change <name>` 兩個指令各自獨立，中斷後需要執行兩次指令才能了解完整進度。開發者需要在 PHASE 級別與 task 級別之間切換，降低工作效率。此變更將 harness 狀態整合到 `lingmaflow status` 中，提供單一視角查看雙層進度。

## What Changes

- `lingmaflow status` 指令在有 active change 時，自動附加 harness 區塊顯示 task 級別進度
- `harness init` 執行時寫入 `.lingmaflow/active_change` 檔案記錄當前 change 名稱
- `harness init` 覆蓋執行時更新 `active_change` 檔案
- 向後相容：無 `active_change` 的舊專案行為不變，仍只顯示 PHASE 級別狀態

## Capabilities

### New Capabilities
- `status-harness-integration`: `lingmaflow status` 整合 harness 狀態顯示，包含 change 名稱、task 進度百分比、當前 task ID、最後 session 時間

### Modified Capabilities
<!-- 無現有 spec 需要修改，這是全新功能 -->

## Impact

**Affected code:**
- `lingmaflow/cli/lingmaflow.py`: `status` 子命令讀取 `active_change` 並附加 harness 區塊；`harness init` 子命令寫入 `active_change`
- `lingmaflow/core/harness.py`: 維持現有 `get_status()` 介面不變（已由外部呼叫）

**New files:**
- `.lingmaflow/active_change`: 純文字檔案，儲存当前 active change 名稱

**Tests:**
- 新增 3-4 個測試驗證 `active_change` 寫入、讀取、顯示邏輯

**Dependencies:**
- 無新增依賴
