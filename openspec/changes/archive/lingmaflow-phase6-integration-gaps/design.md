## Context

LingmaFlow 目前的核心價值在於 Phase 級別的防迷路機制,透過 TASK_STATE.md、verify、checkpoint 等指令確保開發不偏離軌道。但在 Phase A-D 的實戰中發現,task 級別的追蹤完全失效:

- Harness 系統已建置但未被 agent 使用 (harness done 執行 0 次)
- Prepare 機制僅在 Phase B 前執行一次,後續 Phase 被忽略
- openspec 的 task 狀態與 lingmaflow 的 Phase 狀態各自獨立
- Agent 經常違反 AGENTS.md 規則自行推進,跳過 verify 步驟

這導致中斷後的接回需要手動 grep tasks.md,可能重做已完成工作,整體價值發揮僅 40-50%。

**Constraints:**
- Lingma IDE 的 agent 不像 Claude Code 會強制讀取 AGENTS.md
- 必須向後相容,不能破壞現有專案
- 變更應集中在模板與 CLI 層,避免大幅重構核心邏輯

**Stakeholders:**
- 使用 LingmaFlow 的開發者 (需要更可靠的防迷路)
- 維護團隊 (需要清晰的實作指引)

## Goals / Non-Goals

**Goals:**
1. 讓 harness done 成為 agent 的強制行為,每個 task 完成後自動更新 tasks.json
2. 讓 prepare 機制自動化,checkpoint 後立即生成 current_task.md
3. 提供 init-phase 指令,從模板自動產生 Done Conditions,減少手動維護
4. 增強 harness resume,整合多來源狀態資訊,提供完整接回指引
5. 在 AGENTS.md 模板明確標示 Lingma IDE 的限制與應對策略

**Non-Goals:**
1. 不改變 lingmaflow 的核心狀態機架構 (Phase 級別仍是主要單位)
2. 不嘗試強制 Lingma IDE agent 遵守規則 (這是 IDE 限制,只能透過文件說明)
3. 不實作完整的 Phase 5 openspec tracker (留待未來迭代)
4. 不修改 openspec-apply-change 的行為 (只能在文件中建議使用者加入停止指令)

## Decisions

### Decision 1: AGENTS.md 模板加入強制規則區塊

**Choice:** 在 AGENTS.md.j2 模板中加入新的 `## openspec 執行強制規則` 章節,明確列出 harness done 與 harness log 的執行時機。

**Rationale:**
- Agent 需要明確的「不可跳過」指示才會執行外部指令
- 將規則放在 AGENTS.md 頂部 (每次啟動必做之後) 能提高能見度
- 使用繁體中文與現有風格一致

**Alternatives Considered:**
- ❌ 在 skill 中加入規則:Skill 是選擇性載入,不夠強制
- ❌ 依賴 agent 自行判斷:實證失敗 (Phase A-D 中 agent 違反規則至少 2 次)

### Decision 2: agents_injector 偵測 tasks.json 並動態注入規則

**Choice:** 在 `agents_injector.generate()` 方法中,檢查專案根目錄是否存在 `tasks.json`,若存在則在生成的 AGENTS.md 中加入 harness 規則區塊。

**Rationale:**
- 只有初始化過 harness 的專案才需要這些規則
- 避免在未使用 openspec 的專案中出現無關指令
- 保持模板的通用性,特定邏輯放在 injector 中

**Implementation:**
```python
# 在 generate() 中加入
tasks_json_path = os.path.join(project_root, "tasks.json")
has_harness = os.path.exists(tasks_json_path)

if has_harness:
    # 從模板片段讀取 harness 規則並插入
    harness_rules = self._load_harness_rules_template()
    content = content.replace("<!-- HARNESS_RULES -->", harness_rules)
```

### Decision 3: checkpoint 指令自動呼叫 prepare

**Choice:** 在 `cli/lingmaflow.py` 的 `checkpoint()` 函數末尾,成功更新 TASK_STATE.md 後自動呼叫 `prepare()`。

**Rationale:**
- 確保 current_task.md 始終反映最新狀態
- 減少使用者忘記執行 prepare 的機會
- prepare 是輕量操作,不會顯著影響效能

**Implementation:**
```python
@click.command()
def checkpoint():
    # ... 現有邏輯 ...
    click.echo("✅ Checkpoint 完成")
    
    # 自動執行 prepare
    click.echo("\n🔄 自動執行 prepare...")
    ctx.invoke(prepare)
```

### Decision 4: 新增 init-phase 指令

**Choice:** 建立新的 CLI 指令 `lingmaflow init-phase <phase_name>`,從預定義的 YAML 模板讀取 Done Conditions 並寫入 TASK_STATE.md。

**Rationale:**
- 解決手動維護 Done Conditions 容易遺失的問題
- 標準化各 Phase 的驗證項目
- 可擴充:未來可為不同類型的 Phase 提供不同模板

