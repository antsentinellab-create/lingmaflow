# LingmaFlow

## Agentic Development Framework

**LingmaFlow — AI Agent 工作流管理工具**

解決三個核心問題：
- ❌ **Agent 中斷後迷路** - 重新開始時不知道從哪裡繼續
- ❌ **跨 Session 進度消失** - 每次都要重新說明上下文
- ❌ **Done Condition 無法自動驗證** - 主觀判斷「什麼叫做完成」

---

## 簡介 Introduction

LingmaFlow 提供完整的 AI Agent 工作流管理，包含：
- ✅ **任務狀態追蹤** - 明確的當前步驟、狀態、下一步
- ✅ **技能註冊系統** - 自動發現和管理技能（SKILL.md）
- ✅ **執行引擎** - 自動驗證 Done Conditions 並推進（v0.2.0+）
- ✅ **防迷路設計** - AGENTS.md 注入執行規則
- ✅ **OpenSpec 整合** - 與 spec-driven 開發流程無縫接軌（v0.2.1+）
- ✅ **雙層狀態顯示** - `lingmaflow status` 同時顯示 Phase + task 進度（v0.4.0+）
- ✅ **自動 prepare** - `checkpoint` 成功後自動更新 current_task.md（v0.4.0+）
- ✅ **Phase 模板** - `lingmaflow init-phase` 快速初始化 Done Conditions（v0.4.0+）

### 核心優勢 Core Benefits

**中文**：
LingmaFlow 是一個輕量級的 AI Agent 工作流管理框架，專注於解決 AI 輔助開發中的上下文管理和進度追蹤問題。通過結構化的任務狀態管理和自動化驗證機制，確保 AI Agent 能夠持續、高效地推進複雜開發任務。

**English**:
LingmaFlow is a lightweight AI Agent workflow management framework, focusing on solving context management and progress tracking issues in AI-assisted development. Through structured task state management and automated verification mechanisms, it ensures AI Agents can continuously and efficiently advance complex development tasks.

---

## 安裝 Installation

### 系統需求 Requirements

- Python 3.11+
- pip
- Git（推薦，用於版本控制）

### 從原始碼安裝 Install from Source

```bash
# 克隆倉庫 Clone repository
git clone https://github.com/your-org/lingmaflow.git
cd lingmaflow

# 建立虛擬環境 Create virtual environment（推薦）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安裝開發模式 Install in development mode
pip install -e ".[dev]"

# 驗證安裝 Verify installation
lingmaflow --version
```

### 常見安裝問題 Common Installation Issues

#### 問題 1: build-backend 錯誤

**症狀**:
```
pip install -e ".[dev]" 失敗
BackendUnavailable: Cannot import 'setuptools.backends.legacy'
```

**解決方案**:
檢查 `pyproject.toml` 的 `[build-system]` 區塊，確保使用正確的 backend:
```toml
[build-system]
build-backend = "setuptools.build_meta"
```

#### 問題 2: 多個頂層 package 導致安裝失敗

**症狀**:
```
error: Multiple top-level packages discovered in a flat-layout
```

**解決方案**:
在 `pyproject.toml` 加入明確指定:
```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["lingmaflow*"]
```

#### 問題 3: lingmaflow 在 AI-Factory venv 中找不到

**症狀**:
```
bash: lingmaflow：指令找不到
```

**原因**:
lingmaflow 只安裝在自己的 venv，沒有安裝到 AI-Factory 的 venv

**解決方案**:
在 AI-Factory 的 venv 中安裝 lingmaflow:
```bash
pip install -e ~/Applications/lingmaflow
```

---

## 快速開始 Quick Start (5 分鐘上手)

### Step 1: 初始化專案 Initialize Project

```bash
# 建立新專案目錄
mkdir my-ai-project
cd my-ai-project

# 初始化 LingmaFlow
lingmaflow init --path .
```

這會建立以下結構:
```
my-ai-project/
├── skills/              # 技能定義目錄
│   └── */SKILL.md      # 技能定義檔案
├── .lingma/            # Agent 配置目錄
│   └── agents/         # Agent 配置
├── .lingmaflow/        # LingmaFlow 工作目錄
│   └── current_task.md # 當前任務簡報
├── TASK_STATE.md       # 任務狀態檔案
└── AGENTS.md          # Agent 執行規則
```

### Step 2: 準備任務 Prepare Task

```bash
lingmaflow prepare
```

這會讀取 `TASK_STATE.md` 並生成 `.lingmaflow/current_task.md`,包含:
- 當前步驟說明
- 下一步指導
- Done Conditions 清單
- 匹配的 Skill 參考

### Step 3: AI Agent 執行任務 Agent Execution

AI Agent 根據 `.lingmaflow/current_task.md` 執行任務。例如:

