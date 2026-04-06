## 1. AGENTS.md 模板強化

- [ ] 1.1 在 `templates/AGENTS.md.j2` 中加入 `<!-- HARNESS_RULES -->` 佔位符
- [ ] 1.2 建立 `templates/harness_rules.md.j2` 獨立模板檔案,包含 harness done 與 harness log 強制規則
- [ ] 1.3 在「每次啟動強制執行」章節加入讀取 `.lingmaflow/current_task.md` 的步驟
- [ ] 1.4 測試新模板生成的 AGENTS.md 格式正確

## 2. Agents Injector 增強

- [ ] 2.1 修改 `agents_injector.generate()` 方法,加入 tasks.json 存在性檢查
- [ ] 2.2 實作 `_load_harness_rules_template()` 方法載入 harness 規則模板
- [ ] 2.3 當偵測到 tasks.json 時,將 harness 規則注入 AGENTS.md
- [ ] 2.4 編寫單元測試驗證 injector 在不同情境下的行為 (有/無 tasks.json)

## 3. CLI 指令改進 - Checkpoint 自動 Prepare

- [ ] 3.1 修改 `cli/lingmaflow.py` 的 `checkpoint()` 函數,在成功後呼叫 `ctx.invoke(prepare)`
- [ ] 3.2 加入適當的輸出提示「🔄 自動執行 prepare...」
- [ ] 3.3 處理 prepare 失敗時的降級邏輯 (顯示警告但不中斷)
- [ ] 3.4 測試 checkpoint 後 current_task.md 是否正確生成

## 4. 新增 init-phase 指令

- [ ] 4.1 建立 `templates/phases/` 目錄結構
- [ ] 4.2 建立三個內建模板: phase-b-retry-budget.yaml、phase-c-rate-limiting.yaml、phase-d-circuit-breaker.yaml
- [ ] 4.3 在 `cli/lingmaflow.py` 中新增 `init_phase()` 指令函數
- [ ] 4.4 實作 YAML 模板解析與驗證邏輯
- [ ] 4.5 實作 `--list` 參數,列出所有可用模板
- [ ] 4.6 實作 `--template` 參數,支援自訂模板路徑
- [ ] 4.7 更新 TASK_STATE.md 的 Done Conditions 區塊
- [ ] 4.8 編寫單元測試驗證模板載入與驗證

## 5. Harness Resume 增強

- [ ] 5.1 修改 `harness resume` 指令,讀取 TASK_STATE.md 獲取 Phase 資訊
- [ ] 5.2 從 tasks.json 讀取下一個未完成的 task
- [ ] 5.3 從 PROGRESS.md 解析最近的 harness log 記錄
- [ ] 5.4 整合三個來源的資訊,按照設計文件中的格式輸出
- [ ] 5.5 處理缺失檔案的降級邏輯 (PROGRESS.md 不存在等)
- [ ] 5.6 實作 `--change` 參數,支援指定 change 名稱
- [ ] 5.7 當所有 tasks 完成時顯示提示並建議 checkpoint
- [ ] 5.8 編寫單元測試驗證 resume 輸出格式

## 6. 文件與指南更新

- [ ] 6.1 更新 README.md,說明新功能的用途與使用方法
- [ ] 6.2 新增「常見問題」章節,說明 Lingma IDE agent 限制與應對策略
- [ ] 6.3 在 README 中加入 migration guide,說明現有專案如何升級 AGENTS.md
- [ ] 6.4 更新 `openspec-apply-change` 的使用建議,強調必須加入停止指令

## 7. 整合測試與驗證

- [ ] 7.1 建立測試專案,執行完整工作流程驗證所有新功能
- [ ] 7.2 驗證 harness done 在每個 task 後正確更新 tasks.json
- [ ] 7.3 驗證 checkpoint 後自動執行 prepare,current_task.md 保持最新
- [ ] 7.4 驗證 init-phase 從模板正確生成 Done Conditions
- [ ] 7.5 驗證 harness resume 輸出包含所有必要資訊
- [ ] 7.6 執行所有現有單元測試,確保向後相容
- [ ] 7.7 更新版本號為 v0.4.0
