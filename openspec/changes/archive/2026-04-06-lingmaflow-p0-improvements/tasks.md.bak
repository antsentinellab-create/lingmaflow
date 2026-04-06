# Tasks: lingmaflow-p0-improvements

## ⚠️ 執行規則（必讀，不可跳過）

```
每完成一個 Task → 立即執行 lingmaflow harness done <task_id> --notes "..."
不得自行繼續下一個 Task
輸出「✅ Task X.X 完成，等待確認」後停止
```

---

## Section 1：修改 agents_injector.py，加入 harness 強制規則

### Task 1.1 — 閱讀現有 agents_injector.py

```bash
cat lingmaflow/agents_injector.py
```

確認：
- `generate()` 方法的簽名
- 目前注入 AGENTS.md 的方式（字串模板還是檔案）
- 是否有 `project_path` 參數

完成後：
```bash
lingmaflow harness done 1.1 --notes "generate() 簽名: <填入實際簽名>"
```
輸出「✅ Task 1.1 完成，等待確認」後停止。

---

### Task 1.2 — 新增 `_has_harness()` 方法

在 `agents_injector.py` 加入以下方法（加在 class 內，`generate()` 之前）：

```python
def _has_harness(self, project_path: Path) -> bool:
    """偵測是否有任何 change 的 tasks.json 存在"""
    openspec_path = project_path / "openspec" / "changes"
    if not openspec_path.exists():
        return False
    for change_dir in openspec_path.iterdir():
        if change_dir.is_dir() and (change_dir / "tasks.json").exists():
            return True
    return False
```

驗證：
```bash
python3 -c "
from pathlib import Path
from lingmaflow.agents_injector import AgentsInjector
inj = AgentsInjector()
print(hasattr(inj, '_has_harness'))
"
```
預期輸出：`True`

完成後：
```bash
lingmaflow harness done 1.2 --notes "_has_harness 加入成功"
```
輸出「✅ Task 1.2 完成，等待確認」後停止。

---

### Task 1.3 — 新增 HARNESS_RULES 字串常數

在 `agents_injector.py` 的常數區塊（或檔案頂端）加入：

```python
HARNESS_RULES = """
## harness 執行規則（強制，不可跳過）

### 每完成一個 task 後，立即執行
```bash
lingmaflow harness done <task_id> --notes "<關鍵決策>"
```

### session 結束前，執行
```bash
lingmaflow harness log --change <change_name> \\
  --completed "<完成的 task IDs>" \\
  --leftover "<未完成的 task>" \\
  --failed "<失敗記錄，無則填 none>" \\
  --next "<下一步指引>"
```

### 禁止行為
- 不可跳過 harness done，即使 task 很簡單
- 不可修改 tasks.json 的 id 或 description 欄位
- 不可刪除任何 task 條目
"""
```

驗證：
```bash
python3 -c "from lingmaflow.agents_injector import HARNESS_RULES; print('OK')"
```
預期輸出：`OK`

完成後：
```bash
lingmaflow harness done 1.3 --notes "HARNESS_RULES 常數加入成功"
```
輸出「✅ Task 1.3 完成，等待確認」後停止。

---

### Task 1.4 — 修改 `generate()` 方法，偵測 harness 並注入規則

修改 `generate()` 方法，加入 `project_path` 可選參數，並在有 harness 時附加 `HARNESS_RULES`：

```python
def generate(self, force: bool = False, project_path: Path = None) -> str:
    # ... 現有邏輯不變 ...

    # 在產生 AGENTS.md 內容的最後加入：
    if project_path is not None and self._has_harness(project_path):
        content += "\n" + HARNESS_RULES

    return content
```

⚠️ 注意：`project_path=None` 時行為與原版完全相同（向後相容）。

驗證（建立假的 tasks.json 後測試）：
```bash
python3 -c "
import tempfile, json
from pathlib import Path
from lingmaflow.agents_injector import AgentsInjector

with tempfile.TemporaryDirectory() as tmp:
    p = Path(tmp)
    change_dir = p / 'openspec' / 'changes' / 'test-change'
    change_dir.mkdir(parents=True)
    (change_dir / 'tasks.json').write_text('[]')

    inj = AgentsInjector()
    result = inj.generate(project_path=p)
    print('harness rules injected:', 'harness 執行規則' in result)
"
```
預期輸出：`harness rules injected: True`