```bash
# 使用 OpenSpec 進行 spec-driven 開發
/openspec-apply-change my-feature

# 或使用其他 AI Agent 工具
# Agent 會自動讀取 current_task.md 並執行對應任務
```

### Step 4: 驗證條件 Verify Conditions

```bash
lingmaflow verify
```

輸出範例:
```
✅ file:lingmaflow/core/task_state.py
✅ pytest:tests/test_task_state.py
❌ func:lingmaflow.core.TaskStateManager
   Attribute not found in module
```

### Step 5: 推進步驟 Advance to Next Step

```bash
# 如果 verify 全部通過，使用 checkpoint 自動推進
lingmaflow checkpoint STEP-02 "All tests passed"

# 或手動推進（即使條件未完全達成）
lingmaflow advance STEP-02 "Implementation complete"
```

### Step 6: 查看狀態 Check Status

```bash
lingmaflow status
```

輸出範例:
```
Current Step: STEP-03
Status: IN_PROGRESS
Next Step: Implement API endpoints

Unresolved Issues (0):
  (none)

Done Conditions (3/3):
  ✅ file:src/main.py
  ✅ pytest:tests/
  ✅ func:app.create_app
```

---

## 核心概念 Core Concepts

### 1. 任務狀態管理 Task State Management

LingmaFlow 使用 `TASK_STATE.md` 作為單一事實來源（Single Source of Truth）:

```markdown
# Task State

## Current Step
STEP-02

## Status
IN_PROGRESS

## Next Step
Implement core functionality

## Unresolved Issues
(空或列出阻礙問題)

## Done Conditions
- [ ] file:src/main.py
- [ ] pytest:tests/test_main.py
- [ ] func:app.create_app

## Last Result
上一步結果：Your result description here
```

#### 狀態流转 State Transitions

```
NOT_STARTED → IN_PROGRESS → BLOCKED → IN_PROGRESS → DONE
                     ↓                ↑
                 (verify)        (resolve)
```

### 2. Done Conditions（完成條件）

Done Conditions 是細粒度的完成標準，使用 Markdown checkbox 語法:

```markdown
## Done Conditions

- [ ] file:src/main.py           # 檔案存在性檢查
- [ ] pytest:tests/              # Pytest 測試驗證
- [ ] func:app.create_app        # 函式/類別存在檢查
```

#### 三種驗證類型 Three Verification Types

**1. `file:PATH` - 檔案存在性檢查**

驗證指定路徑的檔案是否存在。

```markdown
- [ ] file:src/main.py
- [ ] file:docs/api.md
- [ ] file:config/settings.yaml
```

**2. `pytest:PATH` - Pytest 測試驗證**

執行 pytest 並驗證所有測試通過（exit code = 0）。

```markdown
- [ ] pytest:tests/test_auth.py
- [ ] pytest:tests/               # 驗證整個目錄
- [ ] pytest:tests/unit/
```

**3. `func:MODULE.CLASS` - 函式/類別存在檢查**

使用 `importlib` 驗證模組和屬性存在。

```markdown
- [ ] func:lingmaflow.core.TaskStateManager
- [ ] func:myapp.models.User
- [ ] func:flask.Flask
```

#### 驗證機制 Verification Mechanics

- ✅ `[x]` - 條件已達成
- ❌ `[ ]` - 條件未達成
- `lingmaflow verify` 自動檢查所有條件
- `lingmaflow checkpoint` 在全部通過時自動推進

### 3. Agents.md 注入規則 AGENTS.MD Injection Rules

LingmaFlow 通過 `AGENTS.md` 文件向 AI Agent 注入執行規則:

```markdown
# 每次啟動必做

1. 執行：cat TASK_STATE.md
2. 確認「當前步驟」與「狀態」
3. 從未完成的 done condition 開始工作
4. 不重做已完成步驟

# Done Condition 規則

每個步驟必須全部達成才能推進：
- 對應檔案存在
- pytest 全綠
- TASK_STATE.md 已更新

# 錯誤處置

- 測試失敗：只修當前步驟，不往前推進
- 工具失敗：記錄到 TASK_STATE.md 未解決問題，停止等待
- 修正超過 3 次仍失敗：停止，標記 BLOCKED
```

### 4. 技能註冊系統 Skill Registry

技能定義位於 `skills/*/SKILL.md`,採用 YAML Frontmatter + Markdown Body 格式:

```yaml
---
name: test-driven-development
version: 1.0.0
triggers:
  - "test"
  - "pytest"
  - "TDD"
priority: high
---
```

#### 五大核心技能 Five Core Skills

1. **brainstorming** - 需求釐清與設計討論
2. **writing-plans** - 任務拆解與計劃撰寫
3. **test-driven-development** - 測試驅動開發
4. **systematic-debugging** - 系統化除錯
5. **subagent-driven** - 計劃執行與任務管理

