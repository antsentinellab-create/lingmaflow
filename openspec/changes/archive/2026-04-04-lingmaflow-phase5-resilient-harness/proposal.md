## Why

目前 LingmaFlow 在執行長任務時，一旦中斷（context window 限制或手動停止），agent 只能靠 grep 猜測做到哪裡。問題根源在於：

1. **tasks.md 使用 Markdown checkbox 格式**：容易被 agent 誤改，且只記錄「做了什麼」，不記錄「為什麼這樣做」
2. **缺乏決策記憶**：沒有記錄嘗試過什麼、為什麼失敗、下個 session 該注意什麼
3. **沒有標準接回流程**：新 session 的 agent 靠直覺推測狀態，容易誤判進度

這導致長任務（200+ features）幾乎無法完成，因為 agent 會在多次中斷後迷失。本 change 引入 Anthropic 實測有效的 harness 系統，讓 agent 能精確接回中斷的任務。

## What Changes

- **新增 `lingmaflow/core/harness.py` 模組**：包含 `HarnessManager` class 和 `ResumePoint` dataclass，管理 tasks.json 和 PROGRESS.md 的讀寫
- **新增 CLI 子命令群組 `lingmaflow harness`**：
  - `harness init <change_name>`：初始化 openspec change 的執行環境
  - `harness done <task_id>`：標記 task 完成並記錄決策
  - `harness log`：session 結束前記錄決策過程
  - `harness resume`：生成接回指令給新 session 的 agent
  - `harness status`：查看當前 change 的整體進度
- **tasks.md → tasks.json 格式遷移**：從 Markdown checkbox 改為 JSON 格式，增加 started_at/completed_at/notes 欄位
- **新增 PROGRESS.md 檔案**：作為 agent 的 portable long-term memory，記錄每個 session 的決策與失敗經驗
- **更新 AGENTS.md 模板**：注入 harness 執行規則，規範 agent 如何與 harness 互動
- **新增測試檔案 `tests/test_harness.py`**：驗證 HarnessManager 的核心功能

## Capabilities

### New Capabilities

- `harness-manager`: HarnessManager class，負責管理 tasks.json 和 PROGRESS.md 的生命週期
- `cli-harness-commands`: CLI harness 子命令群組，提供 init/done/log/resume/status 命令
- `progress-tracking`: PROGRESS.md 格式與 session log 機制，記錄決策記憶
- `task-json-format`: tasks.json schema 與 tasks.md 轉換邏輯

### Modified Capabilities

無（不修改現有 spec 級別的需求）

## Impact

- **Affected code**: 
  - 新增 `lingmaflow/core/harness.py`
  - 修改 `lingmaflow/cli/lingmaflow.py`（新增 harness 子命令）
  - 修改 `lingmaflow/templates/AGENTS.md.j2`（注入 harness 規則）
  - 新增 `tests/test_harness.py`
- **Dependencies**: 需要 git 命令支援（每步自動 commit）
- **Systems**: 與現有 openspec 工作流整合，向後相容於 phase4 的 verify/checkpoint 機制
- **Breaking changes**: 無，向後相容。tasks.md 會自動轉換為 tasks.json 並保留備份
