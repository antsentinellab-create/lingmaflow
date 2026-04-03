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
- ✅ **執行引擎** - 自動驗證 Done Conditions 並推進
- ✅ **防迷路設計** - AGENTS.md 注入執行規則

---

## 安裝 Installation

### 系統需求
- Python 3.11+
- pip

### 從原始碼安裝

```bash
# Clone repository
git clone https://github.com/your-org/lingmaflow.git
cd lingmaflow

# Install in development mode
pip install -e ".[dev]"
```

### 驗證安裝

```bash
lingmaflow --version
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

### 技能查詢 Skill Queries

| Command | Description | Example |
|---------|-------------|---------|
| `skill list` | List all skills | `lingmaflow skill list` |
| `skill find` | Find skill by keyword | `lingmaflow skill find pytest` |

### AGENTS.md 管理

| Command | Description | Example |
|---------|-------------|---------|
| `agents generate` | Generate AGENTS.md | `lingmaflow agents generate --force` |

### 執行引擎 Execution Engine (NEW in v0.2.0)

| Command | Description | Example |
|---------|-------------|---------|
| `prepare` | Generate task brief | `lingmaflow prepare` |
| `verify` | Verify done conditions | `lingmaflow verify` |
| `checkpoint` | Auto-advance if verified | `lingmaflow checkpoint STEP-02 --commit` |

---

## 標準工作流程 Standard Workflow

### Step 1: 初始化專案

```bash
lingmaflow init --path ./my-project
cd ./my-project
```

這會建立：
- `skills/` - 技能定義目錄
- `.lingma/` - Agent 配置目錄
- `TASK_STATE.md` - 任務狀態檔案
- `AGENTS.md` - 執行規則

### Step 2: 準備任務

```bash
lingmaflow prepare
```

產生 `.lingmaflow/current_task.md` 包含：
- 當前步驟
- 下一步說明
- Done Conditions 清單
- 匹配的 Skill 參考

### Step 3: Agent 執行

AI Agent 根據 `.lingmaflow/current_task.md` 執行任務。

### Step 4: 驗證條件

```bash
lingmaflow verify
```

輸出範例：
```
✅ file:lingmaflow/core/task_state.py
✅ pytest:tests/test_task_state.py
❌ func:lingmaflow.core.TaskStateManager
   Attribute not found in module
```

### Step 5: 推進步驟

```bash
# 如果 verify 全部通過
lingmaflow checkpoint STEP-02 "All tests passed"

# 或者手動推進
lingmaflow advance STEP-02 "Implementation complete"
```

---

## Done Conditions 格式

Done Conditions 是細粒度的完成標準，使用 Markdown checkbox 語法：

```markdown
## Done Conditions

- [ ] file:lingmaflow/core/task_state.py
- [ ] pytest:tests/test_task_state.py
- [ ] func:lingmaflow.core.TaskStateManager
```

### 三種驗證類型

#### 1. `file:PATH` - 檔案存在性檢查

驗證指定路徑的檔案是否存在。

```markdown
- [ ] file:src/main.py
- [ ] file:docs/api.md
```

#### 2. `pytest:PATH` - Pytest 測試驗證

執行 pytest 並驗證所有測試通過。

```markdown
- [ ] pytest:tests/test_auth.py
- [ ] pytest:tests/
```

#### 3. `func:MODULE.CLASS` - 函式/類別存在檢查

使用 `importlib` 驗證模組和屬性存在。

```markdown
- [ ] func:lingmaflow.core.TaskStateManager
- [ ] func:myapp.models.User
```

### 驗證機制

- ✅ `[x]` - 條件已達成
- ❌ `[ ]` - 條件未達成
- `lingmaflow verify` 自動檢查所有條件
- `lingmaflow checkpoint` 在全部通過時自動推進

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

任務狀態管理，提供：
- `TaskStateManager` - 載入/保存/推進任務
- `TaskStatus` - 狀態枚舉（NOT_STARTED, IN_PROGRESS, BLOCKED, DONE）
- `get_conditions()` - 解析 Done Conditions
- `mark_condition_done()` - 標記條件完成
- `all_conditions_done()` - 檢查所有條件

#### `core/skill_registry.py`

技能註冊表，提供：
- `SkillRegistry.scan()` - 掃描技能目錄
- `SkillRegistry.get()` - 獲取特定技能
- `SkillRegistry.find()` - 按關鍵字搜尋
- `SkillRegistry.list()` - 列出所有技能

#### `core/agents_injector.py`

AGENTS.md 生成器，提供：
- `AgentsInjector.generate()` - 生成內容
- `AgentsInjector.inject()` - 寫入檔案
- `AgentsInjector.update()` - 更新現有檔案

#### `core/condition_checker.py` (v0.2.0 NEW)

條件驗證器，提供：
- `ConditionChecker.check_file()` - 檢查檔案
- `ConditionChecker.check_pytest()` - 執行 pytest
- `ConditionChecker.check_func()` - 驗證模組
- `ConditionChecker.check_all()` - 批量檢查
- `ConditionChecker.all_passed()` - 快速檢查

#### `cli/lingmaflow.py`

CLI 工具，提供 8 個命令：
- `init`, `status`, `advance`, `block`, `resolve`
- `skill list`, `skill find`
- `agents generate`
- `prepare`, `verify`, `checkpoint` (v0.2.0 NEW)

#### `skills/*/SKILL.md`

技能定義檔案，包含：
- YAML Frontmatter（name, version, triggers, priority）
- Markdown Body（核心原則、執行流程、禁止行為）

五大核心技能：
- **brainstorming** - 需求釐清與設計討論
- **writing-plans** - 任務拆解與計劃撰寫
- **test-driven-development** - 測試驅動開發
- **systematic-debugging** - 系統化除錯
- **subagent-driven** - 計劃執行與任務管理

---

## 測試 Testing

### 執行所有測試

```bash
pytest tests/ -v
```

### 測試覆蓋率

```bash
# Run with coverage
pytest tests/ --cov=lingmaflow --cov-report=html

# View HTML report
open htmlcov/index.html
```

### 當前狀態

- **Total Tests**: 153
- **Passing**: 153 ✅
- **Failing**: 0
- **Coverage**: ~90%

測試分佈：
- `test_task_state.py` - TaskStateManager 測試
- `test_skill_registry.py` - SkillRegistry 測試
- `test_agents_injector.py` - AgentsInjector 測試
- `test_cli.py` - CLI 命令測試
- `test_condition_checker.py` - ConditionChecker 測試 (v0.2.0 NEW)

---

## 版本歷史 Version History

### v0.2.0 (Current)

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

---

## 貢獻 Contributing

歡迎提交 Issue 和 Pull Request！

### 開發環境設置

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

---

## 相關資源 Resources

- [Lingma IDE](https://lingma.aliyun.com/)
- [Superpowers Paper](https://example.com/superpowers)
- [Click Documentation](https://click.palletsprojects.com/)

---

**最後更新**: 2026-04-02  
**版本**: v0.2.0  
**維護者**: LingmaFlow Team