#### 技能查詢 Skill Queries

```bash
# 列出所有技能
lingmaflow skill list

# 搜尋特定技能
lingmaflow skill find pytest

# 輸出範例
Found 1 skill(s) matching "pytest":

1. test-driven-development (v1.0.0)
   Triggers: test, pytest, TDD
   Priority: high
```

---

## CLI 命令參考 Command Reference

### 任務管理 Task Management

| Command | Description | Example |
|---------|-------------|---------|
| `init` | Initialize project | `lingmaflow init --path ./my-project` |
| `status` | Display current state | `lingmaflow status` |
| `advance` | Advance to next step | `lingmaflow advance STEP-02 "Completed"` |
| `block` | Mark task as blocked | `lingmaflow block "Waiting for API key"` |
| `resolve` | Resolve blocking issue | `lingmaflow resolve 1` |

#### `lingmaflow init` - 初始化專案

```bash
# 初始化新專案
lingmaflow init --path ./my-project

# 選項
--path PATH     專案路徑（必填）
--force         覆蓋現有檔案
```

#### `lingmaflow status` - 顯示當前狀態

```bash
lingmaflow status

# 輸出範例
Current Step: STEP-03
Status: IN_PROGRESS
Next Step: Implement API endpoints

Unresolved Issues (0):
  (none)

Done Conditions (3/3):
  ✅ file:src/main.py
  ✅ pytest:tests/
  ✅ func:app.create_app

Last Result: All tests passed
```

#### `lingmaflow advance` - 推進到下一步

```bash
# 推進步驟並附加結果
lingmaflow advance STEP-02 "Implementation complete"

# 選項
step_id      步驟 ID（如 STEP-02）
result       上一步結果描述（選填）
```

#### `lingmaflow block` - 標記為受阻

```bash
# 標記任務為受阻狀態
lingmaflow block "Waiting for API key from client"

# 選項
reason    受阻原因（必填）
```

#### `lingmaflow resolve` - 解決受阻問題

```bash
# 解決編號 1 的問題
lingmaflow resolve 1

# 選項
issue_id    問題編號（從 TASK_STATE.md 獲取）
```

### 技能查詢 Skill Queries

| Command | Description | Example |
|---------|-------------|---------|
| `skill list` | List all skills | `lingmaflow skill list` |
| `skill find` | Find skill by keyword | `lingmaflow skill find pytest` |

#### `lingmaflow skill list` - 列出所有技能

```bash
lingmaflow skill list

# 輸出範例
Available skills (5):

1. brainstorming (v1.0.0)
   Triggers: brainstorm, design, architecture
   Priority: high

2. writing-plans (v1.0.0)
   Triggers: plan, task, breakdown
   Priority: high
...
```

#### `lingmaflow skill find` - 搜尋技能

```bash
lingmaflow skill find pytest

# 輸出範例
Found 1 skill(s) matching "pytest":

1. test-driven-development (v1.0.0)
   Triggers: test, pytest, TDD
   Priority: high
```

### AGENTS.md 管理

| Command | Description | Example |
|---------|-------------|---------|
| `agents generate` | Generate AGENTS.md | `lingmaflow agents generate --force` |

#### `lingmaflow agents generate` - 生成 AGENTS.md

```bash
# 生成 AGENTS.md
lingmaflow agents generate

# 選項
--force     覆蓋現有 AGENTS.md
```

### 執行引擎 Execution Engine (v0.2.0+)

| Command | Description | Example |
|---------|-------------|---------|
| `prepare` | Generate task brief | `lingmaflow prepare` |
| `verify` | Verify done conditions | `lingmaflow verify` |
| `checkpoint` | Auto-advance if verified | `lingmaflow checkpoint STEP-02 --commit` |

#### `lingmaflow prepare` - 準備任務簡報

```bash
lingmaflow prepare

# 生成 .lingmaflow/current_task.md
# 包含：
# - 當前步驟
# - 下一步說明
# - Done Conditions 清單
# - 匹配的 Skill 參考
```

#### `lingmaflow verify` - 驗證完成條件

```bash
lingmaflow verify

# 輸出範例
✅ file:lingmaflow/core/task_state.py
✅ pytest:tests/test_task_state.py
❌ func:lingmaflow.core.TaskStateManager
   Attribute not found in module

# 返回碼
0 - 所有條件通過
1 - 有條件未通過
```

#### `lingmaflow checkpoint` - 檢查點並自動推進

```bash
# 驗證並自動推進（如果全部通過）
lingmaflow checkpoint STEP-02 "All tests passed"

# 選項
step_id         步驟 ID（必填）
--result TEXT   結果描述（選填）
--commit        自動提交 git（如果可用）
--no-commit     不提交 git（預設）
```

