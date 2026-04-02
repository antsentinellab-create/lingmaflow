"""Condition Checker Module - Core validation logic for execution engine.

This module provides three verification types (file, pytest, func) to check
if Done Conditions are met.
"""

from __future__ import annotations

import importlib
import os
import subprocess
from dataclasses import dataclass


@dataclass
class ConditionResult:
    """Result of a condition check.
    
    Attributes:
        passed: Whether the condition passed
        condition: The original condition string
        message: Human-readable message about the result
    """
    passed: bool
    condition: str
    message: str = ""


class UnknownConditionTypeError(Exception):
    """Raised when an unknown condition type prefix is encountered."""
    pass


class ConditionChecker:
    """Checker for validating Done Conditions.
    
    Supports three condition types:
    - file:PATH - Check if file exists
    - pytest:PATH - Run pytest and check if tests pass
    - func:MODULE.CLASS - Check if module/class exists
    """
    
    def __init__(self):
        """Initialize the ConditionChecker."""
        pass
    
    def check_file(self, path: str) -> ConditionResult:
        """Check if a file exists.
        
        Args:
            path: Path to the file
            
        Returns:
            ConditionResult with passed=True if file exists
        """
        if os.path.exists(path):
            return ConditionResult(
                passed=True,
                condition=f"file:{path}",
                message=f"File exists: {path}"
            )
        else:
            return ConditionResult(
                passed=False,
                condition=f"file:{path}",
                message=f"File not found: {path}"
            )
    
    def check_pytest(self, path: str) -> ConditionResult:
        """Run pytest on a path and check if tests pass.
        
        Args:
            path: Path to test file or directory
            
        Returns:
            ConditionResult with passed=True if all tests pass
        """
        try:
            result = subprocess.run(
                ['pytest', path, '-v'],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return ConditionResult(
                    passed=True,
                    condition=f"pytest:{path}",
                    message=f"All tests passed: {path}"
                )
            else:
                # Count failed tests from output
                failed_count = result.stdout.count(' FAILED')
                return ConditionResult(
                    passed=False,
                    condition=f"pytest:{path}",
                    message=f"{failed_count} tests failed: {path}"
                )
        except subprocess.TimeoutExpired:
            return ConditionResult(
                passed=False,
                condition=f"pytest:{path}",
                message=f"Test execution timed out: {path}"
            )
        except FileNotFoundError:
            return ConditionResult(
                passed=False,
                condition=f"pytest:{path}",
                message=f"pytest not found or path does not exist: {path}"
            )
    
    def check_func(self, module_path: str) -> ConditionResult:
        """Check if a module.class or module.attribute exists.
        
        Args:
            module_path: Full path like "lingmaflow.core.TaskStateManager"
            
        Returns:
            ConditionResult with passed=True if module and attribute exist
        """
        try:
            # Split into module and attribute parts
            parts = module_path.rsplit('.', 1)
            if len(parts) != 2:
                return ConditionResult(
                    passed=False,
                    condition=f"func:{module_path}",
                    message=f"Invalid format. Expected MODULE.ATTRIBUTE: {module_path}"
                )
            
            module_name, attr_name = parts
            
            # Import the module
            module = importlib.import_module(module_name)
            
            # Check if attribute exists
            if hasattr(module, attr_name):
                return ConditionResult(
                    passed=True,
                    condition=f"func:{module_path}",
                    message=f"Module and attribute found: {module_path}"
                )
            else:
                return ConditionResult(
                    passed=False,
                    condition=f"func:{module_path}",
                    message=f"Attribute not found in module: {attr_name}"
                )
                
        except ImportError as e:
            return ConditionResult(
                passed=False,
                condition=f"func:{module_path}",
                message=f"Module not found: {module_name} ({str(e)})"
            )
        except Exception as e:
            return ConditionResult(
                passed=False,
                condition=f"func:{module_path}",
                message=f"Error importing module: {str(e)}"
            )
    
    def parse_condition(self, condition_str: str) -> tuple[str, str]:
        """Parse a condition string into type and value.
        
        Args:
            condition_str: String like "file:path/to/file.py"
            
        Returns:
            Tuple of (condition_type, value)
            
        Raises:
            UnknownConditionTypeError: If condition type is not recognized
        """
        if ':' not in condition_str:
            raise UnknownConditionTypeError(
                f"Invalid condition format: {condition_str}. "
                f"Expected TYPE:VALUE (e.g., file:path.py)"
            )
        
        condition_type, value = condition_str.split(':', 1)
        condition_type = condition_type.strip()
        value = value.strip()
        
        if condition_type not in ('file', 'pytest', 'func'):
            raise UnknownConditionTypeError(
                f"Unknown condition type: {condition_type}. "
                f"Supported types: file, pytest, func"
            )
        
        return condition_type, value
    
    def check_all(self, conditions: list[str]) -> list[ConditionResult]:
        """Check all conditions and return results.
        
        Args:
            conditions: List of condition strings
            
        Returns:
            List of ConditionResult objects, one per condition
        """
        results = []
        
        for condition in conditions:
            try:
                condition_type, value = self.parse_condition(condition)
                
                if condition_type == 'file':
                    result = self.check_file(value)
                elif condition_type == 'pytest':
                    result = self.check_pytest(value)
                elif condition_type == 'func':
                    result = self.check_func(value)
                else:
                    # Should not happen due to parse_condition validation
                    result = ConditionResult(
                        passed=False,
                        condition=condition,
                        message=f"Unknown condition type: {condition_type}"
                    )
                
                results.append(result)
                
            except UnknownConditionTypeError as e:
                results.append(ConditionResult(
                    passed=False,
                    condition=condition,
                    message=str(e)
                ))
            except Exception as e:
                results.append(ConditionResult(
                    passed=False,
                    condition=condition,
                    message=f"Unexpected error: {str(e)}"
                ))
        
        return results
    
    def all_passed(self, conditions: list[str]) -> bool:
        """Check if all conditions passed.
        
        Args:
            conditions: List of condition strings
            
        Returns:
            True if all conditions passed, False otherwise
        """
        results = self.check_all(conditions)
        return all(result.passed for result in results)
