## Context

LingmaFlow 目前的 Done Condition 驗證機制（file/pytest/func）存在盲點：只能驗證結構正確性,無法確保行為正確性。Phase 6 實戰中發現 agent 可以透過建立空檔案、讓測試驗證自己、或建空函式來通過驗證,導致「達標但功能未實作」的問題。目前依賴手動二次 code review 作為補救,但這是最貴的解法且主觀不可重複。

本設計引入 BDD（Behavior-Driven Development）作為第四種驗證類型,透過使用者事先定義的 feature files 來驗證行為正確性,並加入 hash 保護機制防止 agent 修改 scenarios。

**Constraints**:
- 必須向後相容現有 file:/pytest:/func: conditions
- 不得破壞現有 openspec 格式或 TASK_STATE.md 格式
- behave package 為外部依賴,需處理未安裝情境
- Feature files 由使用者撰寫,agent 不得修改

## Goals / Non-Goals

**Goals:**
1. 提供 behave: Done Condition 類型,支援執行 behave feature files 並根據 exit code 判斷條件達成與否
2. 實現 feature file hash 保護機制,防止 agent 修改或刪除 scenarios
3. 自動在 AGENTS.md 中注入 BDD 規則（當偵測到 features/ 目錄時）
4. 更新 openspec propose 模板,提示使用者加入 behave: conditions
5. 完整單元測試覆蓋 BehaveConditionChecker 與 feature_lock 邏輯

**Non-Goals:**
- 不實作 feature file 自動生成（由使用者手寫或從 ai-factory 案例複製）
- 不修改現有 openspec spec-driven schema 結構
- 不處理 behave steps 的自動產生（steps/ 目錄由使用者維護）
- 不提供 feature file 語法檢查或 linting（behave 本身會處理）

## Decisions

### Decision 1: BehaveConditionChecker 實作方式

**Choice**: 使用 subprocess.run(["behave", feature_path]) 執行,捕捉 exit code 與 stderr

**Rationale**:
- behave CLI 已提供完整的 scenario 執行與報告功能
- 不需重新實作 Gherkin parser 或 scenario runner
- Exit code 语义明確：0 = 全綠,非 0 = 有失敗
- 可保留 behave 原生的彩色輸出與錯誤訊息

**Alternatives considered**:
- ❌ 使用 behave Python API：需處理 test runner 初始化、reporter 設定,複雜度高
- ❌ 自實作 Gherkin parser：重複造輪子,維護成本高

### Decision 2: Feature Lock Hash 儲存格式

**Choice**: 使用 SHA256 hash,儲存於 `.lingmaflow/feature_locks.json`,格式為 `{ "path": "sha256:hex" }`

**Rationale**:
- SHA256 碰撞機率極低,適合檔案完整性驗證
- JSON 格式易讀易維護,支援手動編輯（如需重置某個 file）
- `.lingmaflow/` 目錄已存在於專案結構中,符合既有慣例
- `sha256:` prefix 方便未來擴充其他 hash 演算法

**Alternatives considered**:
- ❌ 使用 git commit hash：需確保 feature files 已 commit,增加工作流程複雜度
- ❌ 使用 MD5：碰撞風險較高,安全性不足

### Decision 3: Hash 驗證時機

**Choice**: 在 BehaveConditionChecker.check() 中,執行 behave 之前先呼叫 FeatureLock.verify()

**Rationale**:
- Fail-fast 原則：若 feature file 被修改,立即報錯,不浪費時間執行 behave
- 單一責任：BehaveConditionChecker 同時負責 hash 驗證與 behave 執行,邏輯內聚
- 錯誤訊息清晰：可明確指出哪個 file 被修改,expected vs actual hash

**Alternatives considered**:
- ❌ 在 lingmaflow verify 開頭統一驗證所有 hashes：需遍歷所有 conditions 找出 behave:,增加複雜度
- ❌ 獨立的 `lingmaflow feature-verify` 指令：使用者可能忘記執行,保護效果降低

### Decision 4: AGENTS.md BDD 規則注入條件

**Choice**: 偵測 `features/` 目錄存在且包含至少一個 `.feature` 檔案時才注入

**Rationale**:
- 避免在無 BDD 需求的專案中污染 AGENTS.md
- 明確的觸發條件：有 feature files 才需要 BDD 規則
- 使用 glob 而非僅檢查目錄存在,避免誤判空目錄

**Implementation**:
```python
import glob
if os.path.exists("features/") and glob.glob("features/*.feature"):
    inject_bdd_rules(agents_md)
```

### Decision 5: Feature File 命名慣例

**Choice**: 從 change name 轉換：去掉專案前綴（如 `ai-factory-`）、連字號改底線、去掉 `-bug`/`-production` 等後綴

