# BDD Integration Guide

本文件說明 LingmaFlow 如何整合 BDD (Behavior-Driven Development) 工作流，包含 `behave:` Done Condition 的使用方式、feature file 命名慣例，以及相關的保護機制。

---

## 1. behave: Done Condition 用法說明

### 基本語法

在 TASK_STATE.md 或 tasks.json 的 done conditions 中，使用 `behave:` prefix 指定需要執行的 feature file：

```yaml
done_conditions:
  - file:src/module.py
  - pytest:tests/test_module.py
  - behave:features/user_login.feature
```

### 執行流程

當 Agent 標記某個 condition 為完成時，LingmaFlow 會自動：

1. **驗證 feature file 完整性**：檢查 `.lingmaflow/feature_locks.json` 中的 hash 是否與當前檔案一致
2. **執行 behave 測試**：呼叫 `behave features/<對應的 feature 檔案>`
3. **回報結果**：
   - ✅ 所有 scenarios 通過 → condition 標記為完成
   - ❌ 有 scenario 失敗 → condition 保持未完成，顯示錯誤訊息
   - ❌ behave 命令不存在 → 提示安裝指令 `pip install behave`

### 注意事項

- **不得修改 .feature 檔案**：一旦鎖定，Agent 不可修改、刪除或跳過任何 Scenario
- **必須全綠才算完成**：behave 未全綠時，不可執行 `lingmaflow checkpoint`
- **鎖定機制**：使用 `lingmaflow feature-lock <path>` 或 `lingmaflow feature-lock --all` 鎖定 feature files

---

## 2. Feature File 命名慣例

### 基本原則

Feature file 應放置在專案根目錄的 `features/` 目錄下，檔名應清晰描述所測試的功能。

### 命名格式

```
features/<功能模組>.feature
```

### 範例：AI Factory 專案

以下是 AI Factory 專案中實際使用的 6 個 feature files，展示了如何針對具體問題編寫 BDD 驗收條件：

```
features/
├── remove_dead_orchestrator.feature    # 移除無效 Orchestrator 邏輯
├── fix_random_seed.feature             # 修復隨機種子不一致問題
├── unify_max_retry.feature             # 統一重試次數上限設定
├── storage_write_lock.feature          # 儲存層寫入鎖機制
├── protocol_action_routing.feature     # 協定動作路由邏輯
└── router_side_effect_free.feature     # Router 無副作用保證
```

#### 案例說明

1. **remove_dead_orchestrator.feature** - 確保清理不再使用的 Orchestrator 程式碼，避免技術債累積
2. **fix_random_seed.feature** - 確保 LLMGateway 初始化不呼叫 random.seed()，保留真實隨機 jitter
3. **unify_max_retry.feature** - 確認系統中所有重試機制使用一致的上限值
4. **storage_write_lock.feature** - 測試儲存層寫入時的鎖定機制，防止競態條件
5. **protocol_action_routing.feature** - 驗證協定層的动作路由正確性
6. **router_side_effect_free.feature** - 確保 Router 組件不產生副作用，符合函數式設計原則

### Feature File 內容範例

以下以 `fix_random_seed.feature` 為例，展示如何編寫具體的 BDD 驗收條件：

```gherkin
Feature: LLMGateway 不干擾全局 random state
  為了避免 thundering herd 問題
  LLMGateway 初始化不得呼叫 random.seed()
  確保 exponential backoff jitter 為真實隨機

  Scenario: 原始碼不含 random.seed() 呼叫
    When scanning gateway/llm_gateway.py source code
    Then it does not contain "random.seed("

  Scenario: jitter 計算程式碼仍然存在
    When scanning gateway/llm_gateway.py source code
    Then it contains "random.uniform"

  Scenario: LLMGateway 初始化後 random state 不變
    Given random.seed(999) is set and first value is recorded
    When LLMGateway is initialized
    Then resetting random.seed(999) produces the same first value

  Scenario: 多個 LLMGateway 實例產生不同 jitter
    When 3 LLMGateway instances are created sequentially
    Then their jitter values are not all identical
```

