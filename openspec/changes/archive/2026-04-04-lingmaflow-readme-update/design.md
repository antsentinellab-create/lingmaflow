## Context

**當前狀態：**
- README.md 是 v0.1.0 版本，只包含基本的 task management 和 skill 查詢功能
- Phase 4 執行引擎（prepare / verify / checkpoint）已完成但未在 README 中說明
- 缺少完整的標準工作流程指導
- Done Conditions 格式未文檔化

**背景：**
- LingmaFlow 已進入 v0.2.0，核心功能完整
- 153 個測試全部通過，功能穩定
- 需要完整的用戶指南幫助用戶使用執行引擎

**約束條件：**
- 保持中英雙語（繁體中文 + English）
- 保持與現有 AGENTS.md 一致的風格
- 清晰、簡潔、易於快速查閱

**利害關係人：**
- 新用戶：需要快速了解功能和安裝
- 現有用戶：需要學習執行引擎使用方法
- 貢獻者：需要了解整體架構

## Goals / Non-Goals

**Goals:**
- 全面更新 README.md 反映 v0.2.0 功能
- 新增執行引擎命令說明（prepare / verify / checkpoint）
- 新增 Done Conditions 格式和驗證機制
- 提供標準工作流程範例
- 更新架構說明包含 condition_checker.py
- 更新測試狀態為 153 tests

**Non-Goals:**
- 不修改任何程式碼（純文檔更新）
- 不改變現有 CLI 命令行為
- 不引入新的功能或依賴
- 不修改其他文檔檔案（AGENTS.md, TASK_STATE.md 等）

## Decisions

### 1. README 結構設計

**決策：** 採用模組化結構，分為 8 個主要區塊

**結構：**
1. 專案定位（Project Title & Problems Solved）
2. 安裝（Installation）
3. CLI 指令清單（CLI Commands Reference）
4. 標準工作流程（Standard Workflow）
5. Done Conditions 格式（Done Condition Format）
6. 架構說明（Architecture）
7. 測試（Testing）
8. License

**原因：**
- 符合開源專案慣例
- 由淺入深，從安裝到進階使用
- 方便快速查閱特定功能

### 2. 語言策略

**決策：** 中英雙語並列，以繁體中文為主

**格式：**
```markdown
# 標題（中文）
## Title (English)

內容以繁體中文撰寫，關鍵術語保留英文
```

**原因：**
- 符合台灣開發者習慣
- 保留國際化可能性
- 技術術語使用英文便於搜尋

### 3. CLI 命令呈現方式

**決策：** 使用表格 + 程式碼範例

**格式：**
```markdown
| Command | Description |
|---------|-------------|
| `lingmaflow init` | Initialize project |

```bash
$ lingmaflow prepare
```
```

**原因：**
- 表格方便快速瀏覽
- 程式碼範例展示實際用法
- 符合 Click CLI 文檔慣例

### 4. 工作流程呈現

**決策：** 使用步驟式說明 + 流程圖

**格式：**
```markdown
### Step 1: Initialize
$ lingmaflow init

### Step 2: Prepare
$ lingmaflow prepare
...
```

**原因：**
- 逐步指導初學者
- 可複製貼上執行
- 降低學習曲線

### 5. Done Conditions 格式

**決策：** 明確列出三種類型 + 範例

**格式：**
```markdown
## Done Condition Types

1. **file:PATH** - Check file existence
   ```markdown
   - [ ] file:lingmaflow/core/task_state.py
   ```

2. **pytest:PATH** - Run pytest
   ...
```

**原因：**
- 清晰區分三種驗證類型
- 提供可直接使用的範例
- 避免混淆

### 6. 架構說明深度

**決策：** 高層次概述 + 核心模組列表

**內容：**
- 列出 5 個核心模組
- 每個模組一句話說明職責
- 不包含詳細 API 或實作細節

**原因：**
- README 應該保持簡潔
- 詳細 API 文件應放在 docstring 或獨立文檔
- 快速了解整體架構即可

## Risks / Trade-offs

### [Risk] README 過於冗長

**描述：** 包含所有功能可能使 README 過長

**Mitigation:**
- 保持每個章節簡潔
- 使用表格而非長段落
- 提供清晰的章節標題方便跳讀
- 進階細節連結到 wiki 或 docstring

### [Risk] 中英雙語增加維護成本

**描述：** 雙語可能需要同步更新

**Mitigation:**
- 以中文為主，英文為輔
- 英文標題僅供參考
- 未來可考慮純中文或純英文版本

### [Risk] 快速演化的 API

**描述：** CLI 命令可能繼續擴充

**Mitigation:**
- 使用 `lingmaflow --help` 作為權威參考
- README 聚焦穩定的核心功能
- 標註實驗性功能

## Migration Plan

### 階段 1: 準備
1. 讀取現有 README.md
2. 備份原始版本
3. 確認所有新功能已完成

### 階段 2: 重寫
1. 更新專案定位（v0.2.0）
2. 新增執行引擎命令
3. 新增 Done Conditions 格式
4. 新增標準工作流程
5. 更新架構說明
6. 更新測試狀態

### 階段 3: 驗證
1. 檢查所有連結有效
2. 驗證程式碼範例可執行
3. 確認中英雙語正確
4. 檢查格式一致性

### 階段 4: 發布
1. Commit: "docs: Update README for v0.2.0"
2. 準備歸檔這個變更

## Open Questions

無（所有設計決策已明確）
