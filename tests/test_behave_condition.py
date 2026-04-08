"""Tests for Behave condition checking functionality."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

from lingmaflow.core.condition_checker import (
    ConditionChecker,
    ConditionResult,
)


class TestBehaveConditionParsing:
    """Test behave: condition parsing."""
    
    def test_parse_behave_condition(self):
        """Test parsing behave: prefix correctly."""
        checker = ConditionChecker()
        condition_type, value = checker.parse_condition("behave:features/test.feature")
        
        assert condition_type == "behave"
        assert value == "features/test.feature"
    
    def test_parse_behave_condition_with_subdirectory(self):
        """Test parsing behave: with subdirectory path."""
        checker = ConditionChecker()
        condition_type, value = checker.parse_condition("behave:features/subdir/test.feature")
        
        assert condition_type == "behave"
        assert value == "features/subdir/test.feature"
    
    def test_parse_invalid_behave_condition_empty_path(self):
        """Test parsing behave: with empty path still works (validation happens later)."""
        checker = ConditionChecker()
        condition_type, value = checker.parse_condition("behave:")
        
        assert condition_type == "behave"
        assert value == ""


class TestCheckBehave:
    """Test check_behave method."""
    
    def test_behave_all_scenarios_pass(self):
        """Test behave execution when all scenarios pass (real execution)."""
        # Use real feature file from fixtures
        feature_path = "tests/fixtures/test_passing.feature"
        
        checker = ConditionChecker()
        result = checker.check_behave(feature_path)
        
        assert result.passed is True
        assert result.condition == f"behave:{feature_path}"
        assert "✅ behave passed" in result.message
    
    def test_behave_scenario_fails(self):
        """Test behave execution when scenario fails (real execution)."""
        # Use real failing feature file from fixtures
        feature_path = "tests/fixtures/test_failing.feature"
        
        checker = ConditionChecker()
        result = checker.check_behave(feature_path)
        
        assert result.passed is False
        assert result.condition == f"behave:{feature_path}"
        assert "❌ behave failed" in result.message
    
    @patch('lingmaflow.core.condition_checker.subprocess.run')
    def test_behave_command_not_found(self, mock_run):
        """Test behave execution when command is not installed."""
        # Mock FileNotFoundError
        mock_run.side_effect = FileNotFoundError("behave command not found")
        
        checker = ConditionChecker()
        result = checker.check_behave("features/test.feature")
        
        assert result.passed is False
        assert result.condition == "behave:features/test.feature"
        assert "behave command not found" in result.message
        assert "pip install behave" in result.message
    
    @patch('lingmaflow.core.condition_checker.subprocess.run')
    def test_behave_timeout(self, mock_run):
        """Test behave execution timeout."""
        # Mock TimeoutExpired
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="behave", timeout=300)
        
        checker = ConditionChecker()
        result = checker.check_behave("features/test.feature")
        
        assert result.passed is False
        assert result.condition == "behave:features/test.feature"
        assert "timed out" in result.message.lower()
    
    @patch('lingmaflow.core.condition_checker.subprocess.run')
    def test_behave_uses_correct_command(self, mock_run):
        """Test that behave is called with correct arguments."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        checker = ConditionChecker()
        checker.check_behave("features/my_test.feature")
        
        # Verify subprocess.run was called with correct arguments
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0] == ['behave', 'features/my_test.feature']
        assert call_args[1]['capture_output'] is True
        assert call_args[1]['text'] is True
        assert call_args[1]['timeout'] == 300


class TestBehaveIntegrationWithCheckAll:
    """Test behave integration with check_all method."""
    
    @patch('lingmaflow.core.condition_checker.subprocess.run')
    def test_check_all_with_behave_condition(self, mock_run):
        """Test check_all processes behave: conditions correctly."""
        # Mock successful behave execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "1 scenario passed"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        checker = ConditionChecker()
        conditions = [
            "file:test.txt",
            "behave:features/test.feature"
        ]
        
        results = checker.check_all(conditions)
        
        assert len(results) == 2
        assert results[0].condition == "file:test.txt"
        assert results[1].condition == "behave:features/test.feature"
        assert results[1].passed is True
    
    @patch('lingmaflow.core.condition_checker.subprocess.run')
    def test_check_all_mixed_pass_fail(self, mock_run):
        """Test check_all with mix of passing and failing behave conditions."""
        # First call succeeds, second fails
        success_result = MagicMock()
        success_result.returncode = 0
        success_result.stdout = ""
        success_result.stderr = ""
        
        fail_result = MagicMock()
        fail_result.returncode = 1
        fail_result.stdout = ""
        fail_result.stderr = "Scenario failed"
        
        mock_run.side_effect = [success_result, fail_result]
        
        checker = ConditionChecker()
        conditions = [
            "behave:features/pass.feature",
            "behave:features/fail.feature"
        ]
        
        results = checker.check_all(conditions)
        
        assert len(results) == 2
        assert results[0].passed is True
        assert results[1].passed is False
        assert "❌ behave failed" in results[1].message


class TestConditionCheckerFactoryWithBehave:
    """Test ConditionCheckerFactory with behave conditions."""
    
    def test_factory_create_behave_condition(self):
        """Test factory creates checker for behave: condition."""
        from lingmaflow.core.condition_checker import ConditionCheckerFactory
        
        checker, condition_type, value = ConditionCheckerFactory.create("behave:features/test.feature")
        
        assert isinstance(checker, ConditionChecker)
        assert condition_type == "behave"
        assert value == "features/test.feature"
    
    @patch('lingmaflow.core.condition_checker.subprocess.run')
    def test_factory_check_behave(self, mock_run):
        """Test factory check method with behave condition."""
        from lingmaflow.core.condition_checker import ConditionCheckerFactory
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        result = ConditionCheckerFactory.check("behave:features/test.feature")
        
        assert result.passed is True
        assert result.condition == "behave:features/test.feature"