**注意**: `checkpoint` 命令的行為:
1. 執行 `verify` 檢查所有 Done Conditions
2. 如果全部通過，自動調用 `advance` 推進到下一步
3. 如果有未通過的條件，顯示錯誤並停止

---

## 與 OpenSpec 整合使用 Integration with OpenSpec

LingmaFlow v0.2.1+ 支援與 OpenSpec 的 spec-driven 開發流程無縫整合。

### 什麼是 OpenSpec? What is OpenSpec?

OpenSpec 是一個規範驅動的開發框架，通過以下 artifacts 管理變更:
- `proposal.md` - 變更提案（為什麼要做）
- `design.md` - 技術設計（如何做）
- `specs/**/*.md` - 詳細規格（做什麼）
- `tasks.md` - 實施任務清單（具体步驟）

### 標準工作流程 Standard Workflow

#### Phase 1: 創建變更提案 Create Change Proposal

```bash
# 使用 skill 創建變更
/openspec-propose my-feature

描述：
  目標：實現新功能 X
  語言：中英雙語
  重點：包含 API 變更和測試策略
```

這會創建:
```
openspec/changes/my-feature/
├── proposal.md
├── design.md
├── specs/
│   └── feature-x/
│       └── spec.md
└── tasks.md
```

#### Phase 2: 實施變更 Implement Change

```bash
# 應用變更提案
/openspec-apply-change my-feature
```

AI Agent 會:
1. 讀取 `tasks.md` 了解任務清單
2. 按照任務順序實施代碼
3. 每完成一個任務，更新 `tasks.md` 的 checkbox
4. 所有任務完成後，提示歸檔

#### Phase 3: 結合 LingmaFlow 驗證 Verify with LingmaFlow

在每個 Step 完成後，執行:

```bash
# 1. Agent 完成 Step X
/openspec-apply-change my-feature  # Step 1 完成

# 2. 停止，等待人工驗證
# Agent 輸出："Step 1 完成，等待驗證"

# 3. 人工執行 LingmaFlow 驗證
lingmaflow verify

# 4. 如果通過，推進到下一步
lingmaflow checkpoint STEP-02 "Step 1 completed"

# 5. 繼續下一個 Step
/openspec-apply-change my-feature  # Step 2
```

### 強制規則 Mandatory Rules

當結合 OpenSpec 使用時，AI Agent 必須遵守:

```markdown
## 強制規則

每個 Step 完成後必須停止
不得自行繼續下一步
等待人工執行 lingmaflow verify

完成後停止，輸出「Step X 完成，等待驗證」
不要自行繼續下一步
```

### 完整範例 Complete Example

以下是實現 LLM Gateway 功能的完整流程:

#### Step 0: 準備任務

```bash
# 1. 初始化 LingmaFlow
lingmaflow init --path .

# 2. 準備任務簡報
lingmaflow prepare

# 3. 查看當前任務
cat .lingmaflow/current_task.md
```

#### Step 1: 創建變更提案

```bash
/openspec-propose llm-gateway

描述：
  目標：實現 LLM Gateway 抽象層
  語言：中英雙語
  重點：支援多種 LLM provider（OpenAI, Anthropic, Local）
```

#### Step 2: 實施第一個 Step

```bash
/openspec-apply-change llm-gateway

# Agent 實施:
# - 任務 1.1: 創建 gateway 目錄結構
# - 任務 1.2: 實現 base gateway class
# - 任務 1.3: 添加基礎測試

# 完成後輸出:
# "Step 1 完成，等待驗證"
```

#### Step 3: 驗證並推進

```bash
# 1. 驗證 Done Conditions
lingmaflow verify

# 輸出:
# ✅ file:gateway/llm_gateway.py
# ✅ pytest:tests/test_llm_gateway.py
# ✅ func:gateway.LLMGateway

# 2. 推進到下一步
lingmaflow checkpoint STEP-02 "Step 1 verified"

# 3. 更新 TASK_STATE.md
# Current Step: STEP-03
# Status: IN_PROGRESS
```

#### Step 4: 繼續實施

```bash
/openspec-apply-change llm-gateway

# Agent 實施 Step 2:
# - 任務 2.1: 實現 OpenAI provider
# - 任務 2.2: 實現 Anthropic provider
# - 任務 2.3: 實現 Local provider
```

### 最佳實踐 Best Practices

1. **小步快走**: 每個 Step 控制在 10-30 分鐘內完成
2. **及時驗證**: 每個 Step 後必須執行 `lingmaflow verify`
3. **清晰邊界**: 每個 Step 聚焦單一職責，避免耦合
4. **文檔同步**: 更新 `tasks.md` 時保持描述清晰

---

## 標準工作流程 Standard Workflow

### 完整流程圖 Complete Workflow Diagram

