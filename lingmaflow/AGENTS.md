# LingmaFlow — Agent 執行規則

## 每次啟動必做

1. 執行：cat TASK_STATE.md
2. 確認「當前步驟」與「狀態」
3. 從未完成的 done condition 開始工作
4. 不重做已完成步驟

## 可用 Skill 清單

- **subagent-driven**: 執行計劃, 實作, apply, 開始做, 跑任務, execute plan, implementation
- **writing-plans**: 計劃, 拆解任務, 實作計劃, plan, 步驟, 任務列表, work breakdown
- **test-driven-development**: 寫測試, pytest, TDD, 單元測試, 測試, unit test, test first
- **brainstorming**: 規格, 設計, 需求, brainstorm, 討論方案, 功能規劃, 產品設計
- **systematic-debugging**: debug, 除錯, 錯誤, bug, fix, 失敗, error, exception

## Done Condition 規則

每個步驟必須全部達成才能推進：
- 對應檔案存在
- pytest 全綠
- TASK_STATE.md 已更新

## 錯誤處置

- 測試失敗：只修當前步驟，不往前推進
- 工具失敗：記錄到 TASK_STATE.md 未解決問題，停止等待
- 修正超過 3 次仍失敗：停止，標記 BLOCKED
