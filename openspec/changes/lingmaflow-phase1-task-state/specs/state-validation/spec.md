## ADDED Requirements

### Requirement: State transition validation
系統 SHALL 驗證所有狀態轉換符合定義的狀態機

#### Scenario: NOT_STARTED to IN_PROGRESS
- **WHEN** 首次 load() 且檔案不存在
- **THEN** 自動轉換為 IN_PROGRESS（透過 advance 第一次呼叫）

#### Scenario: IN_PROGRESS self-transition
- **WHEN** 在 IN_PROGRESS 狀態下呼叫 advance()
- **THEN** 保持 IN_PROGRESS，更新步驟資訊

#### Scenario: IN_PROGRESS to BLOCKED
- **WHEN** 在 IN_PROGRESS 狀態下呼叫 block(reason)
- **THEN** 轉換為 BLOCKED

#### Scenario: BLOCKED to IN_PROGRESS
- **WHEN** 在 BLOCKED 狀態下呼叫 resolve(reason)
- **THEN** 轉換回 IN_PROGRESS

#### Scenario: IN_PROGRESS to DONE
- **WHEN** 在 IN_PROGRESS 狀態下呼叫 complete()
- **THEN** 轉換為 DONE

#### Scenario: DONE is terminal
- **WHEN** 在 DONE 狀態下呼叫任何轉換方法（advance, block, complete）
- **THEN** 拋出 InvalidStateError（resolve 允許但無效）

### Requirement: Exception types
系統 SHALL 定義兩種自訂異常類別

#### Scenario: InvalidStateError for advance from DONE
- **WHEN** 對 DONE 狀態呼叫 advance()
- **THEN** 拋出 InvalidStateError 並包含描述性訊息

#### Scenario: InvalidStateError for invalid block
- **WHEN** 對 DONE 或 NOT_STARTED 狀態呼叫 block()
- **THEN** 拋出 InvalidStateError

#### Scenario: MalformedStateFileError for unparseable content
- **WHEN** 載入缺少必要欄位的 TASK_STATE.md
- **THEN** 拋出 MalformedStateFileError 並指出缺少的欄位

#### Scenario: MalformedStateFileError for invalid status value
- **WHEN** 載入包含未知狀態值（如 "RUNNING"）的檔案
- **THEN** 拋出 MalformedStateFileError
