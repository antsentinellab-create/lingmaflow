#!/usr/bin/env python3
"""
Graph Integrity Test Suite.
Validates GraphManager core functionality, atomic writes, and precision mapping.
"""

import os
import sys
import json
import time
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graph_manager import GraphManager, SafeFileLock


class TestGraphManagerCore:
    """Task 7.1 - 7.9: Core GraphManager Unit Tests."""

    @pytest.fixture
    def temp_graph(self, tmp_path):
        """Setup a temporary graph manager for each test."""
        db_path = tmp_path / "topology.json"
        return GraphManager(db_path=str(db_path))

    def test_add_node_creates_correct_attributes(self, temp_graph):
        """Task 7.1: Verify node attributes."""
        temp_graph.add_node("test_func", "function", "src/test.py", 10, 20)
        attrs = temp_graph.graph.nodes["test_func"]
        
        assert attrs["type"] == "function"
        assert attrs["file_path"] == "src/test.py"
        assert attrs["start_line"] == 10
        assert attrs["end_line"] == 20
        assert attrs["vector_ids"] == []

    def test_add_node_type_assertion(self, temp_graph):
        """Task 7.2: Ensure non-string node_id raises TypeError."""
        with pytest.raises(TypeError):
            temp_graph.add_node(123, "function", "src/test.py", 10, 20)
        
        with pytest.raises(TypeError):
            temp_graph.add_node(("tuple", "id"), "function", "src/test.py", 10, 20)

    def test_link_vector_to_node_intersection(self, temp_graph):
        """Task 7.3: Link vector to nodes with line number intersection."""
        temp_graph.add_node("func_a", "function", "src/a.py", 5, 15)
        temp_graph.link_vector_to_node("vec_1", 10, 12, "src/a.py")
        
        assert "vec_1" in temp_graph.graph.nodes["func_a"]["vector_ids"]
        assert "func_a" in temp_graph.get_nodes_by_vector_id("vec_1")

    def test_many_to_many_mapping(self, temp_graph):
        """Task 7.4: One vector linking to multiple nodes (crossing functions)."""
        temp_graph.add_node("func_a", "function", "src/a.py", 1, 10)
        temp_graph.add_node("func_b", "function", "src/a.py", 11, 20)
        
        # Chunk spans from line 8 to 14
        temp_graph.link_vector_to_node("vec_cross", 8, 14, "src/a.py")
        
        assert "vec_cross" in temp_graph.graph.nodes["func_a"]["vector_ids"]
        assert "vec_cross" in temp_graph.graph.nodes["func_b"]["vector_ids"]

    def test_get_filtered_neighbors_degree_filter(self, temp_graph):
        """Task 7.6: Skip neighbors with high in-degree."""
        temp_graph.add_node("logger", "function", "lib/log.py", 1, 5)
        temp_graph.add_node("caller", "function", "src/main.py", 1, 5)
        temp_graph.graph.add_edge("caller", "logger")
        
        # Simulate high degree by adding many predecessors to logger
        for i in range(15):
            temp_graph.graph.add_edge(f"other_{i}", "logger")
        
        neighbors = temp_graph.get_filtered_neighbors("caller", max_in_degree=10)
        assert "logger" not in neighbors  # Should be filtered out

    def test_save_creates_lock_and_json(self, temp_graph):
        """Task 7.7: Verify save creates files."""
        temp_graph.add_node("test", "function", "t.py", 1, 2)
        temp_graph.save()
        
        assert temp_graph.db_path.exists()
        assert temp_graph.lock_path.exists() is False  # Lock should be released

    def test_load_rebuilds_index(self, temp_graph):
        """Task 7.8: Load restores graph and vector index."""
        temp_graph.add_node("n1", "function", "f.py", 1, 2)
        temp_graph.link_vector_to_node("v1", 1, 2, "f.py")
        temp_graph.save()
        
        new_mgr = GraphManager(db_path=str(temp_graph.db_path))
        new_mgr.load()
        
        assert new_mgr.graph.has_node("n1")
        assert "n1" in new_mgr.get_nodes_by_vector_id("v1")


class TestSafeFileLock:
    """Task 8.1 - 8.4: Atomic Write and Concurrency Tests."""

    def test_stale_lock_detection(self, tmp_path):
        """Task 8.3: Detect and break stale locks older than timeout."""
        lock_path = tmp_path / "test.lock"
        
        # Create a fake stale lock file
        with open(lock_path, 'w') as f:
            json.dump({"pid": 99999, "timestamp": time.time() - 600}, f)  # 10 mins ago
        
        # Modify mtime to ensure it's old
        old_time = time.time() - 600
        os.utime(lock_path, (old_time, old_time))
        
        lock = SafeFileLock(str(lock_path), timeout=300)
        lock.acquire()  # Should detect stale lock and proceed
        
        assert lock_path.exists()  # New lock should exist
        lock.release()

    def test_atomic_write_resilience(self, tmp_path):
        """Task 8.1: Simulate crash during dump and verify integrity."""
        db_path = tmp_path / "atomic_test.json"
        mgr = GraphManager(db_path=str(db_path))
        mgr.add_node("crash_test", "function", "c.py", 1, 2)
        
        # Mock json.dump to raise an exception halfway
        original_dump = json.dump
        def crashing_dump(*args, **kwargs):
            raise RuntimeError("Simulated Crash")
        
        with patch('json.dump', side_effect=crashing_dump):
            with pytest.raises(RuntimeError):
                mgr.save()
        
        # Verify no corrupted file exists (atomic write ensures this)
        assert not db_path.exists() or db_path.stat().st_size > 0


class TestPrecisionMapping:
    """Task 9.1 - 9.4: Precision Line Number Mapping Tests."""

    def test_relative_path_storage(self, tmp_path):
        """Task 9.4: Ensure paths are stored relatively."""
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        db_path = repo_root / "topology.json"
        
        mgr = GraphManager(db_path=str(db_path))
        mgr.add_node("m1", "module", "src/mod.py", 1, 10)
        mgr.save()
        
        with open(db_path, 'r') as f:
            data = json.load(f)
        
        # Check if the node in the JSON has relative path
        node_data = next((n for n in data['nodes'] if n['id'] == 'm1'), None)
        assert node_data is not None
        assert node_data['file_path'] == "src/mod.py"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
