# lingmaflow-p0-improvements

## 概述

修正 AI-Factory Phase A-D 實戰（2026-04-03）發現的三個 P0 問題。
核心診斷：harness 系統有建但沒有用（使用率 0%），lingmaflow 整體價值只發揮 40-50%。

## 問題

| # | 問題 | 根因 | 影響 |
|---|------|------|------|
| P0-1 | harness done 從未被呼叫 | AGENTS.md 沒有強制規則 | 中斷後無法精確接回 |
| P0-2 | prepare 只用了 1 次 | checkpoint 後不自動更新 | current_task.md 過期 |
| P0-3 | agent 跳過 verify 自行繼續 | 指令模板缺停止規則 | Done Conditions 沒驗證就推進 |

## 變更範圍

- `lingmaflow/agents_injector.py`：新增 _has_harness() + HARNESS_RULES 注入
- `lingmaflow/cli.py` 或 checkpoint handler：成功推進後自動呼叫 prepare()
- `openspec/` 指令模板：加入強制停止規則
- `tests/`：新增至少 6 個測試

## 驗收標準

- [ ] lingmaflow agents generate 在有 tasks.json 時，AGENTS.md 包含 harness 規則
- [ ] lingmaflow checkpoint 成功後，.lingmaflow/current_task.md 自動更新
- [ ] openspec-apply-change 模板包含 per-section 強制停止規則
- [ ] 所有原有測試通過（no regression）
- [ ] 新增測試 >= 6 個
