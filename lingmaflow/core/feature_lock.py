"""Feature Lock Module - Protect feature files from unauthorized modification.

This module provides hash-based protection for BDD feature files to prevent
AI agents from modifying or deleting scenarios to pass verification.
"""

from __future__ import annotations

import hashlib
import json
import os
import glob
from pathlib import Path
from typing import Dict, Optional


class FeatureLockError(Exception):
    """Exception raised when feature lock operations fail."""
    pass


class FeatureLock:
    """Manager for feature file hash locks.
    
    This class provides methods to lock feature files by recording their SHA256
    hashes, and verify that locked files haven't been modified.
    
    Attributes:
        locks_file: Path to the feature_locks.json file
        locks: Dictionary of feature file paths to their hashes
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the FeatureLock manager.
        
        Args:
            project_root: Root directory of the project. Defaults to current directory.
        """
        self.project_root = project_root or Path.cwd()
        self.locks_file = self.project_root / ".lingmaflow" / "feature_locks.json"
        self.locks: Dict[str, str] = {}
        
        # Load existing locks if file exists
        if self.locks_file.exists():
            self._load_locks()
    
    def _load_locks(self) -> None:
        """Load feature locks from JSON file.
        
        Raises:
            FeatureLockError: If the locks file is invalid JSON
        """
        try:
            content = self.locks_file.read_text(encoding='utf-8')
            self.locks = json.loads(content)
        except json.JSONDecodeError as e:
            raise FeatureLockError(
                f"Invalid feature_locks.json format: {str(e)}\n"
                f"Please re-run: lingmaflow feature-lock --all"
            )
    
    def _save_locks(self) -> None:
        """Save feature locks to JSON file."""
        # Ensure .lingmaflow directory exists
        self.locks_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write locks to file
        content = json.dumps(self.locks, indent=2, ensure_ascii=False)
        self.locks_file.write_text(content, encoding='utf-8')
    
    @staticmethod
    def compute_hash(file_path: Path) -> str:
        """Compute SHA256 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            SHA256 hash string with 'sha256:' prefix
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        return f"sha256:{sha256_hash.hexdigest()}"
    
    def lock(self, feature_path: str) -> str:
        """Lock a feature file by recording its hash.
        
        Args:
            feature_path: Relative path to the feature file (e.g., "features/test.feature")
            
        Returns:
            The computed hash string
            
        Raises:
            FileNotFoundError: If the feature file doesn't exist
        """
        file_path = self.project_root / feature_path
        
        if not file_path.exists():
            raise FileNotFoundError(f"Feature file not found: {feature_path}")
        
        # Compute hash
        hash_value = self.compute_hash(file_path)
        
        # Store in locks dictionary
        self.locks[feature_path] = hash_value
        
        # Save to file
        self._save_locks()
        
        return hash_value
    
    def lock_all(self) -> int:
        """Lock all feature files in the features/ directory.
        
        Returns:
            Number of files locked
            
        Raises:
            FeatureLockError: If features/ directory doesn't exist
        """
        features_dir = self.project_root / "features"
        
        if not features_dir.exists():
            raise FeatureLockError("features/ directory not found")
        
        # Find all .feature files
        feature_files = glob.glob(str(features_dir / "**" / "*.feature"), recursive=True)
        
        if not feature_files:
            raise FeatureLockError("No .feature files found in features/ directory")
        
        # Lock each file
        count = 0
        for feature_file in feature_files:
            # Convert to relative path
            rel_path = os.path.relpath(feature_file, self.project_root)
            
            try:
                self.lock(rel_path)
                count += 1
            except Exception as e:
                # Continue with other files even if one fails
                print(f"Warning: Failed to lock {rel_path}: {str(e)}")
        
        return count
    
    def verify(self, feature_path: str) -> bool:
        """Verify that a feature file hasn't been modified.
        
        Args:
            feature_path: Relative path to the feature file
            
        Returns:
            True if hash matches, False otherwise
            
        Raises:
            FeatureLockError: If the locks file is invalid
        """
        # If file is not locked, consider it verified (with optional warning)
        if feature_path not in self.locks:
            # Uncomment the next line if you want warnings for unlocked files
            # print(f"Warning: Feature file not locked: {feature_path}")
            return True
        
        file_path = self.project_root / feature_path
        
        if not file_path.exists():
            # File was deleted - this is a modification
            expected_hash = self.locks[feature_path]
            raise FeatureLockError(
                f"❌ {feature_path} has been deleted!\n"
                f"Expected: {expected_hash}\n"
                f"Feature files must not be modified by agent."
            )
        
        # Compute current hash
        current_hash = self.compute_hash(file_path)
        expected_hash = self.locks[feature_path]
        
        if current_hash != expected_hash:
            raise FeatureLockError(
                f"❌ {feature_path} has been modified!\n"
                f"Expected: {expected_hash}\n"
                f"Got:      {current_hash}\n"
                f"Feature files must not be modified by agent.\n"
                f"If this is intentional, run:\n"
                f"  lingmaflow feature-lock {feature_path}"
            )
        
        return True
