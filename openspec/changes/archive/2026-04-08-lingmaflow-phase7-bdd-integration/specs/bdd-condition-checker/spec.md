## ADDED Requirements

### Requirement: BehaveConditionChecker 解析 behave: prefix
BehaveConditionChecker SHALL 識別並解析以 "behave:" 開頭的 done condition,提取 feature file 路徑。

#### Scenario: 正確解析 behave: condition
- **WHEN** done condition 為 "behave:features/fix_random_seed.feature"
- **THEN** checker 識別為 BehaveConditionChecker 類型
- **AND** feature_path 為 "features/fix_random_seed.feature"

#### Scenario: 拒絕無效的 behave: condition
- **WHEN** done condition 為 "behave:" (無路徑)
- **THEN** 回傳錯誤訊息 "Invalid behave condition: missing feature path"

### Requirement: BehaveConditionChecker 執行 behave 命令
BehaveConditionChecker SHALL 執行 `behave <feature_path>` 並根據 exit code 判斷條件是否達成。

#### Scenario: behave 全綠時條件達成
- **WHEN** features/test_passing.feature 所有 scenarios 通過
- **AND** lingmaflow verify 執行此 condition
- **THEN** ConditionResult.status 為 "pass"
- **AND** ConditionResult.message 包含 "✅ behave passed"

#### Scenario: behave 失敗時條件未達成
- **WHEN** features/test_failing.feature 有 scenario 失敗
- **AND** lingmaflow verify 執行此 condition
- **THEN** ConditionResult.status 為 "fail"
- **AND** ConditionResult.message 包含 "❌ behave failed"
- **AND** ConditionResult.message 包含 behave 的錯誤輸出

#### Scenario: behave 命令不存在時的錯誤處理
- **WHEN** behave 未安裝於系統中
- **AND** lingmaflow verify 執行 behave: condition
- **THEN** ConditionResult.status 為 "fail"
- **AND** ConditionResult.message 包含 "behave command not found"
- **AND** ConditionResult.message 包含安裝指令 "pip install behave"

### Requirement: BehaveConditionChecker 在執行 behave 前驗證 feature lock
BehaveConditionChecker SHALL 在執行 behave 命令之前,先呼叫 FeatureLock.verify() 檢查 feature file hash 是否一致。

#### Scenario: Hash 不一致時立即報錯
- **WHEN** features/fix_random_seed.feature 的 hash 與 .lingmaflow/feature_locks.json 中的記錄不一致
- **AND** lingmaflow verify 執行此 condition
- **THEN** ConditionResult.status 為 "fail"
- **AND** ConditionResult.message 包含 "has been modified"
- **AND** ConditionResult.message 包含 expected 與 actual hash
- **AND** 不執行 behave 命令

#### Scenario: Hash 一致時繼續執行 behave
- **WHEN** features/fix_random_seed.feature 的 hash 與記錄一致
- **AND** lingmaflow verify 執行此 condition
- **THEN** 通過 hash 驗證
- **AND** 繼續執行 behave 命令

### Requirement: BehaveConditionChecker 整合至 condition_checker.py
BehaveConditionChecker SHALL 註冊於 ConditionCheckerFactory,支援 "behave:" prefix 的自動路由。

#### Scenario: Factory 正確建立 BehaveConditionChecker
- **WHEN** ConditionCheckerFactory.create("behave:features/test.feature")
- **THEN** 回傳 BehaveConditionChecker 實例
- **AND** checker.feature_path 為 "features/test.feature"
