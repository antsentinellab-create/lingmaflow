# LingmaFlow — Agent 執行規則

## 每次啟動必做
1. 執行：cat TASK_STATE.md
2. 確認「當前步驟」與「狀態」
3. 從未完成的 done condition 開始工作
4. 不重做已完成步驟

## Done Condition 規則
每個步驟必須全部達成才能推進：
- 對應檔案存在
- pytest 全綠
- TASK_STATE.md 已更新

## 錯誤處置
- 測試失敗：只修當前步驟，不往前推進
- 工具失敗：記錄到 TASK_STATE.md 未解決問題，停止等待
- 修正超過 3 次仍失敗：停止，標記 BLOCKED

## 禁止行為
- 不可跳過步驟
- 不可在測試未通過時更新 TASK_STATE.md
- 不可修改已完成步驟的檔案（除非明確指示）
