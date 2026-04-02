## ADDED Requirements

### Requirement: CLI init command
系統 SHALL 提供 `lingmaflow init` 命令來初始化 LingmaFlow 專案

#### Scenario: Initialize new project
- **WHEN** 用戶執行 `lingmaflow init` 在空目錄
- **THEN** 建立基本目錄結構（skills/, .lingma/）和初始 TASK_STATE.md

#### Scenario: Initialize existing project
- **WHEN** 用戶執行 `lingmaflow init` 在已有檔案的目錄
- **THEN** 顯示警告，詢問是否繼續或跳過

#### Scenario: Init creates default files
- **WHEN** 用戶執行 `lingmaflow init`
- **THEN** 建立 TASK_STATE.md（STEP-01, not_started）、AGENTS.md、skills/ 目錄