```
┌─────────────┐
│  Init       │
│  Project    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Prepare    │
│  Task       │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│  Agent      │────▶│  OpenSpec    │
│  Execution  │     │  Apply       │
└──────┬──────┘     └──────┬───────┘
       │                   │
       ▼                   ▼
┌─────────────┐
│  Verify     │
│  Conditions │
└──────┬──────┘
       │
       ├─────┐
       │     │
       ▼     ▼
  ✅ Pass  ❌ Fail
       │     │
       ▼     │
┌─────────────┴──┐
│  Checkpoint    │
│  Advance       │
└────────────────┘
```

### 詳細步驟 Detailed Steps

#### Step 1: 初始化專案

```bash
lingmaflow init --path ./my-project
cd ./my-project
```

這會建立:
- `skills/` - 技能定義目錄
- `.lingma/` - Agent 配置目錄
- `.lingmaflow/` - 工作目錄
- `TASK_STATE.md` - 任務狀態檔案
- `AGENTS.md` - 執行規則

#### Step 2: 準備任務

```bash
lingmaflow prepare
```

產生 `.lingmaflow/current_task.md` 包含:
- 當前步驟
- 下一步說明
- Done Conditions 清單
- 匹配的 Skill 參考

#### Step 3: Agent 執行

AI Agent 根據 `.lingmaflow/current_task.md` 執行任務。

```bash
# 使用 OpenSpec
/openspec-apply-change my-change

# 或使用其他 Agent
# Agent 自動讀取 current_task.md
```

#### Step 4: 驗證條件

```bash
lingmaflow verify
```

輸出範例:
```
✅ file:lingmaflow/core/task_state.py
✅ pytest:tests/test_task_state.py
❌ func:lingmaflow.core.TaskStateManager
   Attribute not found in module
```

#### Step 5: 推進步驟

```bash
# 如果 verify 全部通過
lingmaflow checkpoint STEP-02 "All tests passed"

# 或者手動推進
lingmaflow advance STEP-02 "Implementation complete"
```

---

## 架構說明 Architecture

### 核心模組 Core Modules

```
lingmaflow/
├── core/
│   ├── task_state.py        # 任務狀態機（State Machine）
│   ├── skill_registry.py    # 技能註冊表
│   ├── agents_injector.py   # AGENTS.md 生成器
│   └── condition_checker.py # 條件驗證器 (v0.2.0 NEW)
├── cli/
│   └── lingmaflow.py        # CLI 工具
└── skills/
    └── */SKILL.md           # 技能定義
```

#### `core/task_state.py`

任務狀態管理，提供:
- `TaskStateManager` - 載入/保存/推進任務
- `TaskStatus` - 狀態枚舉（NOT_STARTED, IN_PROGRESS, BLOCKED, DONE）
- `get_conditions()` - 解析 Done Conditions
- `mark_condition_done()` - 標記條件完成
- `all_conditions_done()` - 檢查所有條件

#### `core/skill_registry.py`

技能註冊表，提供:
- `SkillRegistry.scan()` - 掃描技能目錄
- `SkillRegistry.get()` - 獲取特定技能
- `SkillRegistry.find()` - 按關鍵字搜尋
- `SkillRegistry.list()` - 列出所有技能

#### `core/agents_injector.py`

AGENTS.md 生成器，提供:
- `AgentsInjector.generate()` - 生成內容
- `AgentsInjector.inject()` - 寫入檔案
- `AgentsInjector.update()` - 更新現有檔案

#### `core/condition_checker.py` (v0.2.0 NEW)

條件驗證器，提供:
- `ConditionChecker.check_file()` - 檢查檔案
- `ConditionChecker.check_pytest()` - 執行 pytest
- `ConditionChecker.check_func()` - 驗證模組
- `ConditionChecker.check_all()` - 批量檢查
- `ConditionChecker.all_passed()` - 快速檢查

#### `cli/lingmaflow.py`

CLI 工具，提供 8 個命令:
- `init`, `status`, `advance`, `block`, `resolve`
- `skill list`, `skill find`
- `agents generate`
- `prepare`, `verify`, `checkpoint` (v0.2.0 NEW)

#### `skills/*/SKILL.md`

技能定義檔案，包含:
- YAML Frontmatter（name, version, triggers, priority）
- Markdown Body（核心原則、執行流程、禁止行為）

五大核心技能:
- **brainstorming** - 需求釐清與設計討論
- **writing-plans** - 任務拆解與計劃撰寫
- **test-driven-development** - 測試驅動開發
- **systematic-debugging** - 系統化除錯
- **subagent-driven** - 計劃執行與任務管理

---

## 測試 Testing

### 執行所有測試 Run All Tests

```bash
pytest tests/ -v
```

### 測試覆蓋率 Test Coverage

