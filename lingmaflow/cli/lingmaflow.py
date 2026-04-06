"""
LingmaFlow CLI Tool

Command-line interface for managing LingmaFlow projects,
including task state management, skill queries, and AGENTS.md generation.
"""

import sys
from pathlib import Path

import click

from ..core.task_state import TaskStateManager, InvalidStateError, MalformedStateFileError
from ..core.skill_registry import SkillRegistry, MalformedSkillError
from ..core.agents_injector import AgentsInjector, InjectionError
from ..core.condition_checker import ConditionChecker, UnknownConditionTypeError
from ..core.harness import HarnessManager, ResumePoint


@click.group()
@click.version_option(version='0.2.0', prog_name='lingmaflow')
def cli():
    """LingmaFlow - AI Agent Workflow Management Tool.
    
    Manage your AI agent workflow with task state tracking,
    skill discovery, and automated AGENTS.md generation.
    """
    pass


# ============================================================================
# Task Management Commands
# ============================================================================

@cli.command()
@click.option('--path', '-p', default='.', help='Path to project directory (default: current directory)')
def status(path):
    """Display current task status from TASK_STATE.md."""
    try:
        project_path = Path(path).resolve()
        task_state_file = project_path / 'TASK_STATE.md'
        
        if not task_state_file.exists():
            click.echo(f"Error: TASK_STATE.md not found in {project_path}", err=True)
            sys.exit(1)
        
        manager = TaskStateManager(task_state_file)
        manager.load()
        
        # Display formatted status
        click.echo(f"Current Step: {manager.state.current_step}")
        click.echo(f"Status: {manager.state.status.value}")
        click.echo(f"Last Result: {manager.state.last_result or 'None'}")
        click.echo(f"Next Action: {manager.state.next_action or 'None'}")
        
        # 嘗試讀取 active_change，附加 harness 區塊
        active_change_file = project_path / '.lingmaflow' / 'active_change'
        if active_change_file.exists():
            try:
                active_change = active_change_file.read_text(encoding='utf-8').strip()
                change_dir = project_path / 'openspec' / 'changes' / active_change
                if change_dir.exists():
                    harness_manager = HarnessManager(change_dir)
                    hs = harness_manager.get_status()
                    if 'error' not in hs:
                        click.echo("")
                        click.echo("── Harness ──────────────────────")
                        click.echo(f"Change:       {hs['change_name']}")
                        click.echo(f"Progress:     {hs['done']}/{hs['total']} tasks ({hs['percentage']:.0f}%)")
                        click.echo(f"Current task: {hs['current_task'] or 'ALL DONE'}")
                        last_session = hs['last_session']
                        click.echo(f"Last session: {last_session if last_session != 'N/A' else 'None'}")
                        click.echo("─────────────────────────────────")
            except Exception:
                pass  # harness 區塊失敗不影響主流程

        if manager.state.unresolved:
            click.echo(f"Unresolved Issues ({len(manager.state.unresolved)}):")
            for i, issue in enumerate(manager.state.unresolved, 1):
                click.echo(f"  {i}. {issue}")
        else:
            click.echo("Unresolved Issues: None")

    except MalformedStateFileError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('next_step')
@click.argument('result', required=False, default='Step completed')
@click.option('--path', '-p', default='.', help='Path to project directory')
def advance(next_step, result, path):
    """Advance to the next step.
    
    NEXT_STEP: The next step identifier (e.g., STEP-02)
    
    RESULT: Description of what was accomplished (default: "Step completed")
    """
    try:
        project_path = Path(path).resolve()
        task_state_file = project_path / 'TASK_STATE.md'
        
        if not task_state_file.exists():
            click.echo(f"Error: TASK_STATE.md not found in {project_path}", err=True)
            sys.exit(1)
        
        manager = TaskStateManager(task_state_file)
        manager.load()
        manager.advance(next_step, result)
        manager.save(manager.state)
        
        click.echo(f"✓ Advanced to {next_step}")
        click.echo(f"  Result: {result}")
        
    except InvalidStateError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except MalformedStateFileError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('issue')