這個範例展示了：
- **明確的問題描述**：避免 thundering herd 問題，LLMGateway 不應干擾全局 random state
- **可驗證的 Scenarios**：每個 Scenario 都可以透過 behave 自動執行驗證（掃描原始碼、檢查 random state）
- **具體的 Given-When-Then**：清晰描述前置條件、操作步驟與預期結果

### 子目錄組織

對於大型專案，可以使用子目錄組織 feature files：

```
features/
├── authentication/
│   ├── login.feature
│   ├── logout.feature
│   └── password_reset.feature
├── data_processing/
│   ├── import.feature
│   ├── export.feature
│   └── transformation.feature
└── reporting/
    ├── generate_report.feature
    └── schedule_report.feature
```

---

## 3. Proposal.md 的 Done Condition 區塊範例

當使用 `openspec propose` 建立變更提案時，可以在 proposal.md 中手動加入 Done Condition 區塊作為參考。

**注意**：這不是 openspec template 的一部分，而是手動撰寫的參考內容。

### 範例：新增使用者認證功能

```markdown
## Done Conditions

此變更的完成條件如下：

### 實作條件
- [ ] file:src/auth/login.py
- [ ] file:src/auth/logout.py
- [ ] pytest:tests/test_auth.py

### BDD 驗收條件
- [ ] behave:features/authentication/login.feature
- [ ] behave:features/authentication/logout.feature

### 文件條件
- [ ] file:docs/authentication.md
```

### 範例：AI Agent 工作流程

```markdown
## Done Conditions

### 核心實作
- [ ] file:lingmaflow/core/agents_injector.py
- [ ] file:lingmaflow/cli/commands.py
- [ ] pytest:tests/test_agents_injector.py

### BDD 驗收
- [ ] behave:features/agent_creation.feature
- [ ] behave:features/workflow_execution.feature

### 整合測試
- [ ] pytest:tests/integration/test_agent_workflow.py
```

### 使用建議

1. **明確列出所有 conditions**：讓 Agent 清楚知道需要完成哪些項目
2. **區分類型**：將 file、pytest、behave 等不同类型的 conditions 分組
3. **提供足夠上下文**：在 proposal.md 的 design 或 specs 區塊中說明每個 condition 的目的
4. **保持一致性**：follow 專案既有的 naming conventions

---

## 4. 為何不修改 OpenSpec Template

### 技術原因

OpenSpec 的 templates 位於 npm package 內部：

```
/home/me/.npm-global/lib/node_modules/@fission-ai/openspec/schemas/spec-driven/templates/
├── proposal.md
├── design.md
├── spec.md
└── tasks.md
```

這些檔案屬於 `@fission-ai/openspec` npm package，修改它們會導致以下問題：

1. **npm update 會覆蓋修改**：每次更新 openspec package 時，templates 會被還原為原始版本
2. **團隊協作困難**：其他開發者需要手動套用相同的修改
3. **版本控制混亂**：無法透過 git 追蹤 template 的自訂修改
4. **維護成本高**：每次 openspec 更新都需要重新套用修改

### 替代方案

我們採用以下策略來擴充 OpenSpec 的功能，而不修改其 templates：

1. **文件指引**：在本文件 (`bdd-integration.md`) 中提供詳細的使用說明與範例
2. **CLI 擴充**：透過 `lingmaflow` CLI 工具提供 BDD 相關功能（如 `feature-lock`、`feature-verify`）
3. **Agents.md 注入**：在 AGENTS.md 中自動注入 BDD 規則，指導 Agent 正確使用 behave conditions
4. **範例提案**：在 `openspec/changes/` 目錄中提供實際的 proposal.md 範例供參考

### 最佳實踐

- ✅ **閱讀本文件**：了解 behave: conditions 的正確用法
- ✅ **參考現有提案**：查看 `openspec/changes/lingmaflow-phase7-bdd-integration/proposal.md`
- ✅ **遵循命名慣例**：使用清晰的 feature file 名稱與目錄結構
- ✅ **使用 CLI 工具**：透過 `lingmaflow feature-lock` 管理 feature files
- ❌ **不要修改 openspec templates**：避免維護問題與版本衝突