```bash
# Run with coverage
pytest tests/ --cov=lingmaflow --cov-report=html

# View HTML report
open htmlcov/index.html
```

### 當前狀態 Current Status

- **Total Tests**: 153
- **Passing**: 153 ✅
- **Failing**: 0
- **Coverage**: ~90%

測試分佈:
- `test_task_state.py` - TaskStateManager 測試
- `test_skill_registry.py` - SkillRegistry 測試
- `test_agents_injector.py` - AgentsInjector 測試
- `test_cli.py` - CLI 命令測試
- `test_condition_checker.py` - ConditionChecker 測試 (v0.2.0 NEW)

---

## 已知問題與處理方式 Known Issues & Workarounds

### 問題 1: checkpoint result 顯示 ConditionResult 物件而非字串

**症狀 Symptoms**:
```
lingmaflow status 顯示:
Last Result: ConditionResult(passed=True, condition='pytest:...', message='...')
```

**原因 Cause**:
checkpoint 內部 for loop 使用 `result` 變數名稱，與函式參數 `result` 衝突，傳入 `advance()` 的是物件不是字串。

**解決方案 Fix**:
已在 v0.2.1 修正，for loop 改名為 `cond`。升級到最新版本即可。

```bash
pip install --upgrade lingmaflow
```

---

### 問題 2: checkpoint 後 Done Conditions 消失

**症狀 Symptoms**:
```
執行 lingmaflow checkpoint 後
TASK_STATE.md 的 ## Done Conditions 區塊被清空
下次 lingmaflow verify 顯示「無 Done Conditions」
```

**原因 Cause**:
`_format_state()` 寫入 TASK_STATE.md 時，沒有保留 `## Done Conditions` 區塊。

**解決方案 Fix**:
已在 v0.2.1 修正，`_format_state()` 會讀取原始檔案並保留該區塊。升級到最新版本即可。

**臨時解法（舊版本）Temporary Workaround (Old Versions)**:
每次 checkpoint 後手動補回 Done Conditions:

```bash
python3 -c "
content = open('TASK_STATE.md').read()
if '## Done Conditions' not in content:
    content += '\n## Done Conditions\n- [ ] pytest:tests/\n'
    open('TASK_STATE.md', 'w').write(content)
"
```

---

### 問題 3: Done Conditions 被解析為 Unresolved Issues

**症狀 Symptoms**:
```
lingmaflow status 顯示:
Unresolved Issues (2):
  1. [ ] file:gateway/llm_gateway.py
  2. [ ] pytest:tests/test_llm_gateway.py
```

**原因 Cause**:
`_parse_file()` 在讀「未解決問題」區塊時，把 Done Conditions 的 `- [ ]` 格式也當成 unresolved 讀進去。

**解決方案 Fix**:
已在 v0.2.1 修正，解析邏輯遇到 `## Done Conditions` 時切換 section。升級到最新版本即可。

---

### 問題 4: agent 不停下來等待驗證，自行繼續下一步

**症狀 Symptoms**:
```
/openspec-apply-change 跑完一個 Step
agent 沒有停下來，直接繼續下一個 Step
你無法在中間執行 lingmaflow verify
```

**原因 Cause**:
openspec-apply-change 是連續執行的，agent 不知道「每步必須等人工 verify」這個規則。

**解決方案 Fix**:
在給 agent 的指令裡明確加入停止條件:

```markdown
## 強制規則
每個 Step 完成後必須停止
不得自行繼續下一步
等待人工執行 lingmaflow verify

完成後停止，輸出「Step X 完成，等待驗證」
不要自行繼續下一步
```

在 AGENTS.md 加入強制規則。

---

### 問題 5: lingmaflow 在 AI-Factory venv 中找不到

**症狀 Symptoms**:
```
bash: lingmaflow：指令找不到
```

**原因 Cause**:
lingmaflow 只安裝在自己的 venv，沒有安裝到 AI-Factory 的 venv。

**解決方案 Fix**:
在 AI-Factory 的 venv 中安裝 lingmaflow:

```bash
pip install -e ~/Applications/lingmaflow
```

---

### 問題 6: heredoc 在 terminal 被截斷

**症狀 Symptoms**:
```
cat > file.txt << 'EOF'
...內容...
EOF
執行後內容被截斷或指令找不到
```

**原因 Cause**:
多行 heredoc 在某些終端機環境容易出現貼上問題。

**解決方案 Fix**:
改用 python3 寫入檔案，避免 heredoc:

```bash
# 方法 1: 單行
python3 -c "open('file.txt', 'w').write('內容')"

# 方法 2: 多行
python3 << 'PYEOF'
content = """..."""
open('file.txt', 'w').write(content)
PYEOF
```

---

### 問題 7: TASK_STATE.md 的 last_result 顯示 None

