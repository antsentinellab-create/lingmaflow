## ADDED Requirements

### Requirement: TaskStateManager 擴充 - Done Conditions 管理

TaskStateManager 新增三個方法用於管理 Done Conditions：`get_conditions()`, `mark_condition_done()`, `all_conditions_done()`。

#### Scenario: 解析 Done Conditions 區塊
- **WHEN** 調用 `get_conditions()` 且 TASK_STATE.md 包含 Done Conditions 區塊
- **THEN** 返回所有條件字串的列表（不包含 checkbox 符號）

#### Scenario: 沒有 Done Conditions 區塊
- **WHEN** 調用 `get_conditions()` 但 TASK_STATE.md 沒有該區塊
- **THEN** 返回空列表，不拋出異常

#### Scenario: 標記條件為完成
- **WHEN** 調用 `mark_condition_done("file:lingmaflow/core/task_state.py")`
- **THEN** 將對應的 `[ ]` 改為 `[x]` 並保存文件

#### Scenario: 標記不存在的條件
- **WHEN** 調用 `mark_condition_done("nonexistent:condition")` 且該條件不存在
- **THEN** 拋出 ValueError 異常，訊息包含「Condition not found」

#### Scenario: 檢查所有條件是否完成
- **WHEN** 調用 `all_conditions_done()` 且所有條件都是 `[x]`
- **THEN** 返回 True

#### Scenario: 部分條件未完成
- **WHEN** 調用 `all_conditions_done()` 且有任一條件是 `[ ]`
- **THEN** 返回 False

#### Scenario: 空的 Done Conditions
- **WHEN** 調用 `all_conditions_done()` 但 Done Conditions 區塊為空
- **THEN** 返回 True（視為已完成）