完成後：
```bash
lingmaflow harness done 1.4 --notes "generate() 向後相容，harness 偵測正確"
```
輸出「✅ Task 1.4 完成，等待確認」後停止。

---

### Task 1.5 — 更新 CLI 的 agents generate 命令，傳入 project_path

找到 `lingmaflow/cli.py`（或對應的 CLI 入口）中 `agents generate` 的 handler，
加入 `project_path=Path(".")` 傳遞：

```python
# 修改前（示意）
content = injector.generate(force=force)

# 修改後
content = injector.generate(force=force, project_path=Path("."))
```

驗證（在有 tasks.json 的目錄執行）：
```bash
# 先建立測試用 tasks.json
mkdir -p /tmp/lf-test/openspec/changes/my-change
echo '[]' > /tmp/lf-test/openspec/changes/my-change/tasks.json
cp AGENTS.md /tmp/lf-test/AGENTS.md 2>/dev/null || true

cd /tmp/lf-test
lingmaflow agents generate --force
grep -c "harness 執行規則" AGENTS.md
```
預期輸出：`1`

完成後：
```bash
lingmaflow harness done 1.5 --notes "CLI 傳入 project_path 成功"
```
輸出「✅ Task 1.5 完成，等待確認」後停止。

---

### Task 1.6 — 補充 Section 1 的測試

在 `tests/` 目錄新增或修改對應測試，確保：

- `test_has_harness_returns_false_when_no_tasks_json()`
- `test_has_harness_returns_true_when_tasks_json_exists()`
- `test_generate_injects_harness_rules_when_harness_detected()`
- `test_generate_backward_compatible_without_project_path()`

執行測試：
```bash
pytest tests/ -k "harness" -v
```
預期：全部 PASSED，無 FAILED。

完成後：
```bash
lingmaflow harness done 1.6 --notes "新增 4 個測試，全部通過"
```
輸出「✅ Task 1.6 完成，等待確認」後停止。

---

## Section 2：checkpoint 成功後自動執行 prepare

### Task 2.1 — 找到 checkpoint 的實作位置

```bash
grep -rn "def checkpoint" lingmaflow/
grep -rn "checkpoint" lingmaflow/cli.py | head -20
```

確認：
- checkpoint 邏輯在哪個檔案
- 推進成功後的返回點（`result.success` 或直接 `advance()` 後）

完成後：
```bash
lingmaflow harness done 2.1 --notes "checkpoint 實作在: <填入檔案路徑>"
```
輸出「✅ Task 2.1 完成，等待確認」後停止。

---

### Task 2.2 — 修改 checkpoint，成功推進後呼叫 prepare

在 checkpoint 成功推進的分支加入 `prepare()` 呼叫：

```python
# 推進成功後（示意，依實際程式碼調整）
advance_result = self.advance(step_id, result)
if advance_result.success:
    # 自動更新 current_task.md
    try:
        from lingmaflow.execution_engine import ExecutionEngine
        engine = ExecutionEngine(project_path=self.project_path)
        engine.prepare()
        click.echo("📋 current_task.md 已自動更新")
    except Exception as e:
        # prepare 失敗不應中斷 checkpoint 流程
        click.echo(f"⚠️  prepare 自動執行失敗（不影響 checkpoint）: {e}")
```

⚠️ 注意：prepare 失敗時只 warn，不 raise，不中斷 checkpoint 流程。

驗證（手動執行）：
```bash
# 在有 TASK_STATE.md 的測試目錄
lingmaflow checkpoint STEP-01 "test auto-prepare"
ls -la .lingmaflow/current_task.md
```
預期：`.lingmaflow/current_task.md` 的 mtime 更新。

完成後：
```bash
lingmaflow harness done 2.2 --notes "auto-prepare 加入，失敗不中斷主流程"
```
輸出「✅ Task 2.2 完成，等待確認」後停止。

---

### Task 2.3 — 補充 Section 2 的測試

在 `tests/` 新增：
- `test_checkpoint_calls_prepare_on_success()`：mock prepare，驗證被呼叫
- `test_checkpoint_succeeds_even_if_prepare_fails()`：prepare 拋例外時 checkpoint 仍成功

執行測試：
```bash
pytest tests/ -k "checkpoint" -v
```
預期：全部 PASSED。