@click.option('--path', '-p', default='.', help='Path to project directory')
def block(issue, path):
    """Mark task as blocked with an issue description.
    
    ISSUE: Description of the blocking issue
    """
    try:
        project_path = Path(path).resolve()
        task_state_file = project_path / 'TASK_STATE.md'
        
        if not task_state_file.exists():
            click.echo(f"Error: TASK_STATE.md not found in {project_path}", err=True)
            sys.exit(1)
        
        manager = TaskStateManager(task_state_file)
        manager.load()
        manager.block(issue)
        manager.save(manager.state)
        
        click.echo(f"✓ Task marked as blocked")
        click.echo(f"  Issue: {issue}")
        click.echo(f"  Total unresolved: {len(manager.state.unresolved)}")
        
    except InvalidStateError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except MalformedStateFileError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('issue_number', type=int)
@click.option('--path', '-p', default='.', help='Path to project directory')
def resolve(issue_number, path):
    """Resolve a blocking issue by its number.
    
    ISSUE_NUMBER: The number of the issue to resolve (1-based index)
    """
    try:
        project_path = Path(path).resolve()
        task_state_file = project_path / 'TASK_STATE.md'
        
        if not task_state_file.exists():
            click.echo(f"Error: TASK_STATE.md not found in {project_path}", err=True)
            sys.exit(1)
        
        manager = TaskStateManager(task_state_file)
        manager.load()
        
        if not manager.state.unresolved:
            click.echo("No unresolved issues to resolve.")
            sys.exit(0)
        
        if issue_number < 1 or issue_number > len(manager.state.unresolved):
            click.echo(f"Error: Invalid issue number {issue_number}. Must be between 1 and {len(manager.state.unresolved)}.", err=True)
            sys.exit(1)
        
        resolved_issue = manager.state.unresolved[issue_number - 1]
        manager.resolve(resolved_issue)  # Pass the issue text, not index
        manager.save(manager.state)
        
        click.echo(f"✓ Resolved issue #{issue_number}: {resolved_issue}")
        click.echo(f"  Remaining unresolved: {len(manager.state.unresolved)}")
        
    except InvalidStateError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except MalformedStateFileError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Skill Query Commands
# ============================================================================

@cli.group()
def skill():
    """Query and list available skills."""
    pass


