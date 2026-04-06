# 當前任務

## 步驟：PHASE-7

## 說明：/openspec-apply-change lingmaflow-phase5-resilient-harness

## Done Conditions

- [ ] file:lingmaflow/core/harness.py
- [ ] func:lingmaflow.core.HarnessManager
- [ ] func:lingmaflow.core.ResumePoint
- [ ] file:tests/test_harness.py
- [ ] pytest:tests/test_harness.py
- [ ] pytest:tests/

## 參考 Skill

### subagent-driven

**Triggers:** 執行計劃, 實作, apply, 開始做, 跑任務, execute plan, implementation

**Priority:** normal

# Subagent-Driven - 計劃執行與任務管理

## 核心原則

**每次啟動先讀 TASK_STATE.md，每個任務完成後更新狀態，done condition 全部達成才推進，遇到 BLOCKED 停止等待。**

### 為什麼需要 Subagent-Driven？

- ❌ **不要**跳過任務或改變順序
- ❌ **不要**在測試失敗時繼續前進
- ✅ **要**嚴格遵循計劃
- ✅ **要**保持狀態同步

## 工作流程

### 步驟 1: 閱讀 TASK_STATE.md

**每次開始工作前，第一件事是閱讀 TASK_STATE.md。**

```markdown
# TASK_STATE

當前步驟：STEP-03
狀態：in_progress
上一步結果：Implemented feature X
下一步動作：Write tests for feature X
未解決問題：
- API response time exceeds target
最後更新：2026-04-02T10:30:00
```

**檢查要點：**
- [ ] 當前步驟是什麼？
- [ ] 目前狀態是什麼？（not_started / in_progress / blocked / done）
- [ ] 上一步的結果如何？
- [ ] 下一步應該做什麼？
- [ ] 有未解決的問題嗎？

### 步驟 2: 確認當前任務

**根據 TASK_STATE.md 確定當前要執行的任務。**

```python
# 從 tasks.md 找到對應任務
tasks = {
    "STEP-01": {"description": "Setup project", "done": True},
    "STEP-02": {"description": "Implement core logic", "done": True},
    "STEP-03": {"description": "Write tests", "done": False},  # ← 當前任務
    "STEP-04": {"description": "Deploy", "done": False},
}

current_step = "STEP-03"
current_task = tasks[current_step]
```

### 步驟 3: 執行任務

**專注於當前任務，不要被其他事情干擾。**

```markdown
## 執行原則

1. **單一任務焦點**
   - 一次只做一個任務
   - 完成後再進行下一個
   - 不要同時處理多個任務

2. **Done Condition 檢查**
   - 開始前確認 done condition
   - 完成後驗證是否達成
   - 不確定時詢問用戶

3. **時間管理**
   - 如果任務超過預期時間，記錄下來
   - 遇到困難時及早求助
   - 不要卡在同一个問題太久
```

### 步驟 4: 更新狀態

**任務完成後，立即更新 TASK_STATE.md。**

#### 使用 CLI 更新

```bash
# 推進到下一步
lingmaflow advance STEP-04 "Tests passed, ready to deploy" --path /path/to/project

# 如果遇到阻礙
lingmaflow block STEP-03 "Waiting for API credentials" --path /path/to/project

# 解決問題
lingmaflow resolve 1 --path /path/to/project
```

#### 手動更新（不推薦，除非必要）

```markdown
# TASK_STATE

當前步驟：STEP-04
狀態：in_progress
上一步結果：Tests passed ✓
下一步動作：Deploy to production
未解決問題：
最後更新：2026-04-02T11:00:00
```

### 步驟 5: 驗證 Done Condition

**在推進之前，確認所有 done condition 都已達成。**

```markdown
## Done Condition 範例

□ 程式碼已實作
□ 測試已編寫並通過
□ 文件已更新
□ Code review 已完成
□ CI/CD pipeline 通過

必須全部打勾才能推進到下一步
```

## 狀態管理

### 狀態轉換

```
not_started → in_progress → done
                  ↓
              blocked → in_progress → done
```

### 各狀態的定義

#### not_started

- 還沒有開始這個任務
- 前置條件可能還沒滿足
- 不應該開始執行

#### in_progress

- 正在執行當前任務
- 已經開始但還沒有完成
- 可以正常推進

#### blocked

- 遇到無法克服的阻礙
- 需要外部協助或資源
- 應該停止並等待

