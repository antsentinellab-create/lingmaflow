## Why

Phase 6 診斷出「agent 達標但測試造假」的根本問題：現有的 Done Condition（file/pytest/func）只驗證結構正確性,無法確保行為正確性。AI 可以建立空檔案、讓測試驗證自己、或建空函式來通過驗證。目前依賴手動二次 code review,成本高且主觀。BDD 提供第四種驗證類型（behave:）,由使用者事先定義「做對了長什麼樣」,AI 無法透過造假程式碼讓它通過,預計可減少 70% review 工作量。

## What Changes

- **新增 behave: Done Condition 類型**：lingmaflow verify 支援執行 behave feature files,exit code = 0 表示條件達成
- **新增 features/ 目錄保護機制**：透過 SHA256 hash 鎖定 feature files,防止 agent 修改或刪除 scenarios
- **新增 CLI 指令**：`lingmaflow feature-lock` 記錄 feature file hashes,`lingmaflow feature-verify` 檢查完整性
- **更新 AGENTS.md 模板**：偵測到 features/ 目錄時自動注入 BDD 驗收規則區塊
- **更新 openspec propose 模板**：在 Done Condition 區塊加入 behave: 位置提示與命名慣例

## Capabilities

### New Capabilities
- `bdd-condition-checker`: BehaveConditionChecker 類別,解析並執行 behave: prefix 的 done conditions
- `feature-lock-protection`: Feature file hash 保護機制,包含 feature_lock.py 模組與 CLI 指令
- `agents-md-bdd-rules`: AGENTS.md 模板中自動注入 BDD 驗收規則的邏輯
- `openspec-bdd-template`: openspec propose 模板中加入 behave: 位置提示與 feature file 命名慣例

### Modified Capabilities
- `task-state-management`: _parse_done_conditions() 需支援 behave: prefix 解析
- `condition-validation`: condition_checker.py 需在執行 behave 前加入 hash 驗證邏輯

## Impact

**Affected Code**:
- `lingmaflow/core/condition_checker.py`: 新增 BehaveConditionChecker class
- `lingmaflow/core/task_state.py`: _parse_done_conditions() 支援 behave: prefix
- `lingmaflow/core/feature_lock.py`: 新建模組（hash 保護機制）
- `lingmaflow/cli/commands.py`: 新增 feature-lock 與 feature-verify 指令
- `lingmaflow/core/agents_injector.py`: generate() 方法加入 features/ 目錄偵測與 BDD 規則注入

**New Files**:
- `tests/test_behave_condition.py`: behave: 條件解析與執行測試
- `.lingmaflow/feature_locks.json`: feature file hash 記錄檔

**Dependencies**:
- 需要安裝 `behave` Python package（pip install behave）
- 不影響現有 openspec 格式或 TASK_STATE.md 格式

**Systems**:
- lingmaflow verify 流程增加 behave 驗證步驟
- ai-factory 重構案可立即使用已產出的 6 個 feature files
