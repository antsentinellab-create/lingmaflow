## Context

**Background**: LingmaFlow 是一個基於 openspec 的任務管理系統，用於追蹤 AI agent 在執行長任務時的進度。目前使用 Markdown checkbox 格式的 tasks.md 和 TASK_STATE.md 記錄狀態。

**Current state**: 
- tasks.md 使用 `- [x]` 格式記錄 task 完成狀態
- TASK_STATE.md 記錄 PHASE 級別的進度
- 中斷後 agent 只能靠 grep 猜測做到哪裡
- 缺乏決策記憶（為什麼這樣做、嘗試過什麼、失敗經驗）

**Constraints**:
- 必須向後相容於現有 openspec 工作流
- 不能破壞 phase4 的 verify/checkpoint 機制
- 需要 git 作為最終的狀態儲存（最可靠）

**Stakeholders**: 所有使用 LingmaFlow 執行長任務的 AI agents

## Goals / Non-Goals

**Goals:**
- 實現三層狀態架構（TASK_STATE.md → tasks.json → PROGRESS.md）
- 提供標準化的接回流程（startup sequence）
- 記錄決策記憶防止重複踩坑
- 透過 git commit per task 確保狀態可追溯
- CLI harness 命令能正確管理 tasks.json 和 PROGRESS.md

**Non-Goals:**
- 不修改現有 TASK_STATE.md 格式（維持 PHASE 粒度）
- 不改變 openspec-apply-change 的核心邏輯
- 不影響 phase4 的 condition verification

## Decisions

### Decision 1: JSON vs Markdown for tasks

**選擇**: 使用 JSON 格式取代 Markdown checkbox

**Rationale**:
- Anthropic 實測：JSON 比 Markdown 更穩定，agent 比較不會亂動結構化欄位
- JSON 支援 timestamp 記錄（started_at/completed_at）
- 更容易解析和驗證 schema
- 可以保留 tasks.md 作為備份（tasks.md.bak）

**Alternatives considered**:
- YAML：雖然也可讀，但需要額外 dependency
- 維持 Markdown：已被證明不穩定，容易誤改

### Decision 2: Session log 格式設計

**選擇**: PROGRESS.md 使用 Markdown 格式，每個 session 一個 section

**Rationale**:
- Markdown 易於人類閱讀和編輯
- 追加寫入模式，不需要修改歷史記錄
- 最後一個 session 包含最重要的「遺留」和「失敗記錄」

**Required fields**:
- 完成：list of task IDs
- 遺留：當前進行中的 task 狀態
- 失敗記錄：嘗試過但失敗的方案（必填，防止重複踩坑）
- 下一步：具體指示

### Decision 3: Git commit 策略

**選擇**: 每個操作都執行 git commit

**Commit messages**:
- `harness: init <change_name>` - 初始化
- `task(<task_id>): <description>` - 完成 task
- `progress: session log` - 記錄 session

**Rationale**:
- Git 是最可靠的狀態儲存
- 每個 commit 都是 checkpoint
- 方便 rollback 和審計

**Alternatives considered**:
- 只在 change 完成時 commit：失去中間狀態的可追溯性
- 使用資料庫：增加複雜度，不必要

### Decision 4: ResumePoint dataclass 設計

**選擇**: 使用 Python dataclass 封裝接回資訊

```python
@dataclass
class ResumePoint:
    change_name: str
    next_task_id: str
    last_completed_id: str
    context: str
    failed_attempts: list[str]
```

**Rationale**:
- Type-safe 的回傳值
- 明確的介面契約
- 方便測試和驗證

## Risks / Trade-offs

**[Risk]** Agent 可能忘記執行 `harness done` 就宣告 task 完成  
→ **Mitigation**: AGENTS.md 明確規範禁止行為，並在 `harness resume` 時驗證一致性

**[Risk]** PROGRESS.md 可能變得過長  
→ **Mitigation**: 只記錄最後一個 session 的關鍵資訊，歷史記錄在 git 中可查

**[Risk]** tasks.json 與 tasks.md 可能不同步  
→ **Mitigation**: `harness init` 自動轉換並建立 tasks.md.bak，之後以 tasks.json 為準

**[Risk]** 增加 git commit 頻率可能影響效能  
→ **Mitigation**: Git commit 非常快（<10ms），相對於 agent 執行時間可忽略

**[Trade-off]** 增加認知負擔：agent 需要學習新的 harness 命令  
→ **Benefit**: 長任務成功率大幅提升，避免重複踩坑

## Migration Plan

**Step 1**: 實現 HarnessManager 核心模組
- 建立 `lingmaflow/core/harness.py`
- 實現 `init_change`, `complete_task`, `log_session`, `generate_startup_brief`
- 實現 `get_resume_point` 返回 ResumePoint

**Step 2**: 實現 CLI harness 命令
- 在 `lingmaflow/cli/lingmaflow.py` 新增 `harness` 子命令群組
- 實現 `init`, `done`, `log`, `resume`, `status` 子命令

**Step 3**: 更新 AGENTS.md 模板
- 在 `lingmaflow/templates/AGENTS.md.j2` 注入 harness 執行規則

**Step 4**: 建立測試
- 建立 `tests/test_harness.py`
- 測試 HarnessManager 的核心功能
- 測試 tasks.md → tasks.json 轉換

**Step 5**: 文件與整合
- 更新 README.md（可選）
- 與 openspec-apply-change 整合測試

**Rollback strategy**: 如果發現嚴重 bug，刪除 tasks.json 和 PROGRESS.md，回復使用 tasks.md

## Open Questions

無（所有設計決策已確定）
