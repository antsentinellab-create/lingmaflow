## ADDED Requirements

### Requirement: Agent 必須在每個 task 完成後執行 harness done
當 agent 完成一個 openspec task 時,系統 SHALL 強制要求 agent 立即執行 `lingmaflow harness done <task_id>` 指令,並提供關鍵決策記錄。

#### Scenario: Task 完成後執行 harness done
- **WHEN** agent 完成一個 task (例如實作完 retry_budget.py)
- **THEN** agent 必須執行 `lingmaflow harness done <task_id> --notes "<關鍵決策>"`
- **AND** notes 欄位必填,包含遇到的問題、選擇的方案及原因

#### Scenario: Notes 欄位為空時拒絕執行
- **WHEN** agent 嘗試執行 `lingmaflow harness done` 但未提供 --notes 參數
- **THEN** 系統顯示錯誤訊息「Notes 欄位必填,請提供關鍵決策記錄」
- **AND** 指令執行失敗,tasks.json 不被更新

### Requirement: Session 結束前必須執行 harness log
當 agent 準備結束 session (context 快滿或主動停止) 時,系統 SHALL 強制要求執行 `lingmaflow harness log` 指令,記錄本次 session 的完整狀態。

#### Scenario: Session 結束前記錄狀態
- **WHEN** agent 準備結束 session
- **THEN** agent 必須執行 `lingmaflow harness log --change <change_name> --completed "..." --leftover "..." --failed "..." --next "..."`
- **AND** 所有四個參數 (completed, leftover, failed, next) 都必須提供

#### Scenario: Harness log 記錄到 PROGRESS.md
- **WHEN** agent 執行 `lingmaflow harness log`
- **THEN** 系統將資訊寫入 PROGRESS.md 檔案
- **AND** 下次 harness resume 時可讀取這些決策記憶

### Requirement: AGENTS.md 必須包含 harness 執行規則
當專案已初始化 harness (存在 tasks.json) 時,AGENTS.md SHALL 包含明確的 harness 執行規則章節,標示為「不可跳過」。

#### Scenario: AGENTS.md 包含 harness done 規則
- **WHEN** agents_injector 生成 AGENTS.md 且偵測到 tasks.json 存在
- **THEN** AGENTS.md 必須包含 `## openspec 執行強制規則` 章節
- **AND** 該章節列出 harness done 與 harness log 的執行時機與格式

#### Scenario: 未初始化 harness 的專案不顯示規則
- **WHEN** agents_injector 生成 AGENTS.md 但 tasks.json 不存在
- **THEN** AGENTS.md 不包含 harness 執行規則章節
- **AND** 避免在未使用 openspec 的專案中出現無關指令
