## Why

Phase 3 完成了五大核心技能的內容填充，但 LingmaFlow 缺少實際執行能力。這個變更新增執行引擎，讓 AI Agent 能夠自動驗證任務完成狀態，並在滿足條件時自動推進，實現真正的自主執行。

## What Changes

- **新增 ConditionChecker 模組**：純 Python 實作的條件驗證器，支援三種驗證類型（檔案存在、pytest 測試、函式存在）
- **擴充 TaskStateManager**：新增 Done Conditions 區塊的解析與更新能力
- **新增三個 CLI 指令**：
  - `lingmaflow prepare`：準備當前任務上下文，包含技能參考
  - `lingmaflow verify`：驗證所有 Done Conditions
  - `lingmaflow checkpoint`：驗證通過後自動推進並可選提交
- **新增 .lingmaflow/current_task.md**：任務執行時的上下文文件
- **TASK_STATE.md 格式擴充**：新增 ## Done Conditions 區塊

## Capabilities

### New Capabilities

- `execution-engine`: ConditionChecker 核心驗證邏輯，包含 file/pytest/func 三種檢查類型
- `task-preparation`: prepare 命令，讀取 TASK_STATE.md 和 SKILL.md，生成任務上下文
- `condition-verification`: verify 命令，執行所有條件檢查並顯示結果
- `auto-advance`: checkpoint 命令，驗證通過後自動推進到下一步
- `state-management-extension`: TaskStateManager 擴充，支援 Done Conditions 解析與更新

### Modified Capabilities

無（不修改現有技能的需求）

## Impact

- **新增檔案**：
  - `lingmaflow/core/condition_checker.py`：核心驗證邏輯
  - `tests/test_condition_checker.py`：ConditionChecker 單元測試
  - `.lingmaflow/current_task.md`：運行時生成的任務上下文
  
- **修改檔案**：
  - `lingmaflow/core/task_state.py`：TaskStateManager 擴充
  - `lingmaflow/cli/lingmaflow.py`：新增三個 CLI 指令
  - `tests/test_cli.py`：新增 CLI 測試
  - `tests/test_task_state.py`：TaskStateManager 擴充測試
  
- **依賴**：
  - 純 Python 標準庫（os, subprocess, importlib）
  - 不依賴任何外部工具或 Lingma 特定功能
  
- **向後相容**：
  - 完全向後相容
  - Done Conditions 區塊為選擇性，舊的 TASK_STATE.md 仍然可用
  - 現有三個 CLI 命令（status, advance, block, resolve）不受影響
