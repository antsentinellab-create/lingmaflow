## ADDED Requirements

### Requirement: harness init 命令

CLI 應提供 `lingmaflow harness init <change_name>` 命令，用於初始化 openspec change 的執行環境。

#### Scenario: 成功初始化 change
- **WHEN** 使用者執行 `lingmaflow harness init ai-factory-phase-b`
- **THEN** 在 `openspec/changes/ai-factory-phase-b/` 底下建立 tasks.json
- **THEN** 將現有 tasks.md 轉換為 JSON 格式（如果存在）
- **THEN** 建立空的 PROGRESS.md
- **THEN** 輸出 "✓ Initialized harness for ai-factory-phase-b"
- **THEN** 輸出 "✓ tasks.json: N tasks (M done)"
- **THEN** 執行 git commit "harness: init ai-factory-phase-b"

### Requirement: harness done 命令

CLI 應提供 `lingmaflow harness done <task_id> --notes "備註"` 命令，用於標記 task 完成。

#### Scenario: 成功標記 task 完成
- **WHEN** 使用者執行 `lingmaflow harness done 3.2 --notes "改用 tenacity"`
- **THEN** 更新 tasks.json 中 task 3.2 的 done=true
- **THEN** 記錄 completed_at timestamp
- **THEN** 輸出 "✓ task 3.2 marked done"
- **THEN** 執行 git commit "task(3.2): LLMGateway retry loop"

#### Scenario: notes 參數為可選
- **WHEN** 使用者執行 `lingmaflow harness done 3.2`（未提供 --notes）
- **THEN** 仍然成功完成 task，notes 設為空字串

### Requirement: harness log 命令

CLI 應提供 `lingmaflow harness log` 命令，用於在 session 結束前記錄決策過程。

#### Scenario: 使用參數記錄 session
- **WHEN** 使用者執行 `lingmaflow harness log --completed "3.1,3.2" --leftover "3.3 開始到一半" --failed "httpx retry 和 middleware 衝突" --next "繼續 3.3，注意 tenacity 版本"`
- **THEN** 追加 session 記錄到 PROGRESS.md
- **THEN** 執行 git commit "progress: session log"
- **THEN** 輸出確認訊息

#### Scenario: 互動式輸入（無參數時）
- **WHEN** 使用者執行 `lingmaflow harness log`（未提供參數）
- **THEN** 進入互動式提示，依序詢問 completed/leftover/failed/next_step
- **THEN** 收集完資訊後寫入 PROGRESS.md 並 commit

### Requirement: harness resume 命令

CLI 應提供 `lingmaflow harness resume` 命令，用於生成接回指令給新 session 的 agent。

#### Scenario: 輸出完整的 resume brief
- **WHEN** 使用者執行 `lingmaflow harness resume`
- **THEN** 輸出包含 "═══════════════════════════════ RESUME BRIEF ═══════════════════════════════"
- **THEN** 包含 Change name
- **THEN** 包含 "Resume from: task 3.3"（下一個未完成的 task）
- **THEN** 包含 "Last completed: task 3.2 (3.1, 3.2 done)"
- **THEN** 包含 "Context from last session:" 與失敗記錄
- **THEN** 包含 "Startup sequence:" 與 4 個步驟的命令

#### Scenario: 包含 failed_attempts
- **WHEN** PROGRESS.md 的最後一個 session 包含失敗記錄
- **THEN** resume brief 的 Context 章節列出所有失敗嘗試

### Requirement: harness status 命令

CLI 應提供 `lingmaflow harness status` 命令，用於查看當前 change 的整體進度。

#### Scenario: 顯示進度摘要
- **WHEN** 使用者執行 `lingmaflow harness status`
- **THEN** 輸出 "Change: ai-factory-phase-b-retry-budget-v7"
- **THEN** 輸出 "Progress: 12/23 tasks done (52%)"
- **THEN** 輸出 "Current: task 3.3"
- **THEN** 輸出 "Last session: 2026-04-03T14:30"
