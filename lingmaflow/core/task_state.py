"""
Task State Management Module

This module provides the core state management functionality for LingmaFlow,
enabling AI agents to track progress, handle errors, and maintain clear task states.
"""

from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict


class TaskStatus(Enum):
    """Enumeration of possible task states.
    
    States:
        NOT_STARTED: Task has not been started yet
        IN_PROGRESS: Task is currently being worked on
        BLOCKED: Task is blocked by an issue
        DONE: Task has been completed (terminal state)
    """
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


class InvalidStateError(Exception):
    """Exception raised when attempting an invalid state transition.
    
    This error occurs when trying to transition from a state that doesn't
    allow the requested operation, such as advancing a completed task.
    """
    pass


class MalformedStateFileError(Exception):
    """Exception raised when the state file cannot be parsed.
    
    This error occurs when the TASK_STATE.md file is missing required fields
    or contains invalid values that cannot be processed.
    """
    pass


@dataclass
class TaskState:
    """Data class to hold task state information.
    
    Attributes:
        current_step: Current step identifier (e.g., "STEP-01")
        status: Current task status
        last_result: Result from the previous step
        next_action: Next action to be taken
        unresolved: List of unresolved blocking issues
        timestamp: Last update timestamp in ISO8601 format
    """
    current_step: str = "STEP-00"
    status: TaskStatus = TaskStatus.NOT_STARTED
    last_result: str = ""
    next_action: str = ""
    unresolved: List[str] = field(default_factory=list)
    timestamp: str = ""
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class TaskStateManager:
    """Manager class for task state lifecycle.
    
    This class provides methods to load, save, advance, block, resolve, and
    complete tasks while maintaining state consistency and validation.
    
    Attributes:
        path: Path to the TASK_STATE.md file
        state: Current task state
    """
    
    def __init__(self, path: Path):
        """Initialize the TaskStateManager.
        
        Args:
            path: Path to the TASK_STATE.md file
        """
        self.path = path
        self.state: Optional[TaskState] = None
    
    def _parse_file(self, content: str) -> Dict:
        """Parse the content of a TASK_STATE.md file.
        
        Args:
            content: The markdown content to parse
            
        Returns:
            Dictionary with parsed field values
            
        Raises:
            MalformedStateFileError: If required fields are missing or invalid
        """
        fields = {
            'current_step': '',
            'status': '',
            'last_result': '',
            'next_action': '',
            'unresolved': [],
            'timestamp': ''
        }
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            # Parse key-value pairs (handle both Chinese fullwidth and English semicolon colons)
            # Check for ':' (U+003A - ASCII colon) and '：' (U+FF1A - fullwidth colon)
            has_ascii_colon = ':' in line_stripped
            has_fullwidth_colon = '：' in line_stripped
            
            if (has_ascii_colon or has_fullwidth_colon) and not line_stripped.startswith('-'):
                # Split on first colon (try ASCII first, then fullwidth)
                if has_ascii_colon:
                    parts = line_stripped.split(':', 1)
                else:
                    parts = line_stripped.split('：', 1)
                    
                if len(parts) == 2:
                    key = parts[0].strip().lower()
                    value = parts[1].strip()
                    
                    # Map Chinese keys to field names
                    if key == '當前步驟' or key == 'current_step':
                        fields['current_step'] = value
                    elif key == '狀態' or key == 'status':
                        fields['status'] = value
                    elif key == '上一步結果' or key == 'last_result':
                        fields['last_result'] = value
                    elif key == '下一步動作' or key == 'next_action':
                        fields['next_action'] = value
                    elif key == '最後更新' or key == 'timestamp' or key == '最後更新时间':
                        fields['timestamp'] = value
                    elif key == '未解決問題' or key == 'unresolved' or key == '未解决问题':
                        current_section = 'unresolved'
            elif line_stripped.startswith('- ') and current_section == 'unresolved':
                # Parse unresolved issue
                fields['unresolved'].append(line_stripped[2:])
        
        # Validate required fields
        if not fields['current_step']:
            raise MalformedStateFileError("Missing required field: 當前步驟 (current_step)")
        if not fields['status']:
            raise MalformedStateFileError("Missing required field: 狀態 (status)")
        
        # Validate status value
        valid_statuses = ['not_started', 'in_progress', 'blocked', 'done']
        if fields['status'].lower() not in valid_statuses:
            raise MalformedStateFileError(
                f"Invalid status value: '{fields['status']}'. "
                f"Must be one of: {', '.join(valid_statuses)}"
            )
        
        return fields
    
    def _format_state(self, state: TaskState) -> str:
        """Format a TaskState object as markdown content.
        
        Args:
            state: The TaskState object to format
            
        Returns:
            Formatted markdown string
        """
        lines = [
            f"當前步驟：{state.current_step}",
            f"狀態：{state.status.value}",
            f"上一步結果：{state.last_result}",
            f"下一步動作：{state.next_action}",
            "未解決問題："
        ]
        
        # Add unresolved issues
        for issue in state.unresolved:
            lines.append(f"- {issue}")
        
        lines.append(f"最後更新：{state.timestamp}")
        
        return '\n'.join(lines)
    
    def load(self) -> TaskState:
        """Load task state from file.
        
        If the file doesn't exist, creates an initial state with NOT_STARTED status.
        
        Returns:
            Loaded or newly created TaskState object
        """
        if not self.path.exists():
            # Create initial state
            self.state = TaskState(status=TaskStatus.NOT_STARTED)
            return self.state
        
        # Read and parse existing file
        content = self.path.read_text(encoding='utf-8')
        fields = self._parse_file(content)
        
        # Convert status string to enum
        status_map = {
            'not_started': TaskStatus.NOT_STARTED,
            'in_progress': TaskStatus.IN_PROGRESS,
            'blocked': TaskStatus.BLOCKED,
            'done': TaskStatus.DONE
        }
        
        self.state = TaskState(
            current_step=fields['current_step'],
            status=status_map[fields['status'].lower()],
            last_result=fields['last_result'],
            next_action=fields['next_action'],
            unresolved=fields['unresolved'],
            timestamp=fields['timestamp']
        )
        
        return self.state
    
    def save(self, state: TaskState) -> None:
        """Save task state to file.
        
        Args:
            state: The TaskState object to save
        """
        state.timestamp = datetime.now().isoformat()
        content = self._format_state(state)
        
        # Ensure parent directory exists
        self.path.parent.mkdir(parents=True, exist_ok=True)
        
        self.path.write_text(content, encoding='utf-8')
        self.state = state
    
    def advance(self, next_step: str, result: str) -> TaskState:
        """Advance to the next step.
        
        Args:
            next_step: Identifier for the next step
            result: Result from the current step
            
        Returns:
            Updated TaskState object
            
        Raises:
            InvalidStateError: If current state is DONE
        """
        if self.state is None:
            raise InvalidStateError("State not loaded. Call load() first.")
        
        if self.state.status == TaskStatus.DONE:
            raise InvalidStateError("Cannot advance from DONE state - task is complete.")
        
        self.state.current_step = next_step
        self.state.last_result = result
        self.state.status = TaskStatus.IN_PROGRESS
        self.state.timestamp = datetime.now().isoformat()
        
        return self.state
    
    def block(self, reason: str) -> TaskState:
        """Mark the task as blocked.
        
        Args:
            reason: Reason why the task is blocked
            
        Returns:
            Updated TaskState object
            
        Raises:
            InvalidStateError: If current state is DONE or NOT_STARTED
        """
        if self.state is None:
            raise InvalidStateError("State not loaded. Call load() first.")
        
        if self.state.status == TaskStatus.DONE:
            raise InvalidStateError("Cannot block a DONE task - task is already complete.")
        
        if self.state.status == TaskStatus.NOT_STARTED:
            raise InvalidStateError("Cannot block a NOT_STARTED task - start the task first.")
        
        self.state.status = TaskStatus.BLOCKED
        self.state.unresolved.append(reason)
        self.state.timestamp = datetime.now().isoformat()
        
        return self.state
    
    def resolve(self, reason: str) -> TaskState:
        """Resolve a blocking issue.
        
        Args:
            reason: The reason to remove from unresolved list
            
        Returns:
            Updated TaskState object
        """
        if self.state is None:
            raise InvalidStateError("State not loaded. Call load() first.")
        
        if self.state.status == TaskStatus.DONE:
            raise InvalidStateError("Cannot resolve a DONE task - task is already complete.")
        
        # Remove the reason from unresolved list if it exists
        if reason in self.state.unresolved:
            self.state.unresolved.remove(reason)
        
        self.state.status = TaskStatus.IN_PROGRESS
        self.state.timestamp = datetime.now().isoformat()
        
        return self.state
    
    def complete(self) -> TaskState:
        """Mark the task as complete.
        
        Returns:
            Updated TaskState object
            
        Raises:
            InvalidStateError: If current state is NOT_STARTED or BLOCKED,
                               or if there are unresolved issues
        """
        if self.state is None:
            raise InvalidStateError("State not loaded. Call load() first.")
        
        if self.state.status == TaskStatus.DONE:
            raise InvalidStateError("Task is already complete.")
        
        if self.state.status == TaskStatus.NOT_STARTED:
            raise InvalidStateError("Cannot complete a NOT_STARTED task - start the task first.")
        
        if self.state.status == TaskStatus.BLOCKED:
            raise InvalidStateError("Cannot complete a BLOCKED task - resolve blocking issues first.")
        
        # Check for any remaining unresolved issues
        if self.state.unresolved:
            raise InvalidStateError(
                f"Cannot complete task with {len(self.state.unresolved)} unresolved issue(s): "
                f"{', '.join(self.state.unresolved)}"
            )
        
        self.state.status = TaskStatus.DONE
        self.state.timestamp = datetime.now().isoformat()
        
        return self.state
    
    def is_blocked(self) -> bool:
        """Check if the task is blocked.
        
        Returns:
            True if the task is blocked, False otherwise
        """
        if self.state is None:
            return False
        return self.state.status == TaskStatus.BLOCKED
    
    def is_done(self) -> bool:
        """Check if the task is complete.
        
        Returns:
            True if the task is done, False otherwise
        """
        if self.state is None:
            return False
        return self.state.status == TaskStatus.DONE
    
    def get_conditions(self) -> list[str]:
        """Get all Done Conditions from the state file.
        
        Returns:
            List of condition strings (without checkbox markers).
            Empty list if no Done Conditions block exists.
        """
        if self.state is None:
            raise InvalidStateError("State not loaded. Call load() first.")
        
        if not self.path.exists():
            return []
        
        content = self.path.read_text(encoding='utf-8')
        conditions = []
        
        # Find Done Conditions block
        lines = content.split('\n')
        in_conditions_block = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Check for Done Conditions header
            if line_stripped.startswith('## Done Conditions') or line_stripped.startswith('## 完成條件'):
                in_conditions_block = True
                continue
            
            # Exit block when encountering next section
            if in_conditions_block and line_stripped.startswith('## '):
                break
            
            # Parse checkbox items
            if in_conditions_block and line_stripped.startswith('- ['):
                # Extract condition text (remove checkbox)
                if line_stripped.startswith('- [ ] ') or line_stripped.startswith('- [x] '):
                    condition = line_stripped[6:].strip()
                    if condition:  # Only add non-empty conditions
                        conditions.append(condition)
        
        return conditions
    
    def mark_condition_done(self, condition: str) -> None:
        """Mark a specific condition as done.
        
        Args:
            condition: The condition string to mark as done
            
        Raises:
            ValueError: If condition is not found in the list
        """
        if self.state is None:
            raise InvalidStateError("State not loaded. Call load() first.")
        
        if not self.path.exists():
            raise ValueError(f"Condition not found: {condition}")
        
        content = self.path.read_text(encoding='utf-8')
        lines = content.split('\n')
        new_lines = []
        found = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # Check if this line contains our condition
            if condition in line_stripped and (line_stripped.startswith('- [ ] ') or line_stripped.startswith('- [x] ')):
                # Replace unchecked with checked
                if line_stripped.startswith('- [ ] '):
                    # Preserve original indentation
                    indent = len(line) - len(line.lstrip())
                    new_line = ' ' * indent + '- [x] ' + condition
                    new_lines.append(new_line)
                    found = True
                    continue
            
            new_lines.append(line)
        
        if not found:
            raise ValueError(f"Condition not found: {condition}")
        
        # Write updated content
        new_content = '\n'.join(new_lines)
        self.path.write_text(new_content, encoding='utf-8')
    
    def all_conditions_done(self) -> bool:
        """Check if all Done Conditions are marked as done.
        
        Returns:
            True if all conditions are [x], False if any are [ ].
            Returns True for empty conditions list (vacuous truth).
        """
        conditions = self.get_conditions()
        
        if not conditions:
            return True  # No conditions = vacuously true
        
        if not self.path.exists():
            return False
        
        content = self.path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Check each condition in the file
        for condition in conditions:
            found_checked = False
            
            for line in lines:
                line_stripped = line.strip()
                if condition in line_stripped:
                    if line_stripped.startswith('- [x] '):
                        found_checked = True
                        break
                    elif line_stripped.startswith('- [ ] '):
                        return False  # Found unchecked condition
            
            if not found_checked:
                return False  # Condition not found or not checked
        
        return True
