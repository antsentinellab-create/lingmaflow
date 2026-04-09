"""Tests for FeatureLock module."""

import pytest
import tempfile
from pathlib import Path
import json

from lingmaflow.core.feature_lock import (
    FeatureLock,
    FeatureLockError,
)


class TestFeatureLockError:
    """Test FeatureLockError exception."""
    
    def test_inherits_from_exception(self):
        """Test that it inherits from Exception."""
        error = FeatureLockError("test error")
        assert isinstance(error, Exception)
    
    def test_descriptive_error_message(self):
        """Test descriptive error message."""
        error = FeatureLockError("Feature file modified")
        assert "modified" in str(error).lower()


class TestComputeHash:
    """Test compute_hash static method."""
    
    def test_compute_hash_consistent(self, tmp_path):
        """Test that hash is consistent for same content."""
        test_file = tmp_path / "test.feature"
        test_file.write_text("Feature: Test\n  Scenario: Test scenario\n")
        
        hash1 = FeatureLock.compute_hash(test_file)
        hash2 = FeatureLock.compute_hash(test_file)
        
        assert hash1 == hash2
        assert hash1.startswith("sha256:")
    
    def test_compute_hash_different_content(self, tmp_path):
        """Test that different content produces different hashes."""
        file1 = tmp_path / "file1.feature"
        file1.write_text("Feature: Test 1\n")
        
        file2 = tmp_path / "file2.feature"
        file2.write_text("Feature: Test 2\n")
        
        hash1 = FeatureLock.compute_hash(file1)
        hash2 = FeatureLock.compute_hash(file2)
        
        assert hash1 != hash2
    
    def test_compute_hash_format(self, tmp_path):
        """Test hash format includes sha256: prefix."""
        test_file = tmp_path / "test.feature"
        test_file.write_text("Feature: Test\n")
        
        hash_value = FeatureLock.compute_hash(test_file)
        
        assert hash_value.startswith("sha256:")
        assert len(hash_value) == 71  # "sha256:" (7) + hex digest (64)


class TestLock:
    """Test lock method."""
    
    def test_lock_existing_file(self, tmp_path):
        """Test locking an existing feature file."""
        # Create a feature file
        features_dir = tmp_path / "features"
        features_dir.mkdir()
        feature_file = features_dir / "test.feature"
        feature_file.write_text("Feature: Test\n  Scenario: Test\n")
        
        # Create FeatureLock instance
        lock_manager = FeatureLock(tmp_path)
        
        # Lock the file
        hash_value = lock_manager.lock("features/test.feature")
        
        assert hash_value.startswith("sha256:")
        assert "features/test.feature" in lock_manager.locks
        assert lock_manager.locks["features/test.feature"] == hash_value
        
        # Verify locks file was created
        locks_file = tmp_path / ".lingmaflow" / "feature_locks.json"
        assert locks_file.exists()
        
        # Verify locks file content
        locks_data = json.loads(locks_file.read_text())
        assert "features/test.feature" in locks_data
    
    def test_lock_non_existing_file(self, tmp_path):
        """Test locking a non-existing file raises FileNotFoundError."""
        lock_manager = FeatureLock(tmp_path)
        
        with pytest.raises(FileNotFoundError) as exc_info:
            lock_manager.lock("features/nonexistent.feature")
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_lock_multiple_files(self, tmp_path):
        """Test locking multiple feature files."""
        features_dir = tmp_path / "features"
        features_dir.mkdir()
        
        file1 = features_dir / "test1.feature"
        file1.write_text("Feature: Test 1\n")
        
        file2 = features_dir / "test2.feature"
        file2.write_text("Feature: Test 2\n")
        
        lock_manager = FeatureLock(tmp_path)
        
        hash1 = lock_manager.lock("features/test1.feature")
        hash2 = lock_manager.lock("features/test2.feature")
        
        assert len(lock_manager.locks) == 2
        assert lock_manager.locks["features/test1.feature"] == hash1
        assert lock_manager.locks["features/test2.feature"] == hash2


class TestLockAll:
    """Test lock_all method."""
    
    def test_lock_all_features(self, tmp_path):
        """Test locking all feature files in features/ directory."""
        features_dir = tmp_path / "features"
        features_dir.mkdir()
        
        # Create multiple feature files
        for i in range(3):
            feature_file = features_dir / f"test{i}.feature"
            feature_file.write_text(f"Feature: Test {i}\n")
        
        lock_manager = FeatureLock(tmp_path)
        count = lock_manager.lock_all()
        
        assert count == 3
        assert len(lock_manager.locks) == 3
    
    def test_lock_all_no_features_dir(self, tmp_path):
        """Test lock_all raises error when features/ doesn't exist."""
        lock_manager = FeatureLock(tmp_path)
        
        with pytest.raises(FeatureLockError) as exc_info:
            lock_manager.lock_all()
        
        assert "features/" in str(exc_info.value).lower()
    
    def test_lock_all_no_feature_files(self, tmp_path):
        """Test lock_all raises error when no .feature files exist."""
        features_dir = tmp_path / "features"
        features_dir.mkdir()
        
        # Create a non-feature file
        (features_dir / "readme.txt").write_text("Not a feature file")
        
        lock_manager = FeatureLock(tmp_path)
        
        with pytest.raises(FeatureLockError) as exc_info:
            lock_manager.lock_all()
        
        assert "no .feature files" in str(exc_info.value).lower()
    
    def test_lock_all_recursive(self, tmp_path):
        """Test lock_all finds feature files in subdirectories."""
        features_dir = tmp_path / "features"
        subdir = features_dir / "subdir"
        subdir.mkdir(parents=True)
        
        (features_dir / "test1.feature").write_text("Feature: Test 1\n")
        (subdir / "test2.feature").write_text("Feature: Test 2\n")
        
        lock_manager = FeatureLock(tmp_path)
        count = lock_manager.lock_all()
        
        assert count == 2


