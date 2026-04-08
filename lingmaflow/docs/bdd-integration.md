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
