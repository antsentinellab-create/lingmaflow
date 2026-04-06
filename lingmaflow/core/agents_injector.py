"""
Agents Injector Module

This module provides automatic AGENTS.md generation functionality for LingmaFlow,
ensuring that agent execution rules and available skills remain synchronized with
the SkillRegistry.
"""

from pathlib import Path
from typing import List

from .skill_registry import SkillRegistry


# Harness execution rules to be injected into AGENTS.md when harness is detected
HARNESS_RULES = """
## harness 執行規則（強制，不可跳過）

### 每完成一個 task 後，立即執行
```bash
lingmaflow harness done <task_id> --notes "<關鍵決策>"
```

### session 結束前，執行
```bash
lingmaflow harness log --change <change_name> \\
  --completed "<完成的 task IDs>" \\
  --leftover "<未完成的 task>" \\
  --failed "<失敗記錄，無則填 none>" \\
  --next "<下一步指引>"
```

### 禁止行為
- 不可跳過 harness done，即使 task 很簡單
- 不可修改 tasks.json 的 id 或 description 欄位
- 不可刪除任何 task 條目
"""


class InjectionError(Exception):
    """Exception raised when AGENTS.md cannot be written to the specified path.
    
    This error occurs when the output path is not writable due to permission
    issues, missing parent directories, or other filesystem-related problems.
    """
    pass


class AgentsInjector:
    """Injector for generating and writing AGENTS.md content.
    
    This class reads from SkillRegistry and automatically generates AGENTS.md
    with up-to-date skill information and fixed execution rules.
    
    Attributes:
        registry: SkillRegistry instance containing available skills
        task_state_path: Path to the TASK_STATE.md file
    """
    
    # Fixed content sections
    FIXED_CONTENT = {
        'title': '# LingmaFlow — Agent 執行規則',
        'startup_section': '''## 每次啟動必做

1. 執行：cat TASK_STATE.md
2. 執行：cat .lingmaflow/current_task.md（若存在）
3. 確認「當前步驟」與「狀態」
4. 從未完成的 done condition 開始工作
5. 不重做已完成步驟''',
        'done_condition_section': '''## Done Condition 規則

每個步驟必須全部達成才能推進：
- 對應檔案存在
- pytest 全綠
- TASK_STATE.md 已更新''',
        'error_handling_section': '''## 錯誤處置

- 測試失敗：只修當前步驟，不往前推進
- 工具失敗：記錄到 TASK_STATE.md 未解決問題，停止等待
- 修正超過 3 次仍失敗：停止，標記 BLOCKED'''
    }
    
    def __init__(self, registry: SkillRegistry, task_state_path: Path):
        """Initialize the AgentsInjector.
        
        Args:
            registry: SkillRegistry instance containing available skills
            task_state_path: Path to the TASK_STATE.md file
        """
        self.registry = registry
        self.task_state_path = task_state_path
    
    def _has_harness(self, project_path: Path) -> bool:
        """偵測是否有任何 change 的 tasks.json 存在
        
        Args:
            project_path: Path to the project root directory
            
        Returns:
            True if any change directory contains tasks.json, False otherwise
        """
        openspec_path = project_path / "openspec" / "changes"
        if not openspec_path.exists():
            return False
        try:
            for change_dir in openspec_path.iterdir():
                if change_dir.is_dir() and (change_dir / "tasks.json").exists():
                    return True
        except PermissionError:
            return False
        return False
    
    def _generate_skill_list(self) -> str:
        """Generate the dynamic skill list section.
        
        Returns:
            Markdown formatted string of available skills
        """
        if not self.registry.skills:
            return "目前沒有可用的技能。"
        
        lines = []
        for skill in self.registry.skills:
            triggers_str = ', '.join(skill.triggers)
            lines.append(f'- **{skill.name}**: {triggers_str}')
        
        return '\n'.join(lines)
    
    def generate(self, project_path: Path = None) -> str:
        """Generate the complete AGENTS.md content.
        
        Args:
            project_path: Optional path to project root for harness detection.
                         If provided and harness is detected, HARNESS_RULES will be appended.
        
        Returns:
            Complete markdown content for AGENTS.md including
            fixed sections and dynamic skill list
        """
        skill_list = self._generate_skill_list()
        
        content = f"""{self.FIXED_CONTENT['title']}

{self.FIXED_CONTENT['startup_section']}

## 可用 Skill 清單

{skill_list}

{self.FIXED_CONTENT['done_condition_section']}

{self.FIXED_CONTENT['error_handling_section']}
"""
        
        # Append harness rules if project_path is provided and harness is detected
        if project_path is not None and self._has_harness(project_path):
            content += "\n" + HARNESS_RULES
        
        return content
    
    def inject(self, output_path: Path, project_path: Path = None) -> None:
        """Write the generated content to the specified path.
        
        Creates the file if it doesn't exist. Attempts to create
        parent directories if needed.
        
        Args:
            output_path: Path where AGENTS.md should be written
            project_path: Optional path to project root for harness detection
            
        Raises:
            InjectionError: If the path cannot be written to
        """
        try:
            # Try to create parent directories if they don't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Generate content with optional harness detection
            content = self.generate(project_path=project_path)
            
            # Write to file with UTF-8 encoding
            output_path.write_text(content, encoding='utf-8')
            
        except (PermissionError, OSError) as e:
            raise InjectionError(
                f"Cannot write to {output_path}: {e}"
            )
    
    def update(self, output_path: Path) -> None:
        """Update an existing AGENTS.md file or create new one.
        
        Overwrites the existing file if it exists, creates a new
        one if it doesn't.
        
        Args:
            output_path: Path where AGENTS.md should be written
            
        Raises:
            InjectionError: If the path cannot be written to
        """
        # For now, update behaves the same as inject
        # Always overwrites with current state
        self.inject(output_path)
