## ADDED Requirements

### Requirement: HarnessManager 初始化 change

HarnessManager 應能初始化一個 openspec change 的執行環境，包括建立 tasks.json 和 PROGRESS.md 檔案。

#### Scenario: 成功初始化新 change
- **WHEN** 呼叫 `init_change(change_name="test-change", tasks=[...])`
- **THEN** 在 `openspec/changes/test-change/` 目錄下建立 `tasks.json` 檔案
- **THEN** 建立空的 `PROGRESS.md` 檔案
- **THEN** 執行 git commit，message 為 "harness: init test-change"

### Requirement: HarnessManager 讀取接回點

HarnessManager 應能掃描 tasks.json 和 PROGRESS.md，返回 ResumePoint 物件供 agent 接回。

#### Scenario: 找到下一個未完成的 task
- **WHEN** tasks.json 中有 task 3.3 的 done=false，且 3.1, 3.2 的 done=true
- **THEN** `get_resume_point()` 返回的 next_task_id="3.3"
- **THEN** last_completed_id="3.2"

#### Scenario: 包含最後一個 session 的 context
- **WHEN** PROGRESS.md 的最後一個 session 包含「遺留：task 3.3 開始到一半」
- **THEN** `get_resume_point()` 返回的 context 包含該遺留資訊

#### Scenario: 包含失敗記錄
- **WHEN** PROGRESS.md 的最後一個 session 包含「失敗記錄：httpx retry 和 middleware 衝突」
- **THEN** `get_resume_point()` 返回的 failed_attempts 包含 ["httpx 直接 retry 和 middleware 衝突"]

### Requirement: HarnessManager 完成 task

HarnessManager 應能在 tasks.json 中將指定 task 標記為完成，並記錄時間戳。

#### Scenario: 成功標記 task 完成
- **WHEN** 呼叫 `complete_task(task_id="3.2", notes="改用 tenacity")`
- **THEN** tasks.json 中 task 3.2 的 done=true
- **THEN** completed_at 設為當前 ISO 8601 timestamp
- **THEN** notes 欄位設為 "改用 tenacity"
- **THEN** 執行 git commit，message 為 "task(3.2): <description>"

### Requirement: HarnessManager 記錄 session

HarnessManager 應能追加 session 記錄到 PROGRESS.md，包含決策記憶。

#### Scenario: 成功追加 session log
- **WHEN** 呼叫 `log_session(completed=["3.1","3.2"], leftover="3.3 開始到一半", failed_attempts=["httpx 衝突"], next_step="繼續 3.3")`
- **THEN** 在 PROGRESS.md 末尾追加一筆 session 記錄
- **THEN** session 標題為 "## Session {ISO8601 timestamp}"
- **THEN** 包含完成清單、遺留描述、失敗記錄、下一步指示
- **THEN** 執行 git commit，message 為 "progress: session log"

### Requirement: HarnessManager 生成接回 brief

HarnessManager 應能生成給 agent 的接回指令，格式為純文字。

#### Scenario: 生成完整的 startup brief
- **WHEN** 呼叫 `generate_startup_brief()`
- **THEN** 返回字串包含 Change name
- **THEN** 包含 Resume from task ID
- **THEN** 包含 Last completed task ID
- **THEN** 包含 Context from last session（來自 PROGRESS.md）
- **THEN** 包含 Startup sequence（git log, cat PROGRESS.md, cat tasks.json 等命令）