@skill.command('find')
@click.argument('keyword')
@click.option('--path', '-p', default='.', help='Path to project directory (default: current directory)')
def skill_find(keyword, path):
    """Find skills by keyword.
    
    KEYWORD: The keyword to search for in skill triggers
    """
    try:
        skills_path = Path(path).resolve() / 'lingmaflow' / 'skills'
        if not skills_path.exists():
            skills_path = Path(path).resolve() / 'skills'
        if not skills_path.exists():
            click.echo(f"No skills found. Skills directory not found: {skills_path}", err=True)
            sys.exit(0)
        
        registry = SkillRegistry(skills_path)
        registry.scan()
        
        matches = registry.find(keyword)
        
        if not matches:
            click.echo(f"No skills found matching '{keyword}'")
            sys.exit(0)
        
        click.echo(f"Found {len(matches)} skill(s) matching '{keyword}':\n")
        for skill in matches:
            triggers_str = ', '.join(skill.triggers)
            click.echo(f"- **{skill.name}**: {triggers_str}")
        
    except MalformedSkillError as e:
        click.echo(f"Error reading skill: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@skill.command('list')
@click.option('--path', '-p', default='.', help='Path to project directory (default: current directory)')
def skill_list(path):
    """List all available skills."""
    try:
        skills_path = Path(path).resolve() / 'lingmaflow' / 'skills'
        if not skills_path.exists():
            skills_path = Path(path).resolve() / 'skills'
        if not skills_path.exists():
            click.echo("No skills registered. Skills directory not found.", err=True)
            sys.exit(0)
        
        registry = SkillRegistry(skills_path)
        registry.scan()
        
        skill_names = registry.list()
        
        if not skill_names:
            click.echo("No skills registered.")
            sys.exit(0)
        
        click.echo(f"Found {len(skill_names)} skill(s):\n")
        for name in skill_names:
            click.echo(f"- {name}")
        
    except MalformedSkillError as e:
        click.echo(f"Error reading skill: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Agents Generation Commands
# ============================================================================

@cli.group()
def agents():
    """Manage AGENTS.md file."""
    pass


@agents.command('generate')
@click.option('--output', '-o', default=None, help='Output path for AGENTS.md (default: ./AGENTS.md in project path)')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing file without confirmation')
@click.option('--path', '-p', default='.', help='Path to project directory (default: current directory)')
def agents_generate(output, force, path):
    """Generate AGENTS.md file with current skills.
    
    Generates AGENTS.md with fixed execution rules and dynamic skill list.
    """
    try:
        project_path = Path(path).resolve()
        skills_path = project_path / 'skills'
        
        # Default output to project root if not specified
        if output is None:
            output_path = project_path / 'AGENTS.md'
        else:
            output_path = Path(output).resolve()
        
        # Check if file exists and warn
        if output_path.exists() and not force:
            click.confirm(f"File {output_path} already exists. Overwrite?", abort=True)
        
        # Create registry and injector
        registry = SkillRegistry(skills_path)
        registry.scan()
        
        # Get task_state_path (assume same directory as output)
        task_state_path = output_path.parent / 'TASK_STATE.md'
        
        injector = AgentsInjector(registry, task_state_path)
        injector.inject(output_path, project_path=project_path)
        
        click.echo(f"✓ Generated {output_path}")
        click.echo(f"  Skills included: {len(registry.skills)}")
        
    except InjectionError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except MalformedSkillError as e:
        click.echo(f"Error reading skill: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Execution Engine Commands (NEW in Phase 4)
# ============================================================================

def _run_prepare(project_path: Path) -> Path:
    """Core prepare logic. Extracted for reuse by checkpoint.

    Args:
        project_path: Resolved project root Path.

    Returns:
        Path of the generated current_task.md.

    Raises:
        FileNotFoundError: If TASK_STATE.md does not exist.
        Exception: Propagates any unexpected error to caller.
    """
    task_state_file = project_path / 'TASK_STATE.md'

    if not task_state_file.exists():
        raise FileNotFoundError(f"TASK_STATE.md not found in {project_path}")

    manager = TaskStateManager(task_state_file)
    manager.load()

    conditions = manager.get_conditions()

    skills_path = project_path / 'lingmaflow' / 'skills'
    if not skills_path.exists():
        skills_path = project_path / 'skills'

    matched_skills = []
    if skills_path.exists() and manager.state.next_action:
        reg = SkillRegistry(skills_path)
        reg.scan()
        next_action_lower = manager.state.next_action.lower()
        for skill in reg.skills:
            for trigger in skill.triggers:
                if trigger.lower() in next_action_lower:
                    matched_skills.append(skill)
                    break

    lingmaflow_dir = project_path / '.lingmaflow'
    lingmaflow_dir.mkdir(exist_ok=True)

    output_file = lingmaflow_dir / 'current_task.md'

    content_lines = [
        "# 當前任務\n",
        f"## 步驟：{manager.state.current_step}\n",
        f"## 說明：{manager.state.next_action or 'N/A'}\n",
        "## Done Conditions\n"
    ]

    if conditions:
        for condition in conditions:
            content_lines.append(f"- [ ] {condition}")
    else:
        content_lines.append("無\n")

    content_lines.append("\n## 參考 Skill\n")

    if matched_skills:
        for skill in matched_skills:
            content_lines.append(f"### {skill.name}\n")
            content_lines.append(f"**Triggers:** {', '.join(skill.triggers)}\n")
            content_lines.append(f"**Priority:** {skill.priority}\n")
            content_lines.append(f"{skill.content}\n")
    else:
        content_lines.append("無匹配的 skill\n")

    output_file.write_text('\n'.join(content_lines), encoding='utf-8')
    return output_file


@cli.command('prepare')
@click.option('--path', '-p', default='.', help='Path to project directory (default: current directory)')
def prepare(path):
    """Prepare current task context with skill references.
    
    Reads TASK_STATE.md and generates .lingmaflow/current_task.md
    with step info, done conditions, and matching skill content.
    """
    try:
        project_path = Path(path).resolve()
        output_file = _run_prepare(project_path)
        click.echo(f"✓ Generated {output_file}")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command('init-phase')
@click.argument('phase_name')
@click.option('--path', '-p', default='.', help='Path to project directory (default: current directory)')
@click.option('--next-action', '-n', default=None, help='下一步動作描述')
@click.option('--force', is_flag=True, default=False, help='覆蓋現有 Done Conditions 而不詢問')
def init_phase(phase_name, path, next_action, force):
    """為指定 Phase 初始化 Done Conditions 模板。

    PHASE_NAME: Phase 名稱，例如 PHASE-B、PHASE-C

    \b
    預設模板類型（依名稱自動偵測）：
      *test* / *pytest*  → pytest 模板
      *harness*          → harness 模板
      *refactor*         → refactor 模板
      其他               → 通用模板

    範例：
      lingmaflow init-phase PHASE-B
      lingmaflow init-phase PHASE-C --next-action "實作 retry 機制"
    """
    # Phase 名稱轉小寫用來偵測模板類型
    phase_lower = phase_name.lower()

    # 預設 Done Conditions 模板
    TEMPLATES = {
        'test': [
            f"file:tests/test_{phase_lower.replace('-', '_')}.py",
            f"pytest:tests/test_{phase_lower.replace('-', '_')}.py",
            "pytest:tests/",
        ],
        'harness': [
            "file:lingmaflow/core/harness.py",
            "func:lingmaflow.core.HarnessManager",
            "file:tests/test_harness.py",
            "pytest:tests/test_harness.py",
            "pytest:tests/",
        ],
        'refactor': [
            "pytest:tests/",
        ],
        'default': [
            f"file:lingmaflow/core/{phase_lower.replace('-', '_')}.py",
            f"pytest:tests/",
        ],
    }

    # 偵測模板類型
    if any(k in phase_lower for k in ('test', 'pytest')):
        template_key = 'test'
    elif 'harness' in phase_lower:
        template_key = 'harness'
    elif 'refactor' in phase_lower:
        template_key = 'refactor'
    else:
        template_key = 'default'

    conditions = TEMPLATES[template_key]

    try:
        project_path = Path(path).resolve()
        task_state_file = project_path / 'TASK_STATE.md'

        if not task_state_file.exists():
            click.echo(f"Error: TASK_STATE.md not found in {project_path}", err=True)
            sys.exit(1)

        # 讀取現有狀態
        manager = TaskStateManager(task_state_file)
        manager.load()

        # 確認是否覆蓋
        existing_conditions = manager.get_conditions()
        if existing_conditions and not force:
            click.echo(f"現有 Done Conditions ({len(existing_conditions)} 項)：")
            for c in existing_conditions:
                click.echo(f"  - {c}")
            if not click.confirm(f"覆蓋為 {phase_name} 的模板？"):
                click.echo("已取消。")
                sys.exit(0)

        # 讀取現有 TASK_STATE.md 原始內容
        raw = task_state_file.read_text(encoding='utf-8')

        # 更新當前步驟
        import re
        raw = re.sub(r'^當前步驟：.+$', f'當前步驟：{phase_name}', raw, flags=re.MULTILINE)

        # 更新狀態為 in_progress
        raw = re.sub(r'^狀態：.+$', '狀態：in_progress', raw, flags=re.MULTILINE)

        # 更新下一步動作
        if next_action:
            raw = re.sub(r'^下一步動作：.*$', f'下一步動作：{next_action}', raw, flags=re.MULTILINE)

        # 重建 Done Conditions 區塊
        conditions_block = "## Done Conditions\n"
        for cond in conditions:
            conditions_block += f"- [ ] {cond}\n"

        if "## Done Conditions" in raw:
            # 替換現有區塊（到下一個 ## 或結尾）
            raw = re.sub(
                r'## Done Conditions\n(?:- \[[ x]\] .+\n)*',
                conditions_block,
                raw
            )
        else:
            raw = raw.rstrip() + "\n" + conditions_block

        task_state_file.write_text(raw, encoding='utf-8')

        click.echo(f"✓ {phase_name} 初始化完成")
        click.echo(f"  模板類型：{template_key}")
        click.echo(f"  Done Conditions ({len(conditions)} 項)：")
        for c in conditions:
            click.echo(f"    - [ ] {c}")
        click.echo("")
        click.echo("下一步：")
        click.echo("  lingmaflow prepare")
        click.echo("  lingmaflow verify")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command('verify')
@click.option('--path', '-p', default='.', help='Path to project directory (default: current directory)')
def verify(path):
    """Verify all Done Conditions.
    
    Reads Done Conditions from TASK_STATE.md and checks each one.
    Shows ✅ for pass, ❌ for fail. Exit code 0 if all pass, 1 otherwise.
    """
    try:
        project_path = Path(path).resolve()
        task_state_file = project_path / 'TASK_STATE.md'
        
        if not task_state_file.exists():
            click.echo(f"Error: TASK_STATE.md not found in {project_path}", err=True)
            sys.exit(1)
        
        # Load and get conditions
        manager = TaskStateManager(task_state_file)
        manager.load()
        conditions = manager.get_conditions()
        
        if not conditions:
            click.echo("無 Done Conditions")
            sys.exit(0)
        
        # Check all conditions
        checker = ConditionChecker()
        results = checker.check_all(conditions)
        
        # Display results
        all_passed = True
        for result in results:
            if result.passed:
                click.echo(f"✅ {result.condition}")
            else:
                click.echo(f"❌ {result.condition}")
                click.echo(f"   {result.message}")
                all_passed = False
        
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command('checkpoint')
@click.argument('next_step')
@click.argument('result', required=False, default='Step completed')
@click.option('--commit', is_flag=True, help='Automatically git add and commit after advancing')
@click.option('--path', '-p', default='.', help='Path to project directory (default: current directory)')
def checkpoint(next_step, result, commit, path):
    """Verify conditions and auto-advance if all pass.
    
    NEXT_STEP: The next step identifier (e.g., STEP-02)
    
    If --commit flag is set, automatically runs git add and git commit.
    """
    try:
        import subprocess
        
        project_path = Path(path).resolve()
        task_state_file = project_path / 'TASK_STATE.md'
        
        if not task_state_file.exists():
            click.echo(f"Error: TASK_STATE.md not found in {project_path}", err=True)
            sys.exit(1)
        
        # Load and verify
        manager = TaskStateManager(task_state_file)
        manager.load()
        conditions = manager.get_conditions()
        
        if conditions:
            checker = ConditionChecker()
            results = checker.check_all(conditions)
            
            # Display results
            all_passed = all(cond.passed for cond in results)
            
            for cond in results:
                if cond.passed:
                    click.echo(f"✅ {cond.condition}")
                else:
                    click.echo(f"❌ {cond.condition}")
                    click.echo(f"   {cond.message}")
            
            if not all_passed:
                click.echo("\n⚠️  Not all conditions passed. Cannot advance.", err=True)
                sys.exit(1)
        
        # All passed - advance
        manager.advance(next_step, result)
        manager.save(manager.state)
        
        click.echo(f"\n✓ Advanced to {next_step}")
        
        # Auto-execute prepare after successful checkpoint
        try:
            _run_prepare(project_path)
            click.echo("📋 current_task.md 已自動更新")
        except Exception as e:
            # prepare 失敗不應中斷 checkpoint 流程
            click.echo(f"⚠️  prepare 自動執行失敗（不影響 checkpoint）: {e}")
        
        # Handle git commit if requested
        if commit:
            try:
                # Git add
                subprocess.run(['git', 'add', '.'], cwd=project_path, check=True, capture_output=True)
                
                # Git commit
                commit_msg = f"Complete {manager.state.current_step}"
                subprocess.run(
                    ['git', 'commit', '-m', commit_msg],
                    cwd=project_path,
                    check=True,
                    capture_output=True
                )
                
                click.echo(f"✓ Git commit: {commit_msg}")
                
            except subprocess.CalledProcessError as e:
                click.echo(f"⚠️  Git operation failed: {e}")
                click.echo("  Continuing anyway...")
        
    except InvalidStateError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Harness Management Commands (NEW in Phase 5)
# ============================================================================

@cli.group()
def harness():
    """Manage harness for resilient agent resume."""
    pass


@harness.command('init')
@click.argument('change_name')
@click.option('--path', '-p', default='.', help='Path to openspec changes directory (default: current directory)')
def harness_init(change_name, path):
    """Initialize harness for an openspec change.
    
    CHANGE_NAME: The name of the openspec change
    """
    try:
        project_path = Path(path).resolve()
        change_dir = project_path / 'openspec' / 'changes' / change_name
        
        if not change_dir.exists():
            click.echo(f"Error: Change directory not found: {change_dir}", err=True)
            sys.exit(1)
        
        manager = HarnessManager(change_dir)
        manager.init_change(change_name)

        # 寫入 active_change，讓 lingmaflow status 知道目前活躍的 change
        lingmaflow_dir = project_path / '.lingmaflow'
        lingmaflow_dir.mkdir(parents=True, exist_ok=True)
        (lingmaflow_dir / 'active_change').write_text(change_name, encoding='utf-8')
        click.echo(f"✓ active_change 設為 {change_name}")

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@harness.command('done')
@click.argument('task_id')
@click.option('--notes', '-n', default='', help='Notes about the task completion')
@click.option('--change', '-c', default=None, help='Change name (overrides HARNESS_CHANGE_NAME env var)')
@click.option('--path', '-p', default='.', help='Path to openspec changes directory')
def harness_done(task_id, notes, change, path):
    """Mark a task as done.
    
    TASK_ID: The ID of the task to mark as done
    """
    try:
        project_path = Path(path).resolve()
        
        # Get change directory: --change param > env var > current dir
        if change:
            change_dir = project_path / 'openspec' / 'changes' / change
        else:
            import os
            change_name = os.environ.get('HARNESS_CHANGE_NAME')
            if change_name:
                change_dir = project_path / 'openspec' / 'changes' / change_name
            else:
                # Assume current working directory contains tasks.json
                change_dir = Path.cwd()
        
        # Verify it's a valid change directory
        if not (change_dir / 'tasks.json').exists():
            click.echo("Error: tasks.json not found. Please use --change or set HARNESS_CHANGE_NAME.", err=True)
            sys.exit(1)
        
        manager = HarnessManager(change_dir)
        manager.complete_task(task_id, notes)
        
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@harness.command('log')
@click.option('--completed', '-c', default='', help='Comma-separated list of completed task IDs')
@click.option('--leftover', '-l', default='', help='Leftover task status')
@click.option('--failed', '-f', 'failed', default='', help='Failed attempts (semicolon-separated)')
@click.option('--next', '-n', 'next_step', default='', help='Next step instructions')
@click.option('--change', '--change-name', default=None, help='Change name (overrides HARNESS_CHANGE_NAME env var)')
@click.option('--path', '-p', default='.', help='Path to openspec changes directory')
def harness_log(completed, leftover, failed, next_step, change, path):
    """Log session progress to PROGRESS.md.
    
    If no options provided, enters interactive mode.
    """
    try:
        project_path = Path(path).resolve()
        
        # Get change directory: --change param > env var > current dir
        if change:
            change_dir = project_path / 'openspec' / 'changes' / change
        else:
            import os
            change_name = os.environ.get('HARNESS_CHANGE_NAME')
            if change_name:
                change_dir = project_path / 'openspec' / 'changes' / change_name
            else:
                # Assume current directory contains tasks.json
                change_dir = Path.cwd()
        
        # Verify it's a valid change directory
        if not (change_dir / 'tasks.json').exists():
            click.echo("Error: tasks.json not found. Please use --change or set HARNESS_CHANGE_NAME.", err=True)
            sys.exit(1)
        
        manager = HarnessManager(change_dir)
        
        # Interactive mode if no parameters provided
        if not any([completed, leftover, failed, next_step]):
            click.echo("Session Log (interactive mode)")
            click.echo("-" * 40)
            
            completed = click.prompt('Completed task IDs (comma-separated)', default='')
            leftover = click.prompt('Leftover task status', default='')
            failed = click.prompt('Failed attempts (semicolon-separated)', default='')
            next_step = click.prompt('Next step instructions', default='')
        
        # Parse inputs
        completed_list = [t.strip() for t in completed.split(',') if t.strip()]
        failed_list = [f.strip() for f in failed.split(';') if f.strip()]
        
        manager.log_session(
            completed=completed_list,
            leftover=leftover,
            failed_attempts=failed_list,
            next_step=next_step
        )
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@harness.command('resume')
@click.option('--change', '-c', default=None, help='Change name (overrides HARNESS_CHANGE_NAME env var)')
@click.option('--path', '-p', default='.', help='Path to openspec changes directory')
def harness_resume(change, path):
    """Generate resume brief for agent recovery.
    """
    try:
        project_path = Path(path).resolve()
        
        # Get change directory: --change param > env var > current dir
        if change:
            change_dir = project_path / 'openspec' / 'changes' / change
        else:
            import os
            change_name = os.environ.get('HARNESS_CHANGE_NAME')
            if change_name:
                change_dir = project_path / 'openspec' / 'changes' / change_name
            else:
                change_dir = Path.cwd()
        
        # Verify it's a valid change directory
        if not (change_dir / 'tasks.json').exists():
            click.echo("Error: tasks.json not found. Please use --change or set HARNESS_CHANGE_NAME.", err=True)
            sys.exit(1)
        
        manager = HarnessManager(change_dir)
        brief = manager.generate_startup_brief(project_path=project_path)
        
        click.echo(brief)
        
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@harness.command('status')
@click.option('--change', '-c', default=None, help='Change name (overrides HARNESS_CHANGE_NAME env var)')
@click.option('--path', '-p', default='.', help='Path to openspec changes directory')
def harness_status(change, path):
    """Show harness status summary.
    """
    try:
        project_path = Path(path).resolve()
        
        # Get change directory: --change param > env var > current dir
        if change:
            change_dir = project_path / 'openspec' / 'changes' / change
        else:
            import os
            change_name = os.environ.get('HARNESS_CHANGE_NAME')
            if change_name:
                change_dir = project_path / 'openspec' / 'changes' / change_name
            else:
                change_dir = Path.cwd()
        
        # Verify it's a valid change directory
        if not (change_dir / 'tasks.json').exists():
            click.echo("Error: tasks.json not found. Please use --change or set HARNESS_CHANGE_NAME.", err=True)
            sys.exit(1)
        
        manager = HarnessManager(change_dir)
        status = manager.get_status()
        
        if 'error' in status:
            click.echo(f"Error: {status['error']}", err=True)
            sys.exit(1)
        
        click.echo(f"Change: {status['change_name']}")
        click.echo(f"Progress: {status['done']}/{status['total']} tasks done ({status['percentage']:.0f}%)")
        click.echo(f"Current: task {status['current_task'] or 'N/A'}")
        click.echo(f"Last session: {status['last_session']}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Project Initialization Command
# ============================================================================

@cli.command()
@click.option('--path', '-p', default='.', help='Path to initialize project (default: current directory)')
def init(path):
    """Initialize a new LingmaFlow project.
    
    Creates the basic directory structure and initial configuration files:
    - skills/ directory for skill definitions
    - .lingma/ directory for agent configuration
    - TASK_STATE.md with initial state
    - AGENTS.md with execution rules
    """
    try:
        project_path = Path(path).resolve()
        
        # Safety check for existing files
        existing_files = []
        for item in ['TASK_STATE.md', 'AGENTS.md', 'skills', '.lingma']:
            if (project_path / item).exists():
                existing_files.append(item)
        
        if existing_files:
            click.echo(f"Warning: The following files/directories already exist:")
            for f in existing_files:
                click.echo(f"  - {f}")
            
            if not click.confirm("Continue anyway?"):
                click.echo("Aborted.")
                sys.exit(0)
        
        # Create directory structure
        skills_dir = project_path / 'skills'
        lingma_dir = project_path / '.lingma'
        
        skills_dir.mkdir(exist_ok=True)
        lingma_dir.mkdir(exist_ok=True)
        
        click.echo("✓ Created directory structure:")
        click.echo(f"  - {skills_dir}/")
        click.echo(f"  - {lingma_dir}/")
        
        # Create initial TASK_STATE.md
        task_state_content = """# TASK_STATE

當前步驟：STEP-01
狀態：not_started
上一步結果：Project initialized
下一步動作：Setup skills and configure workflow
未解決問題：
最後更新："""
        
        task_state_file = project_path / 'TASK_STATE.md'
        task_state_file.write_text(task_state_content, encoding='utf-8')
        click.echo(f"✓ Created {task_state_file}")
        
        # Create initial AGENTS.md (empty skills section)
        registry = SkillRegistry(skills_dir)
        task_state_path = task_state_file
        injector = AgentsInjector(registry, task_state_path)
        injector.inject(project_path / 'AGENTS.md')
        click.echo(f"✓ Created AGENTS.md")
        
        click.echo("\n✓ LingmaFlow project initialized successfully!")
        click.echo("\nNext steps:")
        click.echo("  1. Add skills to the skills/ directory")
        click.echo("  2. Run 'lingmaflow status' to see current state")
        click.echo("  3. Run 'lingmaflow skill list' to see available skills")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    cli()

main = cli
