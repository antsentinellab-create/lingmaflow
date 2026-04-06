## ADDED Requirements

### Requirement: Harness Resume 整合多來源狀態資訊
`lingmaflow harness resume` 指令 SHALL 讀取並整合三個來源的資訊 (TASK_STATE.md、tasks.json、PROGRESS.md),提供完整的接回上下文。

#### Scenario: 顯示完整接回資訊
- **WHEN** agent 執行 `lingmaflow harness resume`
- **THEN** 系統輸出包含以下區塊:
  - 📍 當前位置: Phase (來自 TASK_STATE.md) + Task (來自 tasks.json)
  - 📝 上次結果: Last Result (來自 TASK_STATE.md)
  - 💡 決策記憶: 上次 session 的關鍵決策 (來自 PROGRESS.md)
  - 🎯 下一步: 給 agent 的具體接回指令
- **AND** 所有資訊合併為單一輸出,無需查詢多個檔案

#### Scenario: 找不到某個來源時降級處理
- **WHEN** harness resume 執行但 PROGRESS.md 不存在
- **THEN** 系統仍顯示 TASK_STATE.md 與 tasks.json 的資訊
- **AND** 在決策記憶區塊顯示「⚠️ 無歷史決策記錄 (PROGRESS.md 不存在)」
- **AND** 不中斷指令執行

#### Scenario: 指定 Change 名稱
- **WHEN** agent 執行 `lingmaflow harness resume --change <change_name>`
- **THEN** 系統從 `openspec/changes/<change_name>/tasks.json` 讀取 task 資訊
- **AND** 若未指定 --change,使用預設的 tasks.json (專案根目錄)

### Requirement: 輸出格式結構化且易讀
Harness resume 的輸出 SHALL 採用清晰的視覺分隔與 emoji 標示,讓 agent 快速掃描關鍵資訊。

#### Scenario: 標準輸出格式
- **WHEN** harness resume 成功執行
- **THEN** 輸出格式如下:
  ```
  === Harness Resume ===
  
  📍 當前位置:
    Phase: PHASE-B (Retry Budget Implementation)
    Task: 3.2 (實作 retry_budget.py) [done: false]
  
  📝 上次結果:
    Step 3.1 完成,pytest 全綠
  
  💡 決策記憶 (from PROGRESS.md):
    - 選擇 exponential backoff 而非 fixed delay
    - 最大重試次數設為 3
  
  🎯 下一步:
    1. 確認 workflow/retry_budget.py 存在
    2. 執行 pytest tests/test_retry_budget.py
    3. 完成後執行: lingmaflow harness done 3.2 --notes "..."
  ```
- **AND** 使用 `===` 作為標題分隔線
- **AND** 每個區塊使用不同的 emoji 標示

#### Scenario: 無待辦任務時的提示
- **WHEN** tasks.json 中所有 tasks 的 done 都為 true
- **THEN** 系統顯示「✅ 所有 tasks 已完成」
- **AND** 建議執行 `lingmaflow checkpoint` 推進到下一個 Phase
- **AND** 不提供「下一步」區塊

### Requirement: 從 PROGRESS.md 解析決策記憶
Harness resume SHALL 從 PROGRESS.md 中解析最近一次 session 的 harness log 記錄,提取關鍵決策並簡要呈現。

#### Scenario: 解析最近的 harness log
- **WHEN** PROGRESS.md 包含多次 harness log 記錄
- **THEN** 系統只提取最後一筆記錄的 completed、leftover、failed、next 欄位
- **AND** 將這些資訊格式化為清單,每項一行
- **AND** 限制最多顯示 5 項,避免輸出過長

#### Scenario: PROGRESS.md 格式錯誤時的处理
- **WHEN** PROGRESS.md 存在但格式不符合預期
- **THEN** 系統顯示警告「⚠️ 無法解析 PROGRESS.md,請檢查格式」
- **AND** 跳過決策記憶區塊
- **AND** 繼續顯示其他資訊
