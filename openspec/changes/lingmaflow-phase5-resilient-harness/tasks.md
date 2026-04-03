## 1. HarnessManager 核心模組

- [ ] 1.1 建立 `lingmaflow/core/harness.py` 檔案結構
- [ ] 1.2 定義 `ResumePoint` dataclass（change_name, next_task_id, last_completed_id, context, failed_attempts）
- [ ] 1.3 實現 `HarnessManager.__init__()` 和 change_dir 解析邏輯
- [ ] 1.4 實現 `init_change()` 方法：建立 tasks.json 和 PROGRESS.md，執行 git commit
- [ ] 1.5 實現 `parse_tasks_md()` 方法：將 tasks.md 轉換為 JSON 格式
- [ ] 1.6 實現 `complete_task()` 方法：更新 tasks.json，記錄 timestamp，執行 git commit
- [ ] 1.7 實現 `log_session()` 方法：追加 session 記錄到 PROGRESS.md，執行 git commit
- [ ] 1.8 實現 `get_resume_point()` 方法：掃描 tasks.json 和 PROGRESS.md，返回 ResumePoint
- [ ] 1.9 實現 `generate_startup_brief()` 方法：生成接回指令字串
- [ ] 1.10 實現 `_run_git_command()` 輔助方法：封裝 git add/commit 邏輯

## 2. CLI harness 命令群組

- [ ] 2.1 在 `lingmaflow/cli/lingmaflow.py` 新增 `harness` 子命令群組（使用 Click）
- [ ] 2.2 實現 `harness init <change_name>` 命令：呼叫 HarnessManager.init_change()
- [ ] 2.3 實現 `harness done <task_id> --notes "..."` 命令：呼叫 HarnessManager.complete_task()
- [ ] 2.4 實現 `harness log` 命令：支援參數模式和互動式模式，呼叫 HarnessManager.log_session()
- [ ] 2.5 實現 `harness resume` 命令：呼叫 HarnessManager.generate_startup_brief() 並輸出
- [ ] 2.6 實現 `harness status` 命令：計算進度百分比並輸出摘要
- [ ] 2.7 新增錯誤處理：tasks.json 不存在、git commit 失敗等情境

## 3. AGENTS.md 模板更新

- [ ] 3.1 在 `lingmaflow/templates/AGENTS.md.j2` 新增「harness 執行規則」章節
- [ ] 3.2 注入「開始新 session 時」的 startup sequence
- [ ] 3.3 注入「完成每個 task 後」的 harness done 命令規範
- [ ] 3.4 注入「session 結束前」的 harness log 命令規範
- [ ] 3.5 注入「禁止行為」清單（不可修改 id/description、不可跳過 notes 等）

## 4. 測試與驗證

- [ ] 4.1 建立 `tests/test_harness.py` 測試模組
- [ ] 4.2 測試 `test_init_change()`：驗證 tasks.json 和 PROGRESS.md 建立
- [ ] 4.3 測試 `test_complete_task()`：驗證 done flag 和 timestamp 更新
- [ ] 4.4 測試 `test_log_session()`：驗證 PROGRESS.md 內容格式正確
- [ ] 4.5 測試 `test_get_resume_point()`：驗證 ResumePoint 欄位正確
- [ ] 4.6 測試 `test_parse_tasks_md()`：驗證 Markdown → JSON 轉換邏輯
- [ ] 4.7 測試 CLI 命令：`test_harness_init`, `test_harness_done`, `test_harness_resume`
- [ ] 4.8 執行 `pytest tests/test_harness.py -v` 並確保全綠

## 5. 整合測試與文件

- [ ] 5.1 建立測試用 change：`openspec new change test-harness-integration`
- [ ] 5.2 執行 `lingmaflow harness init test-harness-integration` 驗證初始化
- [ ] 5.3 手動執行 `lingmaflow harness done 1.1 --notes "test"` 驗證 task 完成
- [ ] 5.4 執行 `lingmaflow harness resume` 驗證輸出包含正確的 next_task_id
- [ ] 5.5 執行 `lingmaflow harness resume` 驗證輸出包含 failed_attempts（如果有記錄）
- [ ] 5.6 清理測試 change：`rm -rf openspec/changes/test-harness-integration`
- [ ] 5.7 執行 `pytest tests/` 確保所有測試全綠
