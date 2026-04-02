## ADDED Requirements

### Requirement: TaskStatus enumeration
系統 SHALL 定義四種任務狀態：NOT_STARTED、IN_PROGRESS、BLOCKED、DONE

#### Scenario: Initial state
- **WHEN** 任務首次被載入且無歷史記錄
- **THEN** 狀態應為 NOT_STARTED

#### Scenario: Active task
- **WHEN** 任務正在執行中
- **THEN** 狀態應為 IN_PROGRESS

#### Scenario: Blocked task
- **WHEN** 任務遇到阻礙無法繼續
- **THEN** 狀態應為 BLOCKED

#### Scenario: Completed task
- **WHEN** 所有步驟已完成
- **THEN** 狀態應為 DONE

### Requirement: TaskState dataclass
系統 SHALL 提供一個資料類別來承載任務狀態資訊

#### Scenario: Create initial state
- **WHEN** 建立初始狀態物件
- **THEN** 應包含 current_step="STEP-00", status=NOT_STARTED, empty fields

#### Scenario: State with history
- **WHEN** 從檔案載入狀態
- **THEN** 應包含所有歷史欄位（last_result, next_action, unresolved）

### Requirement: TaskStateManager lifecycle methods
TaskStateManager SHALL 提供完整的生命週期管理方法

#### Scenario: Load non-existent file
- **WHEN** 呼叫 load() 但檔案不存在
- **THEN** 返回初始狀態（status=NOT_STARTED），不拋出異常

#### Scenario: Save state
- **WHEN** 呼叫 save(state)
- **THEN** 將狀態寫入 TASK_STATE.md，使用標準格式

#### Scenario: Advance step
- **WHEN** 呼叫 advance(next_step, result) 且當前狀態為 IN_PROGRESS
- **THEN** 更新 current_step、last_result、next_action、timestamp，status 保持 IN_PROGRESS

#### Scenario: Block task
- **WHEN** 呼叫 block(reason) 且當前狀態為 IN_PROGRESS
- **THEN** status 變為 BLOCKED，reason 加入 unresolved 列表

#### Scenario: Resolve block
- **WHEN** 呼叫 resolve(reason) 且當前狀態為 BLOCKED
- **THEN** status 變為 IN_PROGRESS，reason 從 unresolved 移除

#### Scenario: Complete task
- **WHEN** 呼叫 complete() 且當前狀態為 IN_PROGRESS
- **THEN** status 變為 DONE，current_step 不變

#### Scenario: Advance from DONE state
- **WHEN** 在 DONE 狀態下呼叫 advance()
- **THEN** 拋出 InvalidStateError

### Requirement: State validation
系統 SHALL 驗證狀態轉換的合法性

#### Scenario: Valid transition
- **WHEN** 從 IN_PROGRESS 呼叫 advance()
- **THEN** 允許轉換

#### Scenario: Invalid transition
- **WHEN** 從 DONE 呼叫 advance()
- **THEN** 拋出 InvalidStateError

#### Scenario: Malformed file parsing
- **WHEN** 載入格式錯誤的 TASK_STATE.md
- **THEN** 拋出 MalformedStateFileError
