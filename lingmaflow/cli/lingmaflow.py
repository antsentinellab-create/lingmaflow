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
        injector.inject(output_path)
        
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

@cli.command('prepare')
@click.option('--path', '-p', default='.', help='Path to project directory (default: current directory)')
def prepare(path):
    """Prepare current task context with skill references.
    
    Reads TASK_STATE.md and generates .lingmaflow/current_task.md
    with step info, done conditions, and matching skill content.
    """
    try:
        project_path = Path(path).resolve()
        task_state_file = project_path / 'TASK_STATE.md'
        
        if not task_state_file.exists():
            click.echo(f"Error: TASK_STATE.md not found in {project_path}", err=True)
            sys.exit(1)
        
        # Load task state
        manager = TaskStateManager(task_state_file)
        manager.load()
        
        # Get conditions
        conditions = manager.get_conditions()
        
        # Match skills based on next_action
        skills_path = project_path / 'lingmaflow' / 'skills'
        if not skills_path.exists():
            skills_path = project_path / 'skills'
        
        matched_skills = []
        if skills_path.exists() and manager.state.next_action:
            registry = SkillRegistry(skills_path)
            registry.scan()
            
            # Try to match triggers with next_action
            next_action_lower = manager.state.next_action.lower()
            for skill in registry.skills:
                for trigger in skill.triggers:
                    if trigger.lower() in next_action_lower:
                        matched_skills.append(skill)
                        break
        
        # Create .lingmaflow directory
        lingmaflow_dir = project_path / '.lingmaflow'
        lingmaflow_dir.mkdir(exist_ok=True)
        
        # Generate current_task.md
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
        
        click.echo(f"✓ Generated {output_file}")
        
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
        
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@harness.command('done')
@click.argument('task_id')
@click.option('--notes', '-n', default='', help='Notes about the task completion')
@click.option('--path', '-p', default='.', help='Path to openspec changes directory')
def harness_done(task_id, notes, path):
    """Mark a task as done.
    
    TASK_ID: The ID of the task to mark as done
    """
    try:
        # Get current change name from context or require explicit path
        project_path = Path(path).resolve()
        
        # Try to find the current change directory
        # For now, assume we're working in the current directory's openspec/changes
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True,
            cwd=project_path
        )
        
        if result.returncode != 0:
            click.echo("Error: Not in a git repository", err=True)
            sys.exit(1)
        
        # User needs to specify which change to work with
        # For simplicity, assume current working directory contains tasks.json
        import os
        cwd = Path.cwd()
        if (cwd / 'tasks.json').exists():
            change_dir = cwd
        elif (project_path / 'openspec' / 'changes').exists():
            # Need to specify change name - use environment variable or error
            change_name = os.environ.get('HARNESS_CHANGE_NAME')
            if not change_name:
                click.echo("Error: Please set HARNESS_CHANGE_NAME environment variable or run from change directory", err=True)
                sys.exit(1)
            change_dir = project_path / 'openspec' / 'changes' / change_name
        else:
            click.echo("Error: tasks.json not found", err=True)
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
@click.option('--path', '-p', default='.', help='Path to openspec changes directory')
def harness_log(completed, leftover, failed, next_step, path):
    """Log session progress to PROGRESS.md.
    
    If no options provided, enters interactive mode.
    """
    try:
        project_path = Path(path).resolve()
        
        # Get change directory
        import os
        change_name = os.environ.get('HARNESS_CHANGE_NAME')
        if change_name:
            change_dir = project_path / 'openspec' / 'changes' / change_name
        else:
            # Assume current directory
            change_dir = Path.cwd()
        
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
@click.option('--path', '-p', default='.', help='Path to openspec changes directory')
def harness_resume(path):
    """Generate resume brief for agent recovery.
    """
    try:
        project_path = Path(path).resolve()
        
        # Get change directory
        import os
        change_name = os.environ.get('HARNESS_CHANGE_NAME')
        if change_name:
            change_dir = project_path / 'openspec' / 'changes' / change_name
        else:
            change_dir = Path.cwd()
        
        manager = HarnessManager(change_dir)
        brief = manager.generate_startup_brief()
        
        click.echo(brief)
        
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@harness.command('status')
@click.option('--path', '-p', default='.', help='Path to openspec changes directory')
def harness_status(path):
    """Show harness status summary.
    """
    try:
        project_path = Path(path).resolve()
        
        # Get change directory
        import os
        change_name = os.environ.get('HARNESS_CHANGE_NAME')
        if change_name:
            change_dir = project_path / 'openspec' / 'changes' / change_name
        else:
            change_dir = Path.cwd()
        
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
        from ..core.skill_registry import SkillRegistry
        from ..core.agents_injector import AgentsInjector
        
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