**Examples**:
- `ai-factory-fix-random-seed-production-bug` → `fix_random_seed.feature`
- `ai-factory-remove-dead-orchestrator` → `remove_dead_orchestrator.feature`

**Rationale**:
- 簡短有意義的名稱,易於識別對應的 change
- 底線命名符合 Python module 慣例
- 去掉冗餘後綴,聚焦核心行為

## Risks / Trade-offs

### Risk 1: behave 未安裝導致驗證失敗

**Impact**: 使用者執行 `lingmaflow verify` 時遇到 `FileNotFoundError` 或 `CommandNotFound`

**Mitigation**:
- BehaveConditionChecker.check() 捕捉 subprocess 異常,回傳明確錯誤訊息：
  ```
  ❌ behave command not found. Install with: pip install behave
  ```
- 在 proposal.md 的 Impact 區塊明確列出此依賴
- 考慮在 lingmaflow init 時檢查 behave 是否可用（optional dependency）

### Risk 2: Feature Lock Hash 不同步

**Impact**: 使用者合法更新 feature file 後,hash 不一致導致驗證失敗

**Mitigation**:
- 提供 `lingmaflow feature-lock --all` 指令快速重新鎖定所有 files
- 錯誤訊息中提供解決建議：
  ```
  Feature file has been modified. If this is intentional, run:
    lingmaflow feature-lock features/fix_random_seed.feature
  ```
- 在 AGENTS.md 中說明：只有使用者可執行 feature-lock,agent 不得執行

### Risk 3: Behave Steps 缺失導致 Scenario 失敗

**Impact**: Feature file 存在但 steps/ 目錄不完整,scenario 顯示 undefined step

**Mitigation**:
- Behave 原生會報告 undefined steps,BehaveConditionChecker 直接傳遞此錯誤
- 在 design.md 中明確：steps/ 目錄由使用者維護,不在 lingmaflow 範圍內
- ai-factory 案例已提供完整的 steps/ 實現,可直接參考

### Trade-off 1: 驗證速度 vs 保護強度

**Choice**: 每次 verify 都檢查 hash（而非快取或跳過）

**Pros**: 最大化保護,防止任何時刻的篡改
**Cons**: 每次 verify 需計算 hash（對大檔案可能有輕微效能影響）

**Justification**: Feature files 通常很小（< 5KB）,SHA256 計算耗時 < 1ms,可忽略不計。保護強度優先。

### Trade-off 2: 自動化 vs 靈活性

**Choice**: AGENTS.md 自動注入 BDD 規則,但不強制所有 changes 使用 behave:

**Pros**: 降低使用者負擔,有 features/ 即自動套用規則
**Cons**: 使用者可能不知道如何關閉（若不需要）

**Justification**: 偵測條件明確（有 feature files 才注入）,若不需要 BDD,只需移除 features/ 目錄即可。靈活性足夠。

## Migration Plan

### Phase 1: 核心功能實作（P1）
1. 實作 BehaveConditionChecker 與 feature_lock.py
2. 新增 CLI 指令 feature-lock / feature-verify
3. 撰寫單元測試 test_behave_condition.py
4. 更新 agents_injector.py 加入 BDD 規則注入

### Phase 2: 整合與文件（P2）
1. 更新 openspec propose 模板加入 behave: 提示
2. 文件化 feature file 命名慣例
3. 將 ai-factory 的 6 個 feature files 解壓縮至測試環境

### Phase 3: 實戰驗證（P0 + P3）
1. 在 ai-factory 重構案中實際使用 behave: conditions
2. 觀察 review 工作量是否減少 70%
3. 根據反饋調整 error messages 與 UX

**Rollback Strategy**:
- 若 behave 整合出現重大問題,可暫時停用 BehaveConditionChecker（comment out registration）
- Feature locks 不影響現有 workflow,可安全保留
- AGENTS.md 中的 BDD 規則區塊可手動移除

## Open Questions

1. **Feature Lock 檔案是否納入 git tracking?**
   - Option A: 加入 `.gitignore`,每個開發者本地維護
   - Option B: 納入 git,團隊共享同一份 locks
   - **Tentative decision**: Option B（納入 git）,確保團隊一致性,但需在 .gitignore 中排除其他 `.lingmaflow/` 臨時檔

2. **是否需要支援多個 features/ 目錄?**
   - 當前設計假設單一 `features/` 目錄在專案根目錄
   - 若未來需要多模組各自 features/,需調整路徑解析邏輯
   - **Tentative decision**: 暫不支援,保持簡單。若有需求再擴充

3. **Behave 輸出是否需要在 lingmaflow verify 中格式化?**
   - 當前設計直接傳遞 behave 原始輸出
   - 可考慮擷取關鍵資訊（passed/failed scenarios 數量）做摘要
   - **Tentative decision**: 先保持原始輸出,觀察使用者反饋再決定是否需要摘要
