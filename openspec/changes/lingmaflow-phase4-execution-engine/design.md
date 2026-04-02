## Context

LingmaFlow Phase 1-3 完成了核心模組（TaskStateManager, SkillRegistry, AgentsInjector）和 CLI 工具，以及五大技能的內容填充。然而，整個系統缺少自動驗證和推進能力，AI Agent 需要手動檢查任務完成狀態。

**背景：**
- TASK_STATE.md 追蹤當前步驟和狀態，但缺少細粒度的完成條件
- AI Agent 需要主觀判斷「什麼叫做完成」，容易導致品質不一致
- 無法自動驗證程式碼、測試、功能是否真正完成

**約束條件：**
- 純 Python 實作，不依賴任何外部工具或 Lingma 特定功能
- 完全向後相容，舊的 TASK_STATE.md 仍然可用
- 保持簡單，避免過度設計

**利害關係人：**
- AI Agent：需要明確的驗證標準和自動推進能力
- 開發者：需要透明的驗證過程和可控的推進機制

## Goals / Non-Goals

**Goals:**
- 新增 ConditionChecker 模組，支援三種驗證類型（file, pytest, func）
- 擴充 TaskStateManager，支援 Done Conditions 解析與更新
- 新增三個 CLI 指令（prepare, verify, checkpoint）
- 提供清晰的驗證回饋（✅/❌圖示）
- 實現自動推進能力（checkpoint 命令）
- 保持純 Python 實作，零外部依賴

**Non-Goals:**
- 不自定義新的驗證語言或 DSL（使用簡單的前綴格式）
- 不提供視覺化介面（保持 CLI）
- 不修改現有的 CLI 命令（status, advance, block, resolve）
- 不強制要求 Done Conditions（選擇性功能）
- 不處理並行驗證或分散式執行

## Decisions

### 1. Done Conditions 格式選擇

**決策：** 使用 Markdown checkbox + 前綴格式
```markdown
## Done Conditions
- [ ] file:lingmaflow/core/task_state.py
- [ ] pytest:tests/test_task_state.py
- [ ] func:lingmaflow.core.TaskStateManager
```

**原因：**
- 與現有 TASK_STATE.md 格式一致（都是 Markdown）
- 人類可讀，易於手動編輯
- 簡單的字串解析即可（不需要複雜的 parser）
- Checkbox 語法天然支援完成狀態追蹤

**替代方案考慮：**
- YAML frontmatter：太正式，與現有格式不一致
- JSON 格式：不易閱讀和手動編輯
- 自定義 DSL：增加學習成本

### 2. 驗證類型設計

**決策：** 三種基本類型（file, pytest, func）

**原因：**
- `file:` 覆蓋檔案存在性檢查（最基礎）
- `pytest:` 覆蓋測試驗證（品質保證）
- `func:` 覆蓋程式碼存在性（API 穩定性）
- 這三種已足夠覆蓋 90% 的驗證場景

**替代方案考慮：**
- 更多類型（如 `http:`, `db:`, `perf:`）：留待未來擴充
- 組合條件（AND/OR）：增加複雜度，暫不需要

### 3. ConditionChecker 實作方式

**決策：** 使用 Python 標準庫
- `os.path.exists()` 檢查檔案
- `subprocess.run()` 執行 pytest
- `importlib.import_module()` 驗證模組

**原因：**
- 零外部依賴
- 跨平台相容性好
- 錯誤處理簡單直接

**替代方案考慮：**
- 使用 `pathlib`：可以，但 `os.path` 更直觀
- 使用 `unittest.TestLoader`：太複雜，subprocess 更直接

### 4. CLI 命令名稱選擇

**決策：** `prepare`, `verify`, `checkpoint`

**原因：**
- `prepare`：清楚表達「準備任務上下文」
- `verify`：直觀表達「驗證條件」
- `checkpoint`：隱喻「檢查點」，通過後自動推進

**替代方案考慮：**
- `setup` / `check` / `advance-auto`：不夠精確
- `context` / `validate` / `auto`：語意不夠清晰

### 5. 錯誤處理策略

**決策：**
- 驗證失敗時返回 exit_code 1
- 顯示清晰的 ✅/❌ 回饋
- 不中斷其他條件的驗證（全部顯示）

**原因：**
- Exit code 方便腳本整合
- 圖示比文字更直觀
- 全部顯示幫助快速定位問題

### 6. .lingmaflow/current_task.md 位置

**決策：** 固定在 `.lingmaflow/current_task.md`

**原因：**
- 隱藏目錄（`.` 開頭）不干擾專案結構
- 固定路徑方便 AI Agent 查找
- 與 `.git` 等工具保持一致的命名慣例

## Risks / Trade-offs

### [Risk] Pytest 執行時間過長

**描述：** 如果 Done Conditions 包含多個 `pytest:` 檢查，可能耗時較長

**Mitigation:**
- 建議用戶將測試分組為一個大的測試路徑
- 未來可考慮平行執行
- 添加超時機制

### [Risk] Func 檢查的模組副作用

**描述：** `import_module()` 可能觸發模組初始化代碼

**Mitigation:**
- 文件說明這個潛在風險
- 建議避免在模組層級執行昂貴的操作
- 未來可考慮更安全的檢查方式（如 AST 解析）

### [Risk] 硬編碼的前綴格式

**描述：** `file:`, `pytest:`, `func:` 是硬編碼的

**Mitigation:**
- 使用枚舉或常數定義
- 添加清晰的錯誤訊息
- 預留擴充機制（UnknownConditionTypeError）

### [Risk] Git Commit 的安全性

**描述：** `checkpoint --commit` 自動提交可能包含未預期的變更

**Mitigation:**
- 預設不啟用 `--commit` 旗標
- 文件警告用戶謹慎使用
- 未來可考慮 dry-run 模式

## Migration Plan

### 階段 1: 核心實作
1. 實作 ConditionChecker 模組
2. 實作 ConditionResult dataclass
3. 實作 UnknownConditionTypeError

### 階段 2: TaskStateManager 擴充
1. 新增 `get_conditions()` 方法
2. 新增 `mark_condition_done()` 方法
3. 新增 `all_conditions_done()` 方法
4. 確保向後相容（沒有 Done Conditions 區塊時不報錯）

### 階段 3: CLI 命令實作
1. 實作 `prepare` 命令
2. 實作 `verify` 命令
3. 實作 `checkpoint` 命令
4. 整合 SkillRegistry 用於技能參考

### 階段 4: 測試覆蓋
1. 編寫 ConditionChecker 單元測試
2. 編寫 TaskStateManager 擴充測試
3. 編寫 CLI 命令整合測試
4. 確保所有測試通過

### 階段 5: 文檔更新
1. 更新 README.md
2. 更新 SKILL.md（如果需要）
3. 準備歸檔

## Open Questions

無（所有設計決策已明確）
