## Why

Phase 1 已經完成了三個核心模組（task_state.py、skill_registry.py、agents_injector.py），但目前缺乏 CLI 工具來讓用戶和 agent 與這些模組互動。用戶需要手動執行 Python 程式碼或使用檔案系統操作，這不符合使用者體驗。Phase 2 將建立完整的 CLI 工具，提供直觀的命令列介面來管理任務狀態、查詢技能和生成 AGENTS.md。

## What Changes

- **修改** `lingmaflow/cli/lingmaflow.py`：從空檔案升級為完整 CLI 工具
  - 使用 Click 框架建構命令列介面
  - 新增 `status` 命令：顯示當前任務狀態
  - 新增 `advance` 命令：推進任務到下一步
  - 新增 `skill find <keyword>` 命令：查詢技能
  - 新增 `skill list` 命令：列出所有技能
  - 新增 `agents generate` 命令：生成 AGENTS.md
  - 新增 `init` 命令：初始化 LingmaFlow 專案

- **新增** `tests/test_cli.py`：CLI 命令測試
  - 測試每個命令的輸入輸出
  - 測試錯誤處理
  - 使用 Click 的 CliRunner 進行測試

- **新增** `pyproject.toml` 中的 CLI entry point
  - 註冊 `lingmaflow` 命令
  - 確保 Click 依賴已安裝

## Capabilities

### New Capabilities
- `cli-task-management`: 透過 CLI 管理任務狀態的能力（status, advance, block, resolve）
- `cli-skill-query`: 透過 CLI 查詢技能的能力（skill find, skill list）
- `cli-agents-generation`: 透過 CLI 生成 AGENTS.md 的能力（agents generate）
- `cli-project-init`: 初始化 LingmaFlow 專案的能力（init）

### Modified Capabilities
- 無（此為全新功能，不影響現有需求）

## Impact

- **核心模組**: `lingmaflow/cli/lingmaflow.py` 將成為主要的使用者介面
- **依賴**: 
  - Click (已在 pyproject.toml 中) 用於 CLI 框架
  - 現有 core 模組（task_state, skill_registry, agents_injector）
- **用戶體驗**: 從手動操作升級為直觀的 CLI 命令
- **打包**: 需要在 pyproject.toml 中註冊 entry point
