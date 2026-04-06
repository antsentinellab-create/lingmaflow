## ADDED Requirements

### Requirement: 提供 init-phase 指令從模板產生 Done Conditions
系統 SHALL 提供 `lingmaflow init-phase <phase_name>` 指令,從預定義的 YAML 模板讀取 Done Conditions 並自動填入 TASK_STATE.md。

#### Scenario: 使用內建模板初始化 Phase
- **WHEN** agent 執行 `lingmaflow init-phase phase-b-retry-budget`
- **THEN** 系統從 `templates/phases/phase-b-retry-budget.yaml` 讀取模板
- **AND** 解析 YAML 中的 done_conditions 清單
- **AND** 更新 TASK_STATE.md 的 Done Conditions 區塊
- **AND** 輸出確認訊息「✅ Phase phase-b-retry-budget 已初始化,包含 3 個 Done Conditions」

#### Scenario: 模板不存在時顯示錯誤
- **WHEN** agent 執行 `lingmaflow init-phase` 但指定的 phase_name 沒有對應模板
- **THEN** 系統顯示錯誤訊息「❌ 找不到模板: templates/phases/<phase_name>.yaml」
- **AND** 列出可用的模板清單
- **AND** 指令執行失敗,不修改 TASK_STATE.md

#### Scenario: 支援自訂模板路徑
- **WHEN** agent 執行 `lingmaflow init-phase <phase_name> --template /path/to/custom.yaml`
- **THEN** 系統從指定的自訂路徑讀取模板
- **AND** 忽略內建模板目錄
- **AND** 成功後輸出「✅ 使用自訂模板初始化 Phase」

### Requirement: Phase 模板採用標準 YAML 格式
Phase 模板 SHALL 採用統一的 YAML 結構,包含 phase_id、description、done_conditions 等欄位,每個 condition 指定 type 與 path。

#### Scenario: 標準模板結構
- **WHEN** 建立新的 Phase 模板 YAML 檔案
- **THEN** 檔案必須包含以下結構:
  ```yaml
  phase_id: phase-b-retry-budget
  description: "實作 Retry Budget 機制"
  done_conditions:
    - type: file
      path: workflow/retry_budget.py
    - type: pytest
      path: tests/test_retry_budget.py
    - type: pytest
      path: tests/
  ```
- **AND** type 支援 file、pytest、func 三種類型
- **AND** path 為相對路徑

#### Scenario: 模板驗證
- **WHEN** 載入 Phase 模板時
- **THEN** 系統驗證 YAML 結構是否符合規範
- **AND** 若缺少必要欄位 (phase_id 或 done_conditions),顯示明確錯誤
- **AND** 若 type 不支援,列出可用的 type 清單

### Requirement: 提供常用 Phase 的內建模板
系統 SHALL 在 `templates/phases/` 目錄中提供至少 3 個常用 Phase 的內建模板,作為使用者的參考範例。

#### Scenario: 列出可用模板
- **WHEN** agent 執行 `lingmaflow init-phase --list`
- **THEN** 系統列出所有可用的內建模板
- **AND** 顯示每個模板的 phase_id 與 description
- **AND** 格式為清單,方便複製貼上

#### Scenario: 內建模板包含標準 Phase
- **WHEN** 檢查 `templates/phases/` 目錄
- **THEN** 至少包含以下模板:
  - `phase-b-retry-budget.yaml`: Retry Budget 實作
  - `phase-c-rate-limiting.yaml`: Rate Limiting 實作
  - `phase-d-circuit-breaker.yaml`: Circuit Breaker 實作
- **AND** 每個模板都有完整的 Done Conditions