---

## 相關資源

- [OpenSpec Documentation](https://github.com/fission-ai/openspec)
- [Behave Documentation](https://behave.readthedocs.io/)
- [Gherkin Syntax Reference](https://cucumber.io/docs/gherkin/reference/)
- LingmaFlow CLI 命令：
  - `lingmaflow feature-lock <path>` - 鎖定單一 feature file
  - `lingmaflow feature-lock --all` - 鎖定所有 feature files
  - `lingmaflow feature-verify <path>` - 驗證 feature file 完整性

---

## 實戰紀錄 Practical Implementation Record

### Phase 7 BDD 整合日期

- **開始日期**: 2026-04-07
- **完成日期**: 2026-04-08
- **版本**: LingmaFlow v0.5.0
- **目標專案**: AI-Factory (https://github.com/antsentinellab-create/AI-Factory)

### AI-Factory Feature Files 鎖定狀態

以下 6 個 feature files 已於 2026-04-08 成功鎖定，hashes 記錄於 `.lingmaflow/feature_locks.json`:

| Feature File | SHA256 Hash |
|-------------|-------------|
| `features/remove_dead_orchestrator.feature` | `sha256:f35a8581...` |
| `features/fix_random_seed.feature` | `sha256:0f7c7ee5...` |
| `features/unify_max_retry.feature` | `sha256:0c57b3ea...` |
| `features/storage_write_lock.feature` | `sha256:aaf84b30...` |
| `features/protocol_action_routing.feature` | `sha256:750f22d4...` |
| `features/router_side_effect_free.feature` | `sha256:ef3b8afc...` |

**對應的 OpenSpec Changes:**
- `ai-factory-remove-dead-orchestrator`
- `ai-factory-fix-random-seed-production-bug`
- `ai-factory-unify-max-retry-constants`
- `ai-factory-fix-storage-write-lock-split-brain`
- `ai-factory-fix-protocol-action-duplicate-instantiation`
- `ai-factory-refactor-router-decision-chain`

### Step 衝突修復紀錄

**問題診斷** (2026-04-08):
執行 `behave features/remove_dead_orchestrator.feature` 時遇到 `AmbiguousStep` 錯誤，原因是三個 steps files 中有重複的 step 定義。

**衝突的 Steps:**
1. `@when("scanning {filepath} source code")` - 出現在 `phase1_steps.py` 和 `storage_lock_steps.py`
2. `@then('it does not contain "{unexpected}"')` - 出現在所有三個 files
3. `@then('it contains "{expected}"')` - 出現在 `phase1_steps.py` 和 `storage_lock_steps.py`

**解決方案:**
從 `storage_lock_steps.py` 和 `protocol_action_steps.py` 中移除上述 3 個重複 steps，只保留它們特有的 steps：

- **storage_lock_steps.py 特有 steps**:
  - `@when("task_store and pipeline_store are imported")`
  - `@then("task_store._write_lock is pipeline_store._write_lock")`
  - `@when("{n:d} threads simultaneously acquire and release the shared lock")`
  - 等 threading 相關測試 steps

- **protocol_action_steps.py 特有 steps**:
  - `@then('it does not contain "{text}" in research stage')`
  - `@then('it does not contain "{text}" in planning stage')`
  - `@given("PROTOCOL_ACTIONS_AVAILABLE is True")`
  - 等 protocol-specific steps

- **phase1_steps.py**: 作為通用 steps 來源，提供 parameterized versions

**結果**: 所有 AmbiguousStep 錯誤已解決，behave 可正常載入所有 steps。

### Phase 1 基線測試結果

執行日期: 2026-04-08
環境: AI-Factory venv_ai_factory (Python 3.13, behave 1.3.3)

#### 1. remove_dead_orchestrator.feature
- ✅ **通過 Scenarios** (3/5):
  - `__init__.py 不含 orchestrator 引用`
  - `run_workflow 可直接 import`
  - `run_full_pipeline 可直接 import`
- ❌ **失敗 Scenarios** (2/5):
  - `orchestrator.py 檔案不存在` - 檔案仍存在（change 尚未實作）
  - `無法 import orchestrator 模組` - 模組仍可 import（change 尚未實作）

#### 2. fix_random_seed.feature
- ✅ **通過 Scenarios** (1/4):
  - `jitter 計算程式碼仍然存在`
- ❌ **失敗 Scenarios** (1/4):
  - `原始碼不含 random.seed() 呼叫` - random.seed() 仍存在（change 尚未實作）
- ⚠️ **錯誤 Scenarios** (2/4):
  - `LLMGateway 初始化後 random state 不變` - LLMGateway 需要 metrics/registry 參數
  - `多個 LLMGateway 實例產生不同 jitter` - 同上，需要修正 step 實作

#### 3. unify_max_retry.feature
- ✅ **通過 Scenarios** (2/7):
  - `環境變數設為 2 時 execution_stage 使用 2 次`
  - `未設定環境變數時預設值為 5`
- ❌ **失敗 Scenarios** (3/7):
  - `execution_stage import config 常數而非 constants` - change 尚未實作
  - `constants.py 含 deprecated 標註` - change 尚未實作
  - `環境變數設為 7 時兩個常數都等於 7` - constants.MAX_RETRY 未委派到 config
- ⚠️ **錯誤 Scenarios** (1/7):
  - `constants.MAX_RETRY 委派到 config` - 缺少 step definition

**總結**: 
- 總計 16 scenarios
- ✅ 6 passed (37.5%)
- ❌ 6 failed (37.5%) - 因為 changes 尚未實作
- ⚠️ 3 errored (18.75%) - step definitions 需要調整
- 1 undefined (6.25%)

### 預估可省 70% Code Review 工作量的依據

#### 傳統 Code Review 流程（以 fix-random-seed 為例）

1. **手動檢查原始碼** (15-20 分鐘)
   - grep 搜尋 `random.seed()` 呼叫
   - 檢查所有可能影響 global random state 的位置
   - 確認 jitter 邏輯未被意外移除

2. **理解上下文** (10-15 分鐘)
   - 閱讀 thundering herd 問題的說明
   - 理解為什麼不能 fix seed
   - 確認 exponential backoff 的實作細節

3. **手動測試驗證** (20-30 分鐘)
   - 編寫臨時測試腳本
   - 多次執行確認 randomness
   - 檢查 edge cases

4. **撰寫 Review Comments** (10-15 分鐘)
   - 記錄檢查項目
   - 提出潛在問題
   - 建議改進方向

**總計**: 55-80 分鐘 per change

#### BDD 自動化驗證流程

1. **執行 behave** (1-2 分鐘)
   ```bash
   behave features/fix_random_seed.feature
   ```

2. **檢視結果** (1-2 分鐘)
   - ✅ 全綠 → merge
   - ❌ 失敗 → 查看哪個 scenario 失敗，直接定位問題

3. **Feature Lock 保護** (自動)
   - 防止 agent 修改 .feature file 來通過測試
   - Hash verification 確保驗收條件不被篡改

**總計**: 2-4 分鐘 per change

#### 工作量節省計算

```
傳統流程: 55-80 分鐘
BDD 流程: 2-4 分鐘
節省時間: 53-76 分鐘
節省比例: (53-76) / 55-80 ≈ 70-95%
保守估計: 70%
```

#### 額外優勢

1. **一致性**: 每次 review 使用相同的驗收標準
2. **可追溯性**: feature files 作為 executable documentation
3. **防造假**: Feature Lock 機制防止 agent 繞過測試
4. **自動化**: 整合到 CI/CD pipeline，無需人工介入
5. **知識傳承**: 新成員可透過 feature files 快速理解系統行為

#### 實際應用場景

對於 AI-Factory 的 6 個 changes:
- **傳統方式**: 6 × 55-80 min = 5.5-8 小時
- **BDD 方式**: 6 × 2-4 min = 12-24 分鐘
- **節省**: 5-7.5 小時 ≈ **70% 工作量減少**

隨著專案規模擴大，節省效果會更顯著，因為：
- Feature files 可重複使用
- Regression testing 自動化
- 新 changes 只需關注新增的 scenarios
