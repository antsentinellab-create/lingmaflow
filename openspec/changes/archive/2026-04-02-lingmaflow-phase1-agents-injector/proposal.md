## Why

目前的 AGENTS.md 是手動維護的靜態檔案，無法反映 SkillRegistry 中實際可用的 skills。當 skills 新增或移除時，AGENTS.md 不會自動更新，導致 agent 無法得知最新的可用技能。AgentsInjector 將自動化 AGENTS.md 的生成過程，確保防迷路規則與可用技能清單始終保持同步。

## What Changes

- **新增** `lingmaflow/core/agents_injector.py`：AgentsInjector 核心模組
  - `InjectionError` 自訂異常
  - `AgentsInjector` 類別：提供 generate、inject、update 方法
  - 動態從 SkillRegistry 讀取可用技能
  - 產生標準化的 AGENTS.md 格式

- **新增** `tests/test_agents_injector.py`：完整的單元測試覆蓋
  - 測試 generate() 方法
  - 測試 inject() 和 update() 方法
  - 測試錯誤處理
  - 使用 tmp_path fixture 隔離測試

- **修改** 現有 `AGENTS.md`：由 AgentsInjector 自動生成（後續任務）
  - 保留固定內容（防迷路規則、Done Condition、錯誤處置）
  - 動態插入可用 Skill 清單

## Capabilities

### New Capabilities
- `agents-md-generation`: 根據 SkillRegistry 動態生成 AGENTS.md 內容的能力
- `agents-md-injection`: 將生成的內容寫入指定路徑的能力
- `agents-md-validation`: 驗證輸出路徑可寫性的能力

### Modified Capabilities
- 無（此為全新功能，不影響現有需求）

## Impact

- **核心模組**: `lingmaflow/core/agents_injector.py` 將被 CLI 工具和初始化流程使用
- **依賴**: 
  - Python 標準庫 (pathlib, typing)
  - `lingmaflow.core.skill_registry` 模組（已在 pyproject.toml 依賴中）
- **測試**: 需要新增 `tests/test_agents_injector.py`
- **現有檔案**: `AGENTS.md` 將改為由 Injector 自動生成
