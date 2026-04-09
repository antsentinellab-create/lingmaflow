# LingmaFlow — Agent 執行規則

## 每次啟動必做

1. 執行：cat TASK_STATE.md
2. 執行：cat .lingmaflow/current_task.md（若存在）
3. 確認「當前步驟」與「狀態」
4. 從未完成的 done condition 開始工作
5. 不重做已完成步驟

## 可用 Skill 清單

目前沒有可用的技能。

## Done Condition 規則

每個步驟必須全部達成才能推進：
- 對應檔案存在
- pytest 全綠
- TASK_STATE.md 已更新

## BDD 驗收規則（偵測到 features/ 目錄）

### 禁止行為
- 不得修改 features/ 目錄下的任何 .feature 檔案
- 不得刪除或跳過任何 Scenario
- 不得新增 Scenario 來取代現有的 Scenario
- behave 未全綠不得執行 lingmaflow checkpoint

### behave 執行時機
Done Condition 包含 behave: 時，完成實作後立即執行：
```bash
behave features/<對應的 feature 檔案>
```
必須全綠才算完成此條件


## 錯誤處置

- 測試失敗：只修當前步驟，不往前推進
- 工具失敗：記錄到 TASK_STATE.md 未解決問題，停止等待
- 修正超過 3 次仍失敗：停止，標記 BLOCKED


## harness 執行規則（強制，不可跳過）

### 每完成一個 task 後，立即執行
```bash
lingmaflow harness done <task_id> --notes "<關鍵決策>"
```

### session 結束前，執行
```bash
lingmaflow harness log --change <change_name> --completed "<完成的 task IDs>" --leftover "<未完成的 task>" --failed "<失敗記錄，無則填 none>" --next "<下一步指引>"
```

### 禁止行為

- 不可跳過 harness done，即使 task 很簡單
- 不可修改 tasks.json 的 id 或 description 欄位
- 不可刪除任何 task 條目
