## 1. BehaveConditionChecker 實作

- [X] 1.1 在 lingmaflow/core/condition_checker.py 新增 BehaveConditionChecker class,支援 parse behave: prefix
- [X] 1.2 實作 BehaveConditionChecker.check() 方法,執行 subprocess.run(["behave", feature_path])
- [X] 1.3 處理 behave 命令不存在的異常,回傳明確錯誤訊息包含安裝指令
- [X] 1.4 將 BehaveConditionChecker 註冊至 ConditionCheckerFactory,支援 "behave:" prefix 路由
- [X] 1.5 更新 lingmaflow/core/task_state.py 的 _parse_done_conditions() 支援 behave: prefix 解析

## 2. FeatureLock 保護機制實作

- [X] 2.1 建立 lingmaflow/core/feature_lock.py 模組,實作 FeatureLock class
- [X] 2.2 實作 FeatureLock.lock(feature_path) 方法,計算 SHA256 hash 並寫入 .lingmaflow/feature_locks.json
- [X] 2.3 實作 FeatureLock.lock_all() 方法,掃描 features/ 目錄下所有 .feature 檔案並批量鎖定
- [X] 2.4 實作 FeatureLock.verify(feature_path) 方法,比對當前 hash 與記錄是否一致
- [X] 2.5 處理 feature_locks.json 不存在或格式損毀的情境,提供明確錯誤訊息與修復建議
- [X] 2.6 在 BehaveConditionChecker.check() 中,執行 behave 之前先呼叫 FeatureLock.verify()

## 3. CLI 指令擴充

- [X] 3.1 在 lingmaflow/cli/commands.py 新增 feature-lock 指令,支援單一檔案與 --all 參數
- [X] 3.2 在 lingmaflow/cli/commands.py 新增 feature-verify 指令,檢查單一檔案 hash 一致性
- [X] 3.3 為 feature-lock 指令加入成功/失敗訊息輸出,顯示 locked file count 或 hash 值
- [X] 3.4 為 feature-verify 指令加入通過/失敗訊息輸出,顯示 expected vs actual hash

## 4. AGENTS.md 模板更新

- [X] 4.1 在 lingmaflow/core/agents_injector.py 的 generate() 方法中加入 features/ 目錄偵測邏輯
- [X] 4.2 實作 inject_bdd_rules() 輔助函式,產生 BDD 驗收規則區塊內容
- [X] 4.3 確保 BDD 規則區塊插入於 Done Condition 規則之後、錯誤處置之前
- [X] 4.4 實作冪等性檢查：若 AGENTS.md 已存在 "## BDD 驗收規則" 則跳過注入
- [ ] 4.5 撰寫單元測試驗證 features/ 目錄存在與不存在時的注入行為

## 5. 單元測試撰寫

- [ ] 5.1 建立 tests/test_behave_condition.py,測試 behave: condition 解析邏輯
- [ ] 5.2 撰寫 scenario: behave 全綠時條件達成的測試案例（使用 mock subprocess）
- [ ] 5.3 撰寫 scenario: behave 失敗時條件未達成的測試案例
- [ ] 5.4 撰寫 scenario: behave 命令不存在時的錯誤處理測試案例
- [ ] 5.5 建立 tests/test_feature_lock.py,測試 FeatureLock.lock() 與 verify() 邏輯
- [ ] 5.6 撰寫 scenario: hash 一致時驗證通過的測試案例
- [ ] 5.7 撰寫 scenario: hash 不一致時驗證失敗的測試案例
- [ ] 5.8 撰寫 scenario: feature_locks.json 損毀時的錯誤處理測試案例
- [ ] 5.9 執行 pytest tests/ 確保所有新測試通過且無 regression

## 6. openspec propose 模板更新

- [ ] 6.1 找到 openspec propose 使用的 proposal.md template 檔案位置
- [ ] 6.2 在 Done Condition 區塊加入 behave: 位置提示（位於 file:/pytest: 之前）
- [ ] 6.3 在 design.md 或 proposal.md 模板中加入 feature file 命名慣例說明區塊
- [ ] 6.4 提供實際範例：ai-factory-fix-random-seed → fix_random_seed.feature
- [ ] 6.5 明確標示 behave: condition 為選擇性（僅在有 feature file 時使用）

## 7. 整合測試與文件

- [ ] 7.1 建立測試用的 features/ 目錄與簡易 feature file (features/test_passing.feature)
- [ ] 7.2 執行 `lingmaflow feature-lock features/test_passing.feature` 驗證 hash 記錄正確
- [ ] 7.3 執行 `lingmaflow verify` 驗證 behave: condition 被正確識別與執行
- [ ] 7.4 修改 test_passing.feature 內容,再次 verify 驗證 hash 不一致錯誤被觸發
- [ ] 7.5 執行 `lingmaflow agents generate` 驗證 BDD 規則區塊被正確注入 AGENTS.md
- [ ] 7.6 更新 README.md 或 docs/,說明 BDD 整合功能與使用方式
- [ ] 7.7 文件化 ai-factory 的 6 個 feature files 作為參考案例

## 8. ai-factory 實戰準備（P0）

- [ ] 8.1 解壓縮 bdd_features_all.tar.gz 到 ai-factory/features/ 目錄
- [ ] 8.2 在 ai-factory 環境中安裝 behave: pip install behave
- [ ] 8.3 在 ai-factory 每個 change 的 Done Condition 中加入對應的 behave: instruction
- [ ] 8.4 執行 `lingmaflow feature-lock --all` 鎖定 ai-factory 的所有 feature files
- [ ] 8.5 手動執行 `behave features/fix_random_seed.feature` 驗證 scenarios 可正常通過
- [ ] 8.6 記錄實戰中使用 BDD 取代 code review 的工作量節省數據
