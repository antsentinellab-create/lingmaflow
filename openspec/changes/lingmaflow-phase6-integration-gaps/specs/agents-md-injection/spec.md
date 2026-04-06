## ADDED Requirements

### Requirement: Agents Injector 偵測 tasks.json 存在性
`agents_injector.generate()` 方法 SHALL 在生成 AGENTS.md 前檢查專案根目錄是否存在 `tasks.json`,並根據結果決定是否注入 harness 規則。

#### Scenario: 偵測到 tasks.json 時注入 harness 規則
- **WHEN** agents_injector 執行 generate() 且 tasks.json 存在於專案根目錄
- **THEN** 系統從模板讀取 harness 規則區塊
- **AND** 將規則插入 AGENTS.md 的適當位置 (在「每次啟動必做」之後)
- **AND** 輸出提示「✅ 已加入 harness 執行規則」

#### Scenario: 未偵測到 tasks.json 時不注入規則
- **WHEN** agents_injector 執行 generate() 但 tasks.json 不存在
- **THEN** 系統不加入 harness 規則區塊
- **AND** AGENTS.md 保持通用格式
- **AND** 不顯示任何 harness 相關提示

#### Scenario: 注入位置精確控制
- **WHEN** 插入 harness 規則到 AGENTS.md
- **THEN** 系統尋找 `<!-- HARNESS_RULES -->` 佔位符
- **AND** 若找不到佔位符,在「## 可用 Skill 清單」章節前插入
- **AND** 確保規則出現在文件前半部,提高能見度

### Requirement: Harness 規則模板獨立維護
Harness 規則的內容 SHALL 存放在獨立的模板檔案中 (`templates/harness_rules.md.j2`),方便單獨修改而不影響主模板。

#### Scenario: 載入 harness 規則模板
- **WHEN** agents_injector 需要注入 harness 規則
- **THEN** 系統從 `templates/harness_rules.md.j2` 讀取內容
- **AND** 模板包含完整的 `## openspec 執行強制規則` 章節
- **AND** 使用 Jinja2 語法支援動態變數 (如 change_name)

#### Scenario: 模板內容包含強制指示
- **WHEN** 檢查 harness_rules.md.j2 模板
- **THEN** 模板必須包含以下關鍵元素:
  - 「每完成一個 task,立即執行 (不可跳過)」的明確指示
  - `lingmaflow harness done <task_id> --notes "<關鍵決策>"` 的範例
  - session 結束前的 harness log 指令格式
  - notes 欄位必填的說明與範例內容

### Requirement: 向後相容現有 AGENTS.md
Agents injector 的增強 SHALL 不破壞現有專案已生成的 AGENTS.md,新規則僅在新專案或重新生成時套用。

#### Scenario: 現有專案不受影響
- **WHEN** 使用者升級 lingmaflow 但未重新執行 init
- **THEN** 現有 AGENTS.md 保持不變
- **AND** 不包含新的 harness 規則
- **AND** 使用者可手動執行 `lingmaflow init --force` 重新生成

#### Scenario: 提供升級指引
- **WHEN** 使用者查詢如何更新現有專案的 AGENTS.md
- **THEN** README.md 或文件說明手動更新步驟:
  1. 備份現有 AGENTS.md
  2. 執行 `lingmaflow init --force`
  3. 比對差異,保留自訂修改
- **AND** 未來可考慮提供 `lingmaflow upgrade-agents` 自動化指令