class TestVerify:
    """Test verify method."""
    
    def test_verify_unchanged_file(self, tmp_path):
        """Test verification passes when file hasn't changed."""
        features_dir = tmp_path / "features"
        features_dir.mkdir()
        feature_file = features_dir / "test.feature"
        feature_file.write_text("Feature: Test\n  Scenario: Test\n")
        
        lock_manager = FeatureLock(tmp_path)
        lock_manager.lock("features/test.feature")
        
        # Verify should pass
        result = lock_manager.verify("features/test.feature")
        assert result is True
    
    def test_verify_modified_file(self, tmp_path):
        """Test verification fails when file has been modified."""
        features_dir = tmp_path / "features"
        features_dir.mkdir()
        feature_file = features_dir / "test.feature"
        feature_file.write_text("Feature: Test\n  Scenario: Original\n")
        
        lock_manager = FeatureLock(tmp_path)
        lock_manager.lock("features/test.feature")
        
        # Modify the file
        feature_file.write_text("Feature: Test\n  Scenario: Modified\n")
        
        # Verify should fail
        with pytest.raises(FeatureLockError) as exc_info:
            lock_manager.verify("features/test.feature")
        
        assert "modified" in str(exc_info.value).lower()
        assert "Expected:" in str(exc_info.value)
        assert "Got:" in str(exc_info.value)
    
    def test_verify_deleted_file(self, tmp_path):
        """Test verification fails when file has been deleted."""
        features_dir = tmp_path / "features"
        features_dir.mkdir()
        feature_file = features_dir / "test.feature"
        feature_file.write_text("Feature: Test\n")
        
        lock_manager = FeatureLock(tmp_path)
        lock_manager.lock("features/test.feature")
        
        # Delete the file
        feature_file.unlink()
        
        # Verify should fail
        with pytest.raises(FeatureLockError) as exc_info:
            lock_manager.verify("features/test.feature")
        
        assert "deleted" in str(exc_info.value).lower()
    
    def test_verify_unlocked_file(self, tmp_path):
        """Test verification passes for unlocked files (returns True)."""
        features_dir = tmp_path / "features"
        features_dir.mkdir()
        feature_file = features_dir / "test.feature"
        feature_file.write_text("Feature: Test\n")
        
        lock_manager = FeatureLock(tmp_path)
        
        # Don't lock the file, just verify
        result = lock_manager.verify("features/test.feature")
        assert result is True
    
    def test_verify_invalid_locks_file(self, tmp_path):
        """Test verification fails with invalid locks file."""
        locks_dir = tmp_path / ".lingmaflow"
        locks_dir.mkdir()
        locks_file = locks_dir / "feature_locks.json"
        locks_file.write_text("{invalid json}")
        
        # FeatureLock.__init__() will raise error when loading invalid JSON
        with pytest.raises(FeatureLockError) as exc_info:
            lock_manager = FeatureLock(tmp_path)
        
        assert "invalid" in str(exc_info.value).lower()
        assert "feature_locks.json" in str(exc_info.value)
        assert "lingmaflow feature-lock --all" in str(exc_info.value)


class TestLoadAndSaveLocks:
    """Test loading and saving locks."""
    
    def test_load_existing_locks(self, tmp_path):
        """Test loading locks from existing file."""
        locks_dir = tmp_path / ".lingmaflow"
        locks_dir.mkdir()
        locks_file = locks_dir / "feature_locks.json"
        
        locks_data = {"features/test.feature": "sha256:abc123"}
        locks_file.write_text(json.dumps(locks_data))
        
        lock_manager = FeatureLock(tmp_path)
        
        assert "features/test.feature" in lock_manager.locks
        assert lock_manager.locks["features/test.feature"] == "sha256:abc123"
    
    def test_save_locks_creates_directory(self, tmp_path):
        """Test that saving locks creates .lingmaflow directory if needed."""
        lock_manager = FeatureLock(tmp_path)
        lock_manager.locks["features/test.feature"] = "sha256:test"
        lock_manager._save_locks()
        
        locks_file = tmp_path / ".lingmaflow" / "feature_locks.json"
        assert locks_file.exists()
    
    def test_persist_locks_across_instances(self, tmp_path):
        """Test that locks persist across FeatureLock instances."""
        features_dir = tmp_path / "features"
        features_dir.mkdir()
        feature_file = features_dir / "test.feature"
        feature_file.write_text("Feature: Test\n")
        
        # First instance: lock the file
        lock_manager1 = FeatureLock(tmp_path)
        hash_value = lock_manager1.lock("features/test.feature")
        
        # Second instance: should load the lock
        lock_manager2 = FeatureLock(tmp_path)
        assert "features/test.feature" in lock_manager2.locks
        assert lock_manager2.locks["features/test.feature"] == hash_value
