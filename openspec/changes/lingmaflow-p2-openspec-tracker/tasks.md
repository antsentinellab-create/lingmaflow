## 1. Harness Init - Write active_change

- [ ] 1.1 在 `lingmaflow/cli/lingmaflow.py` 的 `harness_init` 函數中，新增寫入 `.lingmaflow/active_change` 檔案的邏輯
- [ ] 1.2 確保 `.lingmaflow/` 目錄存在（如不存在則建立）
- [ ] 1.3 寫入 change 名稱到 `.lingmaflow/active_change`（純文字，單行）
- [ ] 1.4 處理覆蓋情況：若檔案已存在，直接覆寫內容

## 2. Status Command - Read and Display Harness Block

- [ ] 2.1 在 `lingmaflow/cli/lingmaflow.py` 的 `status` 函數中，新增讀取 `.lingmaflow/active_change` 的邏輯
- [ ] 2.2 若 `active_change` 檔案存在，讀取 change 名稱
- [ ] 2.3 呼叫 `HarnessManager.get_status(change_name)` 取得 task 進度資訊
- [ ] 2.4 格式化 harness 區塊輸出（包含 Change、Progress、Current task、Last session）
- [ ] 2.5 將 harness 區塊附加到 PHASE status 之後顯示
- [ ] 2.6 若 `active_change` 檔案不存在，跳過 harness 區塊（向後相容）

## 3. Harness Block Formatting

- [ ] 3.1 實作分隔線格式：`── Harness ──────────────────────`
- [ ] 3.2 計算進度百分比：`(completed / total) * 100`，無條件捨去至整數
- [ ] 3.3 格式化最後 session 時間為 `YYYY-MM-DD HH:MM`
- [ ] 3.4 若無 last_session，顯示 `Last session: None`

## 4. Testing

- [ ] 4.1 新增測試：驗證 `harness init` 寫入 `active_change` 檔案
- [ ] 4.2 新增測試：驗證 `harness init` 覆蓋已存在的 `active_change` 檔案
- [ ] 4.3 新增測試：驗證 `status` 在有 `active_change` 時顯示 harness 區塊
- [ ] 4.4 新增測試：驗證 `status` 在無 `active_change` 時不顯示 harness 區塊（向後相容）
- [ ] 4.5 執行所有測試並確認全綠

## 5. Documentation & Verification

- [ ] 5.1 更新 TASK_STATE.md 標記此變更完成
- [ ] 5.2 手動測試完整流程：`harness init` → `status` 確認輸出正確
- [ ] 5.3 驗證向後相容性：移除 `active_change` 後 `status` 仍正常運作
