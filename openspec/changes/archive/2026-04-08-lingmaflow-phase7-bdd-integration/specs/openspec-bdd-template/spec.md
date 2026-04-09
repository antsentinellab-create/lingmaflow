## ADDED Requirements

### Requirement: openspec propose 模板加入 behave: 位置提示
openspec propose 生成的 proposal.md 模板 SHALL 在「Done Condition」區塊中加入 behave: 的位置提示。

#### Scenario: Done Condition 區塊包含 behave: 提示
- **WHEN** 使用者執行 `openspec new change "test-change"`
- **AND** 查看產生的 proposal.md 模板
- **THEN** Done Condition 區塊包含以下內容:
  ```
  □ behave:features/<change_name>.feature   ← 行為驗證（若有 feature file）
  □ file:<主要產出檔案>
  □ pytest:tests/<對應測試>
  □ pytest:tests/（全套全綠）
  ```

#### Scenario: behave: 提示位於最上方
- **WHEN** Done Condition 區塊包含多種 condition 類型
- **THEN** behave: 位於第一個位置（優先執行）
- **AND** 其他 conditions (file/pytest/func) 依序排列

### Requirement: Feature File 命名慣例文件化
openspec propose 生成的 design.md 或 proposal.md SHALL 包含 feature file 命名慣例說明。

#### Scenario: 提供命名轉換規則
- **WHEN** 使用者閱讀 proposal.md 或 design.md
- **THEN** 包含以下命名規則說明:
  - "每個 change 對應一個 feature file"
  - "命名規則：去掉專案前綴（如 ai-factory-）、連字號改底線、去掉 -bug/-production 等後綴"

#### Scenario: 提供實際範例
- **WHEN** 使用者閱讀命名慣例說明
- **THEN** 包含以下範例:
  - "ai-factory-fix-random-seed-production-bug → fix_random_seed.feature"
  - "ai-factory-remove-dead-orchestrator → remove_dead_orchestrator.feature"

### Requirement: openspec propose 模板相容性
更新後的 openspec propose 模板 SHALL 保持向後相容,不破壞現有 proposal 格式。

#### Scenario: 既有 changes 不受影響
- **WHEN** 已存在的 changes (如 lingmaflow-phase6-integration-gaps)
- **THEN** 其 proposal.md 不被修改
- **AND** 仍可正常執行 `openspec apply`

#### Scenario: 新 changes 自動套用新模板
- **WHEN** 使用者執行 `openspec new change "new-change"`
- **THEN** 產生的 proposal.md 包含 behave: 提示
- **AND** 其他 sections (Why/What Changes/Capabilities/Impact) 保持原有格式

### Requirement: behave: Condition 為選擇性
openspec propose 模板 SHALL 明確標示 behave: condition 為選擇性（僅在有 feature file 時使用）。

#### Scenario: 無 BDD 需求的 change 可省略 behave:
- **WHEN** change 不涉及行為驗證需求
- **THEN** 使用者可刪除 behave: 那一行
- **AND** 保留 file:/pytest: conditions 即可通過 verify

#### Scenario: 有 BDD 需求的 change 必須包含 behave:
- **WHEN** change 對應的 spec 中有 behave: features/*.feature
- **THEN** Done Condition 必須包含該 behave: condition
- **AND** lingmaflow verify 會執行 behave 驗證
