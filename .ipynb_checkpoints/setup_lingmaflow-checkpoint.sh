#!/bin/bash
set -e

# ─────────────────────────────────────────
# LingmaFlow 專案建立腳本
# 用法：bash setup_lingmaflow.sh [github_username]
# ─────────────────────────────────────────

GITHUB_USER="${1:-your-github-username}"
PROJECT="lingmaflow"
BASE="$HOME/Applications"

echo "📁 建立專案目錄結構..."

cd "$BASE"

# 目錄結構
mkdir -p $PROJECT/{lingmaflow/{core,cli,templates},tests,docs}
mkdir -p $PROJECT/lingmaflow/skills/{brainstorming,writing-plans,test-driven-development,systematic-debugging,subagent-driven}

# Python 模組檔案
touch $PROJECT/lingmaflow/__init__.py
touch $PROJECT/lingmaflow/core/{__init__.py,task_state.py,skill_registry.py,agents_injector.py}
touch $PROJECT/lingmaflow/cli/{__init__.py,lingmaflow.py}

# Skill 文件
touch $PROJECT/lingmaflow/skills/brainstorming/SKILL.md
touch $PROJECT/lingmaflow/skills/writing-plans/SKILL.md
touch $PROJECT/lingmaflow/skills/test-driven-development/SKILL.md
touch $PROJECT/lingmaflow/skills/systematic-debugging/SKILL.md
touch $PROJECT/lingmaflow/skills/subagent-driven/SKILL.md

# 模板
touch $PROJECT/lingmaflow/templates/{AGENTS.md.j2,TASK_STATE.md.j2}

# 測試
touch $PROJECT/tests/{__init__.py,test_task_state.py,test_skill_registry.py,test_cli.py}

# 根目錄文件
touch $PROJECT/{README.md,AGENTS.md}

# ─────────────────────────────────────────
# pyproject.toml
# ─────────────────────────────────────────
cat > $PROJECT/pyproject.toml << 'TOML'
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "lingmaflow"
version = "0.1.0"
description = "Agentic development framework for Lingma IDE"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.11"
dependencies = [
    "click>=8.1",
    "jinja2>=3.1",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
]

[project.scripts]
lingmaflow = "lingmaflow.cli.lingmaflow:main"
TOML

# ─────────────────────────────────────────
# TASK_STATE.md 初始內容
# ─────────────────────────────────────────
cat > $PROJECT/TASK_STATE.md << 'STATE'
# TASK_STATE

當前步驟：STEP-01
狀態：not_started
上一步結果：專案初始化完成
下一步動作：openspec-propose lingmaflow-phase1-task-state
未解決問題：
最後更新：$(date -u +"%Y-%m-%dT%H:%M:%SZ")
STATE

# 用真實時間替換
sed -i "s/\$(date -u +\"%Y-%m-%dT%H:%M:%SZ\")/$(date -u +"%Y-%m-%dT%H:%M:%SZ")/" $PROJECT/TASK_STATE.md

# ─────────────────────────────────────────
# AGENTS.md 防迷路規則
# ─────────────────────────────────────────
cat > $PROJECT/AGENTS.md << 'AGENTS'
# LingmaFlow — Agent 執行規則

## 每次啟動必做
1. 執行：cat TASK_STATE.md
2. 確認「當前步驟」與「狀態」
3. 從未完成的 done condition 開始工作
4. 不重做已完成步驟

## Done Condition 規則
每個步驟必須全部達成才能推進：
- 對應檔案存在
- pytest 全綠
- TASK_STATE.md 已更新

## 錯誤處置
- 測試失敗：只修當前步驟，不往前推進
- 工具失敗：記錄到 TASK_STATE.md 未解決問題，停止等待
- 修正超過 3 次仍失敗：停止，標記 BLOCKED

## 禁止行為
- 不可跳過步驟
- 不可在測試未通過時更新 TASK_STATE.md
- 不可修改已完成步驟的檔案（除非明確指示）
AGENTS

# ─────────────────────────────────────────
# .gitignore
# ─────────────────────────────────────────
cat > $PROJECT/.gitignore << 'IGNORE'
__pycache__/
*.pyc
*.pyo
.venv/
venv/
dist/
build/
*.egg-info/
.pytest_cache/
.coverage
*.log
IGNORE

# ─────────────────────────────────────────
# README.md 骨架
# ─────────────────────────────────────────
cat > $PROJECT/README.md << 'README'
# LingmaFlow

> Agentic development framework for Lingma IDE — inspired by Superpowers

## 簡介

LingmaFlow 為 Lingma IDE 提供 Superpowers 等級的 agentic 開發工作流，解決：
- agent 中斷後迷路問題
- 跨 session 進度消失問題
- 測試失敗後不知下一步的問題

## 安裝

```bash
pip install lingmaflow
```

## 使用

```bash
lingmaflow init          # 初始化專案
lingmaflow status        # 查看當前狀態
lingmaflow step done     # 推進步驟
lingmaflow skill find    # 搜尋 skill
```

## License

MIT
README

# ─────────────────────────────────────────
# Git 初始化
# ─────────────────────────────────────────
echo ""
echo "🔧 初始化 Git..."

cd "$BASE/$PROJECT"
git init
git add .
git commit -m "init: lingmaflow project scaffold

- 建立完整目錄結構
- 初始化 pyproject.toml
- 加入 TASK_STATE.md 防迷路機制
- 加入 AGENTS.md 執行規則
- 建立 5 個核心 skill 佔位檔案"

# ─────────────────────────────────────────
# GitHub remote（選用）
# ─────────────────────────────────────────
echo ""
echo "🔗 設定 GitHub remote..."
echo "   若還沒建立 GitHub repo，請先到："
echo "   https://github.com/new 建立 lingmaflow"
echo ""
echo "   之後執行："
echo "   git remote add origin git@github.com:$GITHUB_USER/lingmaflow.git"
echo "   git branch -M main"
echo "   git push -u origin main"

# ─────────────────────────────────────────
# 完成摘要
# ─────────────────────────────────────────
echo ""
echo "✅ 完成！專案位置：$BASE/$PROJECT"
echo ""
echo "📂 目錄結構："
find "$BASE/$PROJECT" -not -path '*/.git/*' | sort | sed 's|[^/]*/|  |g'
echo ""
echo "🚀 下一步："
echo "   cd $BASE/$PROJECT"
echo "   /openspec-propose lingmaflow-phase1-task-state"