#### done

- 任務完全完成
- 所有 done condition 已達成
- 可以推進到下一步

## BLOCKED 處理

### 什麼時候標記為 BLOCKED？

```markdown
## 常見阻礙

- [x] 缺少必要的權限或帳號
- [x] 依賴的外部服務不可用
- [x] 需求不明確且無法聯絡負責人
- [x] 技術難題超出能力範圍
- [x] 缺少關鍵的硬體或軟體資源
```

### 如何標記 BLOCKED？

```bash
lingmaflow block STEP-03 "Blocked: Need database credentials from DevOps team" --path /path/to/project
```

### BLOCKED 後的行動

1. **記錄詳細信息**
   ```markdown
   ## 阻礙描述
   
   **原因:** 缺少資料庫帳號密碼
   
   **影響:** 無法執行 migration scripts
   
   **需要:** DevOps team 提供 credentials
   
   **聯絡人:** @devops-lead
   
   **緊急程度:** High
   ```

2. **通知相關人員**
   - 立即通知項目負責人
   - 在團隊頻道說明情況
   - 標記需要協助的人員

3. **停止並等待**
   - 不要嘗試繞過阻礙
   - 不要繼續執行後續任務
   - 等待阻礙解除

### 解除 BLOCKED

```bash
# 阻礙解除後
lingmaflow resolve 1 --path /path/to/project

# 然後繼續執行
lingmaflow advance STEP-03 "Database access granted, continuing..." --path /path/to/project
```

## Done Condition 檢查

### 檢查清單範例

```markdown
## Task: Implement user authentication

### Done Conditions

- [ ] User model created with email and password fields
- [ ] Registration API endpoint implemented
- [ ] Login API endpoint implemented
- [ ] Password hashing using bcrypt
- [ ] JWT token generation and validation
- [ ] Unit tests written (≥90% coverage)
- [ ] Integration tests passing
- [ ] API documentation updated
- [ ] Security review completed

必須全部打勾才能標記為 done
```

### 驗證方法

```bash
# 執行測試
pytest tests/test_authentication.py -v

# 檢查覆蓋率
pytest --cov=app/auth --cov-fail-under=90

# 執行 linting
flake8 app/auth/

# 執行 security scan
bandit -r app/auth/
```

## 與其他技能的整合

### Brainstorming → Subagent

Brainstorming 產出 proposal.md 後，才開始執行計劃。

### Writing Plans → Subagent

Writing plans 提供详细的任務列表和 done conditions。

### TDD → Subagent

每個任務執行時應用 TDD 流程。

### Debugging → Subagent

遇到問題時暫停，使用 debugging skill。

## 最佳實踐

### ✅ Do's

- 每次都從閱讀 TASK_STATE.md 開始
- 嚴格按照順序執行任務
- 完成後立即更新狀態
- 遇到阻礙時果斷標記 BLOCKED
- 保持溝通和透明度

### ❌ Don'ts

- 不要跳過任務
- 不要在測試失敗時繼續
- 不要擅自改變任務順序
- 不要隱藏問題或阻礙
- 不要同時處理多個任務

## 工具使用

### LingmaFlow CLI

```bash
# 查看當前狀態
lingmaflow status --path /path/to/project

# 推進任務
lingmaflow advance STEP-04 "All tests passed" --path /path/to/project

# 標記阻礙
lingmaflow block STEP-03 "Need API key" --path /path/to/project

# 解決問題
lingmaflow resolve 1 --path /path/to/project

# 查詢技能
lingmaflow skill find "execution" --path /path/to/project
```

### 版本控制

```bash
# 每個重要節點 commit
git add .
git commit -m "Complete STEP-03: Authentication tests"
git push origin feature-branch
```

## 追蹤進度

### 進度報告模板

```markdown
## 進度報告

**日期:** 2026-04-02
**時間:** 11:00 AM

**當前步驟:** STEP-03
**狀態:** in_progress

**今日完成:**
- [x] 實作 registration API
- [x] 編寫 unit tests
- [x] 達到 95% 覆蓋率

**下一步:**
- [ ] 實作 login API
- [ ] 編寫 integration tests

**阻礙:**
- 無
```

---

**版本:** 1.0  
**最後更新:** 2026-04-02  
**相關技能:** brainstorming, writing-plans, test-driven-development, systematic-debugging
