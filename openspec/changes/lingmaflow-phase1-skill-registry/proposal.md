## Why

目前的 skills 目錄雖然有 5 個 skill 資料夾，但都只有空的 SKILL.md 檔案，缺乏統一的格式規範和載入機制。Agent 無法自動發現、查詢或使用這些 skills。SkillRegistry 將提供標準化的 skill 發現與查詢功能，讓 agent 能夠動態載入合適的 skills 來完成任務。

## What Changes

- **新增** `lingmaflow/core/skill_registry.py`：技能註冊表核心模組
  - `Skill` dataclass：統一 skill 資料結構
  - `SkillRegistry` 類別：提供 scan、get、find、list 方法
  - YAML frontmatter 解析支援
  - 自訂異常 `MalformedSkillError`

- **新增** `tests/test_skill_registry.py`：完整的單元測試覆蓋
  - 測試所有公開方法
  - 測試錯誤處理
  - 使用 tmp_path fixture 隔離測試

- **修改** 現有 `skills/*/SKILL.md`：更新為 YAML frontmatter 格式（後續任務）
  - 新增 name、version、triggers、priority 等中繼資料
  - 保留原有正文內容

## Capabilities

### New Capabilities
- `skill-discovery`: 掃描 skills 目錄並載入 SKILL.md 檔案的能力
- `skill-query`: 依名稱或關鍵字查詢技能的能力
- `skill-validation`: 驗證 SKILL.md 格式與必要欄位的能力

### Modified Capabilities
- 無（此為全新功能，不影響現有需求）

## Impact

- **核心模組**: `lingmaflow/core/skill_registry.py` 將被 CLI 工具和其他模組使用
- **Skills 目錄**: 需要更新現有的 SKILL.md 為新格式（後續任務）
- **依賴**: 
  - Python 標準庫 (dataclasses, pathlib, typing)
  - PyYAML (已在 pyproject.toml 中) 用於解析 YAML frontmatter
- **測試**: 需要新增 `tests/test_skill_registry.py`
