"""Tests for ConditionChecker module."""

import pytest
import tempfile
import os
from pathlib import Path

from lingmaflow.core.condition_checker import (
    ConditionChecker,
    ConditionResult,
    UnknownConditionTypeError,
)


class TestConditionResult:
    """Test ConditionResult dataclass."""
    
    def test_create_with_all_fields(self):
        """Test creating ConditionResult with all fields."""
        result = ConditionResult(
            passed=True,
            condition="file:test.py",
            message="File exists"
        )
        
        assert result.passed is True
        assert result.condition == "file:test.py"
        assert result.message == "File exists"
    
    def test_default_message(self):
        """Test default empty message."""
        result = ConditionResult(passed=False, condition="func:test")
        
        assert result.message == ""


class TestUnknownConditionTypeError:
    """Test UnknownConditionTypeError exception."""
    
    def test_inherits_from_exception(self):
        """Test that it inherits from Exception."""
        error = UnknownConditionTypeError("test")
        assert isinstance(error, Exception)
    
    def test_descriptive_error_message(self):
        """Test descriptive error message."""
        error = UnknownConditionTypeError("unknown type: custom")
        assert "unknown type" in str(error).lower()


class TestCheckFile:
    """Test check_file method."""
    
    def test_check_existing_file(self, tmp_path):
        """Test checking an existing file."""
        # Create a temp file
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        checker = ConditionChecker()
        result = checker.check_file(str(test_file))
        
        assert result.passed is True
        assert result.condition == f"file:{test_file}"
        assert "exists" in result.message.lower()
    
    def test_check_non_existing_file(self, tmp_path):
        """Test checking a non-existing file."""
        non_existing = tmp_path / "nonexistent.txt"
        
        checker = ConditionChecker()
        result = checker.check_file(str(non_existing))
        
        assert result.passed is False
        assert "not found" in result.message.lower()


class TestCheckPytest:
    """Test check_pytest method."""
    
    def test_check_passing_tests(self):
        """Test checking passing tests."""
        # Use the actual test file
        checker = ConditionChecker()
        result = checker.check_pytest("tests/test_condition_checker.py::TestConditionResult::test_create_with_all_fields")
        
        # Should pass since we're running a valid test
        assert result.passed is True
    
    def test_check_failing_tests(self, tmp_path):
        """Test checking failing tests."""
        # Create a test file with a failing test
        test_file = tmp_path / "test_fail.py"
        test_file.write_text("""
def test_always_fails():
    assert False, "This test always fails"
""")
        
        checker = ConditionChecker()
        result = checker.check_pytest(str(test_file))
        
        assert result.passed is False
        assert "failed" in result.message.lower()
    
    def test_check_nonexistent_path(self):
        """Test checking non-existent path."""
        checker = ConditionChecker()
        result = checker.check_pytest("nonexistent/path/test.py")
        
        assert result.passed is False


class TestCheckFunc:
    """Test check_func method."""
    
    def test_check_existing_module_class(self):
        """Test checking an existing module.class."""
        checker = ConditionChecker()
        result = checker.check_func("lingmaflow.core.TaskStateManager")
        
        assert result.passed is True
        assert "found" in result.message.lower()
    
    def test_check_nonexistent_module(self):
        """Test checking a non-existent module."""
        checker = ConditionChecker()
        result = checker.check_func("nonexistent.module.Class")
        
        assert result.passed is False
        assert "not found" in result.message.lower() or "Module not found" in result.message
    
    def test_check_existing_module_nonexistent_attr(self):
        """Test checking existing module with non-existent attribute."""
        checker = ConditionChecker()
        result = checker.check_func("lingmaflow.core.NonExistentClass")
        
        assert result.passed is False
        assert "not found" in result.message.lower()
    
    def test_check_invalid_format(self):
        """Test checking with invalid format (no dot)."""
        checker = ConditionChecker()
        result = checker.check_func("invalidformat")
        
        assert result.passed is False
        assert "Invalid format" in result.message


class TestParseCondition:
    """Test parse_condition method."""
    
    def test_parse_file_condition(self):
        """Test parsing file condition."""
        checker = ConditionChecker()
        condition_type, value = checker.parse_condition("file:path/to/file.py")
        
        assert condition_type == "file"
        assert value == "path/to/file.py"
    
    def test_parse_pytest_condition(self):
        """Test parsing pytest condition."""
        checker = ConditionChecker()
        condition_type, value = checker.parse_condition("pytest:tests/test.py")
        
        assert condition_type == "pytest"
        assert value == "tests/test.py"
    
    def test_parse_func_condition(self):
        """Test parsing func condition."""
        checker = ConditionChecker()
        condition_type, value = checker.parse_condition("func:module.Class")
        
        assert condition_type == "func"
        assert value == "module.Class"
    
    def test_parse_unknown_type(self):
        """Test parsing unknown condition type."""
        checker = ConditionChecker()
        
        with pytest.raises(UnknownConditionTypeError):
            checker.parse_condition("unknown:something")
    
    def test_parse_no_colon(self):
        """Test parsing condition without colon."""
        checker = ConditionChecker()
        
        with pytest.raises(UnknownConditionTypeError):
            checker.parse_condition("nocolon")


class TestCheckAll:
    """Test check_all method."""
    
    def test_check_all_passing(self):
        """Test checking all passing conditions."""
        checker = ConditionChecker()
        results = checker.check_all([
            "file:tests/test_condition_checker.py",
        ])
        
        assert len(results) == 1
        assert all(r.passed for r in results)
    
    def test_check_all_mixed_results(self):
        """Test checking mixed passing/failing conditions."""
        checker = ConditionChecker()
        results = checker.check_all([
            "file:tests/test_condition_checker.py",  # Should exist
            "file:nonexistent_file.txt",  # Should not exist
        ])
        
        assert len(results) == 2
        assert results[0].passed is True  # First should pass
        assert results[1].passed is False  # Second should fail
    
    def test_check_all_with_unknown_type(self):
        """Test checking with unknown condition type."""
        checker = ConditionChecker()
        results = checker.check_all([
            "file:tests/test_condition_checker.py",
            "unknown:type",
        ])
        
        assert len(results) == 2
        assert results[1].passed is False
        assert "Unknown condition type" in results[1].message


class TestAllPassed:
    """Test all_passed method."""
    
    def test_all_passed_true(self):
        """Test when all conditions pass."""
        checker = ConditionChecker()
        passed = checker.all_passed([
            "file:tests/test_condition_checker.py",
        ])
        
        assert passed is True
    
    def test_all_passed_false(self):
        """Test when any condition fails."""
        checker = ConditionChecker()
        passed = checker.all_passed([
            "file:tests/test_condition_checker.py",
            "file:nonexistent.txt",
        ])
        
        assert passed is False


class TestIntegrationWorkflow:
    """Integration tests for complete workflow."""
    
    def test_full_workflow(self, tmp_path):
        """Test complete workflow with multiple condition types."""
        # Create a test file
        test_file = tmp_path / "test_integration.py"
        test_file.write_text("""
def test_pass():
    assert True
""")
        
        checker = ConditionChecker()
        
        # Check file exists
        file_result = checker.check_file(str(test_file))
        assert file_result.passed is True
        
        # Check test passes
        pytest_result = checker.check_pytest(str(test_file))
        assert pytest_result.passed is True
        
        # Check all pass
        all_passed = checker.all_passed([
            f"file:{test_file}",
            f"pytest:{test_file}",
        ])
        assert all_passed is True
