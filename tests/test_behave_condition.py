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
    
    @patch('lingmaflow.core.condition_checker.SafeProcessRunner.run')
    def test_behave_command_not_found(self, mock_run):
        """Test behave execution when command is not installed."""
        mock_run.return_value = (False, "⚠️ Command not found: behave")
        
        checker = ConditionChecker()
        result = checker.check_behave("tests/fixtures/test_passing.feature")
        
        assert result.passed is False
        assert "command not found" in result.message.lower()
    
    def test_behave_feature_file_not_found(self):
        """Test behave check when feature file path does not exist."""
        checker = ConditionChecker()
        result = checker.check_behave("features/non_existent_file.feature")
        
        assert result.passed is False
        assert "Feature file not found" in result.message
        # Ensure we don't get a misleading "command not found" error
        assert "command not found" not in result.message.lower()
    
    @patch('lingmaflow.core.condition_checker.SafeProcessRunner.run')
    def test_behave_timeout(self, mock_run):
        """Test behave execution timeout."""
        mock_run.return_value = (False, "⏱️ Execution timed out after 300s")
        
        checker = ConditionChecker()
        result = checker.check_behave("tests/fixtures/test_passing.feature")
        
        assert result.passed is False
        assert "timed out" in result.message.lower()
    
    @patch('lingmaflow.core.condition_checker.SafeProcessRunner.run')
    def test_behave_uses_correct_command(self, mock_run):
        """Test that behave is called with correct arguments."""
        mock_run.return_value = (True, "1 scenario passed")
        
        checker = ConditionChecker()
        checker.check_behave("tests/fixtures/test_passing.feature")
        
        # Verify SafeProcessRunner was called with correct arguments
        mock_run.assert_called_once_with(['behave', 'tests/fixtures/test_passing.feature'])


class TestBehaveIntegrationWithCheckAll:
    """Test behave integration with check_all method."""
    
    @patch('lingmaflow.core.condition_checker.subprocess.Popen')
    def test_check_all_with_behave_condition(self, mock_popen):
        """Test check_all processes behave: conditions correctly."""
        # Mock successful behave execution
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        checker = ConditionChecker()
        conditions = [
            "file:test.txt",
            "behave:tests/fixtures/test_passing.feature"
        ]
        
        results = checker.check_all(conditions)
        
        assert len(results) == 2
        assert results[0].condition == "file:test.txt"
        assert results[1].condition == "behave:tests/fixtures/test_passing.feature"
        assert results[1].passed is True
    
    @patch('lingmaflow.core.condition_checker.subprocess.Popen')
    def test_check_all_mixed_pass_fail(self, mock_popen):
        """Test check_all with mix of passing and failing behave conditions."""
        # First call succeeds, second fails
        success_process = MagicMock()
        success_process.returncode = 0
        success_process.wait.return_value = 0
        
        fail_process = MagicMock()
        fail_process.returncode = 1
        fail_process.wait.return_value = 1
        
        mock_popen.side_effect = [success_process, fail_process]
        
        checker = ConditionChecker()
        conditions = [
            "behave:tests/fixtures/test_passing.feature",
            "behave:tests/fixtures/test_failing.feature"
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
    
    @patch('lingmaflow.core.condition_checker.subprocess.Popen')
    def test_factory_check_behave(self, mock_popen):
        """Test factory check method with behave condition."""
        from lingmaflow.core.condition_checker import ConditionCheckerFactory
        
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        result = ConditionCheckerFactory.check("behave:tests/fixtures/test_passing.feature")
        
        assert result.passed is True
        assert result.condition == "behave:tests/fixtures/test_passing.feature"
