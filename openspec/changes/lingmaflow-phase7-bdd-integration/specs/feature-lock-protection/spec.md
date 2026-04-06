## ADDED Requirements

### Requirement: FeatureLock 計算並儲存 feature file hash
FeatureLock SHALL 計算指定 feature file 的 SHA256 hash,並儲存於 `.lingmaflow/feature_locks.json`。

#### Scenario: 鎖定單一 feature file
- **WHEN** 執行 `lingmaflow feature-lock features/fix_random_seed.feature`
- **THEN** 計算該檔案的 SHA256 hash
- **AND** 寫入 `.lingmaflow/feature_locks.json`: `{ "features/fix_random_seed.feature": "sha256:<hash>" }`
- **AND** 若檔案已存在則更新,不存在則新增

#### Scenario: 鎖定所有 feature files
- **WHEN** 執行 `lingmaflow feature-lock --all`
- **AND** features/ 目錄下有 3 個 .feature 檔案
- **THEN** 計算所有 3 個檔案的 SHA256 hash
- **AND** 寫入 `.lingmaflow/feature_locks.json` 包含全部 3 筆記錄

#### Scenario: 處理不存在的 feature file
- **WHEN** 執行 `lingmaflow feature-lock features/nonexistent.feature`
- **THEN** 回傳錯誤訊息 "Feature file not found: features/nonexistent.feature"
- **AND** 不修改 feature_locks.json

### Requirement: FeatureLock 驗證 feature file hash 一致性
FeatureLock SHALL 比對當前 feature file 的 hash 與 `.lingmaflow/feature_locks.json` 中的記錄是否一致。

#### Scenario: Hash 一致時驗證通過
- **WHEN** features/fix_random_seed.feature 的內容未改變
- **AND** 執行 `FeatureLock.verify("features/fix_random_seed.feature")`
- **THEN** 回傳 True
- **AND** 不產生任何錯誤訊息

#### Scenario: Hash 不一致時驗證失敗
- **WHEN** features/fix_random_seed.feature 的內容被修改
- **AND** 執行 `FeatureLock.verify("features/fix_random_seed.feature")`
- **THEN** 回傳 False
- **AND** 錯誤訊息包含 "has been modified"
- **AND** 錯誤訊息包含 expected hash (from locks file)
- **AND** 錯誤訊息包含 actual hash (current file)

#### Scenario: 未鎖定的 feature file 視為通過
- **WHEN** features/new_feature.feature 不存在於 feature_locks.json
- **AND** 執行 `FeatureLock.verify("features/new_feature.feature")`
- **THEN** 回傳 True (不阻擋未鎖定的檔案)
- **AND** 可選擇性警告 "Feature file not locked: features/new_feature.feature"

### Requirement: FeatureLock 檔案格式與位置
FeatureLock SHALL 使用 JSON 格式儲存於 `.lingmaflow/feature_locks.json`,支援手動編輯。

#### Scenario: 正確的 JSON 結構
- **WHEN** 讀取 `.lingmaflow/feature_locks.json`
- **THEN** 格式為 `{ "<path>": "sha256:<hex>", ... }`
- **AND** 所有路徑為相對路徑（相對於專案根目錄）
- **AND** 所有 hash 以 "sha256:" 開頭

#### Scenario: 處理損毀的 JSON 檔案
- **WHEN** `.lingmaflow/feature_locks.json` 內容為無效 JSON
- **AND** 執行 `FeatureLock.verify()` 或 `FeatureLock.lock()`
- **THEN** 回傳明確錯誤訊息 "Invalid feature_locks.json format"
- **AND** 建議重新執行 `lingmaflow feature-lock --all`

### Requirement: FeatureLock CLI 指令整合
FeatureLock SHALL 提供 `lingmaflow feature-lock` 與 `lingmaflow feature-verify` CLI 指令。

#### Scenario: feature-lock 單一檔案
- **WHEN** 使用者執行 `lingmaflow feature-lock features/test.feature`
- **THEN** 呼叫 FeatureLock.lock("features/test.feature")
- **AND** 顯示成功訊息 "Locked features/test.feature (sha256:abc123...)"

#### Scenario: feature-lock 所有檔案
- **WHEN** 使用者執行 `lingmaflow feature-lock --all`
- **THEN** 掃描 features/ 目錄下所有 .feature 檔案
- **AND** 逐一鎖定每個檔案
- **AND** 顯示摘要 "Locked 6 feature files"

#### Scenario: feature-verify 單一檔案
- **WHEN** 使用者執行 `lingmaflow feature-verify features/test.feature`
- **THEN** 呼叫 FeatureLock.verify("features/test.feature")
- **AND** 若通過顯示 "✅ features/test.feature verified"
- **AND** 若失敗顯示 "❌ features/test.feature modified" 與 hash 差異
