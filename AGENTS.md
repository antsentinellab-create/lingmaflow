# LingmaFlow — Agent 執行規則

## 每次啟動必做

1. 執行：cat TASK_STATE.md
2. 確認「當前步驟」與「狀態」
3. 從未完成的 done condition 開始工作
4. 不重做已完成步驟

## 可用 Skill 清單

目前沒有可用的技能。

## Done Condition 規則

每個步驟必須全部達成才能推進：
- 對應檔案存在
- pytest 全綠
- TASK_STATE.md 已更新

## 錯誤處置

- 測試失敗：只修當前步驟，不往前推進
- 工具失敗：記錄到 TASK_STATE.md 未解決問題，停止等待
- 修正超過 3 次仍失敗：停止，標記 BLOCKED

## harness 執行規則

### 開始新 session 時（每次都要做）
1. `lingmaflow harness resume`
   複製輸出的 startup sequence 執行
2. 確認 git log 和 PROGRESS.md
3. 從 tasks.json 找下一個 done=false 的 task

### 完成每個 task 後（立即執行）
`lingmaflow harness done <task_id> --notes "<關鍵決策>"`
notes 必填，記錄：
- 遇到什麼問題
- 選擇了什麼方案以及為什麼
- 下一個 task 需要注意什麼

### session 結束前（context 快滿或主動停止時）
`lingmaflow harness log \
  --completed "<完成的 task ids>" \
  --leftover "<中斷點的狀態>" \
  --failed "<嘗試過但失敗的方案>" \
  --next "<下一步具體指示>"`

### 禁止行為
- 不可修改 tasks.json 的 id 或 description 欄位
- 不可刪除任何 task 條目
- 不可在沒有執行 harness done 的情況下宣告 task 完成
- 不可跳過 notes 欄位