**症狀 Symptoms**:
```
lingmaflow status 顯示 Last Result: None
即使已執行 checkpoint 並傳入 result 字串
```

**原因 Cause**:
舊版 checkpoint 寫入了 ConditionResult 物件（問題 1），TASK_STATE.md 檔案內容已損壞，需手動修正。

**解決方案 Fix**:

```bash
python3 -c "
content = open('TASK_STATE.md').read()
content = content.replace(
    '上一步結果：ConditionResult(...)',
    '上一步結果：你的實際結果描述'
)
open('TASK_STATE.md', 'w').write(content)
"
```

**注意**: 把 `ConditionResult(...)` 換成實際的物件字串。

---

### 問題 8: pyproject.toml build-backend 錯誤

**症狀 Symptoms**:
```
pip install -e ".[dev]" 失敗
BackendUnavailable: Cannot import 'setuptools.backends.legacy'
```

**原因 Cause**:
build-backend 設定錯誤。

**解決方案 Fix**:
修改 `pyproject.toml`:

```toml
[build-system]
build-backend = "setuptools.build_meta"
```

---

### 問題 9: 多個頂層 package 導致安裝失敗

**症狀 Symptoms**:
```
error: Multiple top-level packages discovered in a flat-layout
```

**原因 Cause**:
根目錄有多個 Python package（如 lingmaflow + openspec），setuptools 無法自動判斷要打包哪個。

**解決方案 Fix**:
在 `pyproject.toml` 加入明確指定:

```toml
[tool.setuptools.packages.find]
where = ["."]
include = ["lingmaflow*"]
```

---

## Harness 系統 Resilient Harness System (v0.3.0)

### 為什麼需要 Harness？

LingmaFlow v0.2.x 有一個根本性問題：TASK_STATE.md 只記錄 PHASE 粒度的進度，當 agent 中斷後，只能靠 grep 推測做到 tasks.md 的哪一行。

Harness 系統解決這個問題，引入三層狀態架構：

| 層次 | 檔案 | 粒度 | 內容 |
|------|------|------|------|
| 第一層 | TASK_STATE.md | PHASE | 現有格式不變 |
| 第二層 | tasks.json | task（如 3.2） | JSON 格式，比 Markdown checkbox 穩定 |
| 第三層 | PROGRESS.md | session | 決策記憶，防止重複踩坑 |

### 核心概念：決策記憶

Anthropic 2025-11-26 工程文章指出，agent 中斷後最大的問題不是「不知道做到哪」，而是「不知道為什麼失敗過」，導致下一個 session 重複嘗試同樣的死路。

PROGRESS.md 強制記錄失敗嘗試：

Session 2026-04-03 14:30
完成：task 3.1, 3.2
遺留：task 3.3 開始到一半，auth module 尚未 import
失敗記錄：嘗試用 httpx 直接 retry → 和 middleware 衝突
下一步：繼續 3.3，改用 tenacity library（需版本 >=8.2）

### 為什麼用 JSON 取代 Markdown checkbox？

Anthropic 實測：agent 比較不會不當修改或刪除 JSON 條目，Markdown checkbox 容易被 agent 誤改。

tasks.json 格式：
```json
[
  {
    "id": "3.2",
    "description": "LLMGateway retry loop 整合",
    "done": true,
    "started_at": null,
    "completed_at": "2026-04-03T14:30:00Z",
    "notes": "改用 tenacity library"
  }
]
```

只允許修改 `done`、`completed_at`、`notes` 欄位，禁止修改 `id` 和 `description`。

### CLI 命令

#### 開始執行一個 openspec change
```bash
lingmaflow harness init <change_name>
```

初始化行為：
- 將現有 `tasks.md` 的 checkbox 格式轉換為 `tasks.json`
- 建立空的 `PROGRESS.md`
- 備份原始 `tasks.md` 為 `tasks.md.bak`
- 執行 git commit

#### 完成一個 task
```bash
lingmaflow harness done <task_id> --notes "關鍵決策或注意事項"
lingmaflow harness done 3.2 --change ai-factory-phase-b --notes "改用 tenacity"
```

`--notes` 建議填寫，記錄遇到的問題和選擇的方案。

#### 記錄 session（context 快滿時或主動停止前）
```bash
lingmaflow harness log \
  --change <change_name> \
  --completed "3.1,3.2" \
  --leftover "3.3 開始到一半" \
  --failed "httpx retry 和 middleware 衝突" \
  --next "繼續 3.3，注意 tenacity 版本"
```

#### 中斷後接回
```bash
lingmaflow harness resume --change <change_name>
```

輸出範例：
═══════════════════════════════
RESUME BRIEF
═══════════════════════════════
Change: ai-factory-phase-b
Resume from: task 3.3
Last completed: task 3.2
Context from last session:

