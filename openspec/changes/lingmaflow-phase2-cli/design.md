## Context

目前 LingmaFlow 有三個核心模組已經實作完成，但缺乏使用者介面：
- task_state.py：任務狀態管理
- skill_registry.py：技能註冊表
- agents_injector.py：AGENTS.md 生成器

用戶需要手動操作檔案系統或執行 Python 程式碼，體驗不佳。需要建立 CLI 工具來提供直觀的命令列介面。

這是一個從零開始的 CLI 建構，需要整合所有 Phase 1 的核心模組。

## Goals / Non-Goals

**Goals:**
- 使用 Click 框架建立完整的 CLI 工具
- 提供 task status/advance/block/resolve 命令
- 提供 skill find/list 命令
- 提供 agents generate 命令
- 提供 init 命令初始化專案
- 完整的錯誤處理和用戶提示
- 100% 測試覆蓋率

**Non-Goals:**
- GUI 介面（未來可能）
- Web 介面（未來可能）
- 互動式模式（REPL）
- 複雜的參數組合（保持簡單）
- 自訂幫助系統（使用 Click 內建）

## Decisions

### 1. CLI 框架：Click

**選擇**: 使用 Click (Command Line Interface Toolkit)

```python
import click

@click.group()
def cli():
    """LingmaFlow CLI tool."""
    pass

@cli.command()
def status():
    """Show current task status."""
    pass
```

**原因**:
- 已在 pyproject.toml 依賴中
- Python 標準的 CLI 框架
-  declarative 語法，易於閱讀
- 自動生成 --help
- 支援子命令群組
- 良好的錯誤處理

**替代方案考慮**:
- argparse：標準庫但語法繁瑣
- typer：現代但增加額外依賴
- docopt：過於複雜

### 2. 命令結構：分層設計

**選擇**: 使用 Click 的 group/command 分層結構

```
lingmaflow
├── status
├── advance
├── block
├── resolve
├── skill
│   ├── find <keyword>
│   └── list
├── agents
│   └── generate
└── init
```

**原因**:
- 清晰的功能分類
- 符合常見 CLI 工具習慣（如 git, docker）
- 易於擴展新命令
- 幫助訊息有組織

### 3. 路徑處理：相對 vs 絕對

**選擇**: 預設使用當前工作目錄，可選指定路徑

```python
@click.option('--path', '-p', default='.', help='Project path')
def status(path):
    ctx = click.get_current_context()
    project_path = Path(path).resolve()
```

**原因**:
- 符合 UNIX 慣例
- 簡單直覺
- 支援相对路径和绝對路径

### 4. 錯誤處理策略：友好提示

**選擇**: 使用 click.echo() 顯示錯誤，返回非零退出碼

```python
@click.command()
def advance():
    try:
        # ... operation
    except InvalidStateError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)
```

**原因**:
- Click 標準做法
- 清晰的錯誤訊息
- 正確的退出碼利於腳本整合

### 5. 輸出格式：人類可讀

**選擇**: 使用簡單的格式化文字輸出

```
Current Step: STEP-02
Status: in_progress
Last Result: Success
Next Action: Continue implementation
Unresolved Issues: None
```

**原因**:
- 易於閱讀
- 終端友好
- 不需要額外依賴（如 rich, colorama）
- 未來可升級為 JSON 輸出

### 6. 測試策略：CliRunner

**選擇**: 使用 Click 的 CliRunner 進行測試

```python
from click.testing import CliRunner

def test_status_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['status'])
    assert result.exit_code == 0
    assert 'STEP-02' in result.output
```

**原因**:
- Click 官方推薦
- 隔離測試
- 可測試輸出和退出碼

## Risks / Trade-offs

### [Risk] Click 版本相容性
**風險**: 不同版本的 Click API 可能有差異

**緩解**:
- 在 pyproject.toml 中鎖定版本範圍
- 使用穩定的 API（group, command, option）
- 避免使用實驗性功能

### [Risk] 命令過於簡化
**風險**: 某些複雜操作可能需要更多參數

**緩解**:
- 未來可增加 --force, --dry-run 等選項
- 保持核心命令簡單
- 複雜功能留給未來擴展

### [Trade-off] 功能完整性 vs 簡單性
**選擇**: 優先保持簡單，暫不實作：
- 互動式確認（--yes 跳過）
- 詳細模式（-v/--verbose）
- JSON 輸出（--json）
- 別名支援

**原因**: 
- MVP 思維，先解決核心問題
- 可透過後續迭代增強
- 避免過度設計

### [Risk] 跨平台相容性
**風險**: Windows/Linux/macOS 的路徑和編碼差異

**緩解**:
- 使用 pathlib 處理路徑
- 統一使用 UTF-8 編碼
- 避免使用平台特定功能

## Migration Plan

### 階段 1: 核心實作（本次）
1. 實作 `lingmaflow/cli/lingmaflow.py`
2. 更新 `pyproject.toml` entry point
3. 編寫完整測試
4. 確保 100% 通過

### 階段 2: 打包和發布（後續任務）
1. 配置 pyproject.toml scripts
2. 測試 pip install .
3. 驗證 lingmaflow 命令可用

### 階段 3: 增強（未來可能的增強）
1. 增加 --verbose 選項
2. 增加 --json 輸出格式
3. 增加更多實用命令

**回滾策略**: 
- 純新增功能，不影響現有代碼
- 測試失敗時刪除 CLI 檔案即可
- 使用 git revert

## Open Questions

1. **是否需要支援環境變數？**
   - 例如 LINGMAFLOW_PROJECT_PATH
   - 目前是命令行參數

2. **init 命令應該做什麼？**
   - 建立基本目錄結構？
   - 生成初始 TASK_STATE.md？
   - 建立 AGENTS.md？

3. **錯誤訊息是否要本地化？**
   - 目前是英文錯誤訊息
   - 未來可能需要多語言

4. **是否需要自動完成？**
   - Click 支援 bash/zsh completion
   - 需要額外設定