完成後：
```bash
lingmaflow harness done 2.3 --notes "checkpoint auto-prepare 測試通過"
```
輸出「✅ Task 2.3 完成，等待確認」後停止。

---

## Section 3：更新 openspec-apply-change 指令模板

### Task 3.1 — 找到 openspec-apply-change 模板位置

```bash
find openspec/ -name "*.md" | xargs grep -l "apply-change" 2>/dev/null | head -5
ls openspec/
cat openspec/AGENTS.md 2>/dev/null || echo "not found"
```

確認 `openspec-apply-change` 的指令模板在哪個檔案。

完成後：
```bash
lingmaflow harness done 3.1 --notes "模板位置: <填入路徑>"
```
輸出「✅ Task 3.1 完成，等待確認」後停止。

---

### Task 3.2 — 在 openspec-apply-change 指令模板加入強制停止規則

在模板的「執行規則」或「強制規則」區塊加入：

```markdown
## 強制停止規則（不可忽略）

每完成一個 Section 後：
1. 停止執行
2. 輸出：「✅ Section X 完成，等待驗證」
3. 等待人工執行 `lingmaflow verify`
4. 不得自行繼續下一個 Section

每完成一個 Task 後：
1. 執行：`lingmaflow harness done <task_id> --notes "<關鍵決策>"`
2. 輸出：「✅ Task X.X 完成，等待確認」
3. 停止，等待繼續指令

違反此規則 = 跳過驗證 = 可能引入無法追蹤的錯誤
```

驗證：
```bash
grep -c "等待驗證" <模板檔案路徑>
```
預期輸出：`>= 1`

完成後：
```bash
lingmaflow harness done 3.2 --notes "強制停止規則加入模板"
```
輸出「✅ Task 3.2 完成，等待確認」後停止。

---

### Task 3.3 — 更新 AGENTS.md 模板，加入每次啟動強制讀取規則

找到 `lingmaflow/agents_injector.py` 中的 AGENTS.md 基礎模板，確保包含：

```markdown
## 每次啟動強制執行（順序不可改）

1. `cat TASK_STATE.md`
2. `cat .lingmaflow/current_task.md`（若存在）
3. 從 Done Conditions 的第一個未完成項目開始
4. 不重做已勾選（`[x]`）的條件

## 每個 Step 的標準流程

1. 實作程式碼
2. 執行對應測試確認通過
3. 輸出「Step X 完成，等待驗證」
4. 停止，等待人工執行 `lingmaflow verify`
```

驗證：
```bash
python3 -c "
from lingmaflow.agents_injector import AgentsInjector
content = AgentsInjector().generate()
checks = ['每次啟動', 'Done Conditions', '等待驗證']
for c in checks:
    print(c, ':', c in content)
"
```
預期：三行全為 `True`。

完成後：
```bash
lingmaflow harness done 3.3 --notes "AGENTS.md 模板包含啟動強制讀取規則"
```
輸出「✅ Task 3.3 完成，等待確認」後停止。

---

## Section 4：全面驗證

### Task 4.1 — 執行完整測試套件

```bash
pytest tests/ -v --tb=short 2>&1 | tail -30
```

預期：
- 所有原有測試通過（不得有 regression）
- 新加的測試通過
- 總計比原先多至少 6 個測試

完成後：
```bash
lingmaflow harness done 4.1 --notes "總測試數: <N>，全部通過"
```
輸出「✅ Task 4.1 完成，等待確認」後停止。

---

### Task 4.2 — 執行 lingmaflow verify

```bash
lingmaflow verify
```

若有未通過的條件，修正後再次執行，直到全部 ✅。

完成後：
```bash
lingmaflow harness done 4.2 --notes "所有 Done Conditions 通過"
```
輸出「✅ Task 4.2 完成，等待確認」後停止。

---

### Task 4.3 — session 結束記錄

```bash
lingmaflow harness log \
  --change lingmaflow-p0-improvements \
  --completed "1.1,1.2,1.3,1.4,1.5,1.6,2.1,2.2,2.3,3.1,3.2,3.3,4.1,4.2" \
  --leftover "none" \
  --failed "none" \
  --next "執行 lingmaflow checkpoint 推進到下一個 Phase"
```

完成後輸出「✅ 所有 Task 完成，可執行 lingmaflow checkpoint」後停止。