**Template Format:**
```yaml
# templates/phases/phase-b-retry-budget.yaml
phase_id: phase-b-retry-budget
done_conditions:
  - type: file
    path: workflow/retry_budget.py
  - type: pytest
    path: tests/test_retry_budget.py
  - type: pytest
    path: tests/
```

### Decision 5: harness resume 整合多來源資訊

**Choice:** 增強 `harness resume` 指令,讀取三個來源並合併輸出:
1. TASK_STATE.md:當前 Phase 與 Last Result
2. tasks.json:下一個未完成的 task
3. PROGRESS.md:上次 session 的決策記憶

**Rationale:**
- 提供完整的接回上下文,避免 agent 遺失資訊
- 減少手動查詢多個檔案的需要
- 符合「一個指令知道所有資訊」的目標

**Output Format:**
```
=== Harness Resume ===

📍 當前位置:
  Phase: PHASE-B (Retry Budget Implementation)
  Task: 3.2 (實作 retry_budget.py) [done: false]

📝 上次結果:
  Step 3.1 完成,pytest 全綠

💡 決策記憶 (from PROGRESS.md):
  - 選擇 exponential backoff 而非 fixed delay
  - 最大重試次數設為 3

🎯 下一步:
  1. 確認 workflow/retry_budget.py 存在
  2. 執行 pytest tests/test_retry_budget.py
  3. 完成後執行: lingmaflow harness done 3.2 --notes "..."
```

## Risks / Trade-offs

### Risk 1: Agent 仍可能忽略 AGENTS.md 規則

**Impact:** High  
**Mitigation:** 
- 在使用指南中明確說明這是 Lingma IDE 的限制
- 建議使用者在 openspec-apply-change 的 prompt 中加入「完成每個 Section 後停止」
- 長期可考慮開發 VSCode extension 強制讀取 AGENTS.md

### Risk 2: checkpoint 自動呼叫 prepare 可能延遲回應

**Impact:** Low  
**Mitigation:** 
- prepare 是輕量操作 (讀取檔案 + 寫入 current_task.md),通常在 100ms 內完成
- 若發現效能問題,可改為非同步執行或提供 `--no-prepare` flag

### Risk 3: init-phase 模板維護成本

**Impact:** Medium  
**Mitigation:** 
- 初期只提供少數常用 Phase 模板 (如 phase-b-retry-budget)
- 模板放在 `templates/phases/` 目錄,方便擴充
- 文件說明如何自訂模板

### Trade-off 1: 向後相容性 vs. 功能完整性

**Decision:** 優先保證向後相容,新功能以「增強」形式加入,不修改現有行為。

**Consequence:** 
- ✅ 現有專案不受影響
- ❌ 舊專案需要手動更新 AGENTS.md 才能獲得新功能
- 解決方案:提供 `lingmaflow upgrade-agents` 指令 (未來可考慮)

### Trade-off 2: 自動化 vs. 可控性

**Decision:** 在關鍵節點自動化 (如 checkpoint 後自動 prepare),但保留手動執行的能力。

**Consequence:** 
- ✅ 減少忘記執行的機會
- ❌ 使用者可能不清楚背後發生了什麼
- 解決方案:在輸出中明確標示「🔄 自動執行 prepare...」

## Migration Plan

### Phase 1: 模板與 Injector 更新 (v0.4.0)
1. 更新 `AGENTS.md.j2` 模板,加入 harness 規則佔位符
2. 修改 `agents_injector.py`,加入 tasks.json 偵測邏輯
3. 測試新專案的 AGENTS.md 生成正確

### Phase 2: CLI 指令增強 (v0.4.0)
1. 修改 `checkpoint()` 函數,加入自動 prepare 呼叫
2. 新增 `init-phase` 指令與模板系統
3. 增強 `harness resume` 輸出格式

### Phase 3: 文件與指南更新 (v0.4.0)
1. 更新 README.md,說明新功能
2. 新增「常見問題」章節,說明 Lingma IDE 限制
3. 提供 migration guide 給現有專案

### Rollback Strategy
- 所有變更都在 v0.4.0 版本中,可透過降級回 v0.3.x 復原
- 模板變更不影響已生成的 AGENTS.md
- CLI 指令新增功能都有 default behavior,不會破壞現有用法

## Open Questions

1. **是否需要提供 `lingmaflow upgrade-agents` 指令?**
   - 用於更新現有專案的 AGENTS.md
   - 可作為 v0.4.1 的增強功能

2. **init-phase 模板應該內建還是外掛?**
   - 目前決定內建在 `templates/phases/`
   - 未來可考慮支援使用者自訂模板路徑

3. **harness resume 是否需要支援 `--change` 參數?**
   - 目前設計假設單一 change
   - 若專案同時進行多個 changes,可能需要指定
