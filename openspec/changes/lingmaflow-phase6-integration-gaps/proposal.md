## Why

LingmaFlow 在 Phase A-D 的實戰中（2026-04-03 AI-Factory 重構專案）暴露出多項整合缺口。雖然 Phase 級別的防迷路機制運作良好,但 task 級別的追蹤完全失效,導致整體價值僅發揮 40-50%。這些問題若不解決,將持續影響開發效率與可靠性。

## What Changes

- **AGENTS.md 模板強化**:加入 harness done 強制規則與 prepare 讀取要求
- **agents_injector.py 增強**:自動偵測 tasks.json 並注入 harness 規則
- **checkpoint 指令改進**:完成後自動執行 prepare,保持 current_task.md 最新
- **harness resume 整合**:輸出包含 TASK_STATE.md + tasks.json + PROGRESS.md 的完整狀態
- **新增 init-phase 指令**:從預定義模板自動產生 Done Conditions
- **使用指南更新**:明確說明 openspec-apply-change 必須加入停止指令

## Capabilities

### New Capabilities
- `harness-integration`: Agent 在每個 task 完成後強制呼叫 harness done,session 結束前執行 harness log
- `prepare-enforcement`: checkpoint 後自動執行 prepare,AGENTS.md 強制讀取 current_task.md
- `phase-initialization`: lingmaflow init-phase 指令從模板產生 Done Conditions
- `harness-resume-enhancement`: harness resume 整合多來源狀態資訊,提供完整接回指引

### Modified Capabilities
- `agents-md-injection`: agents_injector 需偵測 tasks.json 存在性,動態加入 harness 規則

## Impact

**Affected Code:**
- `lingmaflow/cli/lingmaflow.py`:新增 init-phase 指令,修改 checkpoint 邏輯
- `lingmaflow/core/agents_injector.py`:增強 generate() 方法,加入 tasks.json 偵測
- `lingmaflow/templates/AGENTS.md.j2`:加入 harness 強制規則與 prepare 讀取要求

**Affected Systems:**
- Harness 工作流:從「有建不用」變為「強制使用」
- Prepare 機制:從「可選」變為「自動執行」
- State Management:Phase 級別與 task 級別狀態開始整合

**Documentation:**
- 使用指南需說明 Lingma IDE agent 限制與應對策略
- AGENTS.md 模板更新影響所有新專案

**Breaking Changes:**
- 無 (向後相容,僅增強現有功能)