task 3.3 開始到一半，auth module 尚未 import
httpx retry 和 middleware 衝突

Startup sequence:

git log --oneline -10
cat PROGRESS.md
cat tasks.json | python3 -c "..."
從 task 3.3 繼續
═══════════════════════════════
#### 查看進度
```bash
lingmaflow harness status --change <change_name>
# Change: ai-factory-phase-b
# Progress: 12/23 tasks done (52%)
# Current: task 3.3
# Last session: 2026-04-03 14:30
```

### 與 AGENTS.md 整合

執行 `lingmaflow agents generate` 後，AGENTS.md 自動包含 harness 執行規則：
```markdown
## harness 執行規則

### 開始新 session
  lingmaflow harness resume --change <change_name>
  按照 startup sequence 執行

### 完成每個 task 後（立即執行）
  lingmaflow harness done <task_id> --notes "<關鍵決策>"

### session 結束前
  lingmaflow harness log --change <change_name> \
    --completed "..." --leftover "..." \
    --failed "..." --next "..."

### 禁止行為
  不可修改 tasks.json 的 id 或 description
  不可刪除任何 task 條目
```

### 標準工作流程
開始執行：
lingmaflow harness init <change_name>
/openspec-apply-change <change_name>
每完成一個 task（agent 執行）：
lingmaflow harness done <task_id> --notes "..."
session 結束前（agent 執行）：
lingmaflow harness log --change <change_name> ...
中斷後接回：
lingmaflow harness resume --change <change_name>
→ 輸出 brief → 貼給新 session 的 agent

## 版本歷史 Version History

### v0.4.0 (Current) - 2026-04-07

**新增功能：**
- ✅ `lingmaflow status` 整合兩層狀態（Phase + task 進度同時顯示）
- ✅ `harness init` 自動寫入 `.lingmaflow/active_change`
- ✅ `lingmaflow init-phase` 指令，從模板產生 Done Conditions
- ✅ `harness resume` 整合 TASK_STATE.md Phase 資訊
- ✅ `checkpoint` 成功後自動執行 `prepare`，current_task.md 始終最新
- ✅ AGENTS.md 偵測 tasks.json 存在時自動注入 harness 強制規則
- ✅ 209 個測試全部通過

### v0.3.0 (Previous) - 2026-04-04

**新增功能：**
- ✅ Harness 系統：三層狀態架構（TASK_STATE.md + tasks.json + PROGRESS.md）
- ✅ tasks.md → tasks.json 自動轉換
- ✅ PROGRESS.md 決策記憶，防止 agent 重複踩坑
- ✅ `lingmaflow harness` 子命令群組（init/done/log/resume/status）
- ✅ `--change` 參數明確指定 change，不依賴環境變數
- ✅ AGENTS.md 模板自動注入 harness 執行規則
- ✅ 169 個測試全部通過

### v0.2.1 (Previous) - 2026-04-02

**Bug Fixes:**
- ✅ 修正 checkpoint result 顯示 ConditionResult 物件問題
- ✅ 修正 checkpoint 後 Done Conditions 消失問題
- ✅ 修正 Done Conditions 被解析為 Unresolved Issues 問題
- ✅ 改進 _format_state() 保留 Done Conditions 區塊
- ✅ 改進 _parse_file() section 切換邏輯

**Documentation:**
- ✅ 完整更新 README.md 為詳細版
- ✅ 新增 OpenSpec 整合使用章節
- ✅ 新增已知問題與處理方式章節
- ✅ 中英雙語支持

### v0.2.0 (Previous)

**新增功能：**
- ✅ Execution Engine（prepare / verify / checkpoint）
- ✅ Done Conditions 自動驗證
- ✅ ConditionChecker 模組
- ✅ 153 個測試，100% 通過

### v0.1.0

**初始功能：**
- ✅ Task Management（init / status / advance / block / resolve）
- ✅ Skill Registry（list / find）
- ✅ Agents Injector
- ✅ 基礎 CLI 工具

---

## License

MIT License

Copyright (c) 2026 LingmaFlow Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 貢獻 Contributing

歡迎提交 Issue 和 Pull Request!

### 開發環境設置 Development Setup

```bash
# Clone
git clone https://github.com/your-org/lingmaflow.git
cd lingmaflow

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

### 提交指南 Submission Guidelines

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 相關資源 Resources

- [Lingma IDE](https://lingma.aliyun.com/)
- [Superpowers Paper](https://example.com/superpowers)
- [Click Documentation](https://click.palletsprojects.com/)
- [OpenSpec Documentation](https://github.com/your-org/openspec)

---

**最後更新 Last Updated**: 2026-04-07  
**版本 Version**: v0.4.0  
**維護者 Maintainers**: LingmaFlow Team  
**作者 Authors**: antsentinellab-create
