## ADDED Requirements

### Requirement: ConditionChecker 核心驗證邏輯

ConditionChecker 模組提供三種驗證類型（file, pytest, func），用於檢查 Done Conditions 是否達成。

#### Scenario: 檢查檔案存在
- **WHEN** 調用 `check_file("lingmaflow/core/task_state.py")`
- **THEN** 如果檔案存在返回 `ConditionResult(passed=True)`，否則返回 `passed=False`

#### Scenario: 檢查檔案不存在
- **WHEN** 調用 `check_file("nonexistent/file.py")`
- **THEN** 返回 `ConditionResult(passed=False, message="File not found")`

#### Scenario: 檢查 pytest 測試通過
- **WHEN** 調用 `check_pytest("tests/test_task_state.py")` 且所有測試通過
- **THEN** 返回 `ConditionResult(passed=True, message="All tests passed")`

#### Scenario: 檢查 pytest 測試失敗
- **WHEN** 調用 `check_pytest("tests/test_failing.py")` 且有測試失敗
- **THEN** 返回 `ConditionResult(passed=False, message="X tests failed")`

#### Scenario: 檢查函式/類別存在
- **WHEN** 調用 `check_func("lingmaflow.core.TaskStateManager")` 且該類別存在
- **THEN** 返回 `ConditionResult(passed=True, message="Module and attribute found")`

#### Scenario: 檢查函式不存在
- **WHEN** 調用 `check_func("nonexistent.module.Class")` 且該模組或類別不存在
- **THEN** 返回 `ConditionResult(passed=False, message="Module or attribute not found")`

#### Scenario: 檢查未知條件類型
- **WHEN** 調用 `check_all(["unknown:something"])`
- **THEN** 拋出 `UnknownConditionTypeError` 異常

#### Scenario: 批量檢查混合結果
- **WHEN** 調用 `check_all(["file:exists.py", "file:not_exists.py", "pytest:tests.py"])`
- **THEN** 返回三個 `ConditionResult`，逐一正確反映每個條件的狀態
