# agents-md-bdd-rules Specification

## Purpose
TBD - created by archiving change lingmaflow-phase7-bdd-integration. Update Purpose after archive.
## Requirements
### Requirement: AgentsInjector 偵測 features/ 目錄
AgentsInjector SHALL 在 generate() 方法中偵測專案根目錄是否存在 features/ 目錄且包含至少一個 .feature 檔案。

#### Scenario: 偵測到 features/ 目錄時注入 BDD 規則
- **WHEN** 專案根目錄存在 features/fix_random_seed.feature
- **AND** 執行 `lingmaflow agents generate`
- **THEN** 產生的 AGENTS.md 包含 "## BDD 驗收規則" 區塊
- **AND** 該區塊位於 Done Condition 規則之後

#### Scenario: 未偵測到 features/ 目錄時不注入
- **WHEN** 專案根目錄不存在 features/ 目錄
- **AND** 執行 `lingmaflow agents generate`
- **THEN** 產生的 AGENTS.md 不包含 "## BDD 驗收規則" 區塊
- **AND** 其他區塊正常產生

#### Scenario: features/ 目錄為空時不注入
- **WHEN** features/ 目錄存在但無任何 .feature 檔案
- **AND** 執行 `lingmaflow agents generate`
- **THEN** 產生的 AGENTS.md 不包含 "## BDD 驗收規則" 區塊

### Requirement: AGENTS.md BDD 規則區塊內容
AgentsInjector SHALL 在 AGENTS.md 中注入完整的 BDD 驗收規則,包含禁止行為與 behave 執行時機。

#### Scenario: 注入禁止行為規則
- **WHEN** BDD 規則區塊被注入 AGENTS.md
- **THEN** 包含以下禁止行為:
  - "不得修改 features/ 目錄下的任何 .feature 檔案"
  - "不得刪除或跳過任何 Scenario"
  - "不得新增 Scenario 來取代現有的 Scenario"
  - "behave 未全綠不得執行 lingmaflow checkpoint"

#### Scenario: 注入 behave 執行時機規則
- **WHEN** BDD 規則區塊被注入 AGENTS.md
- **THEN** 包含以下執行時機說明:
  - "Done Condition 包含 behave: 時,完成實作後立即執行: behave features/<對應的 feature 檔案>"
  - "必須全綠才算完成此條件"

#### Scenario: BDD 規則區塊格式正確
- **WHEN** BDD 規則區塊被注入 AGENTS.md
- **THEN** 使用 Markdown 標題 "## BDD 驗收規則（偵測到 features/ 目錄）"
- **AND** 禁止行為使用 "### 禁止行為" 子標題
- **AND** 執行時機使用 "### behave 執行時機" 子標題
- **AND** 所有規則項目使用列表格式 (- item)

### Requirement: BDD 規則區塊插入位置
AgentsInjector SHALL 將 BDD 規則區塊插入於 Done Condition 規則之後、錯誤處置之前。

#### Scenario: 正確的插入順序
- **WHEN** AGENTS.md 包含多個區塊
- **THEN** 區塊順序為:
  1. 每次啟動必做
  2. 可用 Skill 清單
  3. Done Condition 規則
  4. **BDD 驗收規則**（若偵測到 features/）
  5. 錯誤處置
  6. harness 執行規則

#### Scenario: 不破壞現有區塊結構
- **WHEN** BDD 規則區塊被插入
- **THEN** 原有區塊的內容不變
- **AND** 區塊之間的空行保持一致
- **AND** 不重複插入（若已存在則跳過）

### Requirement: BDD 規則區塊冪等性
AgentsInjector SHALL 確保 BDD 規則區塊不會重複注入,若已存在則跳過。

#### Scenario: 多次 generate 不重複注入
- **WHEN** 第一次執行 `lingmaflow agents generate` 注入 BDD 規則
- **AND** 第二次執行 `lingmaflow agents generate`
- **THEN** AGENTS.md 中只有一個 "## BDD 驗收規則" 區塊
- **AND** 內容未被複製或覆蓋

#### Scenario: 偵測已存在的 BDD 區塊
- **WHEN** AGENTS.md 已包含 "## BDD 驗收規則" 字串
- **AND** 執行 `lingmaflow agents generate`
- **THEN** 跳過注入步驟
- **AND** 顯示警告訊息 "BDD rules already present, skipping injection"

