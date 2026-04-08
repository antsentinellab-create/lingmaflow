#!/usr/bin/env python3
"""
Comprehensive Test for SQLite Hybrid DB.
Tests performance, data integrity, and hybrid search logic.
"""

import os
import sys
import time
import random
from pathlib import Path

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from database_manager import DatabaseManager, serialize_float32

def test_basic_integrity():
    """Test basic node and edge counts."""
    print("🧪 Testing Basic Integrity...")
    db = DatabaseManager()
    
    cursor = db.conn.execute("SELECT COUNT(*) FROM nodes")
    node_count = cursor.fetchone()[0]
    
    cursor = db.conn.execute("SELECT COUNT(*) FROM edges")
    edge_count = cursor.fetchone()[0]
    
    assert node_count == 410441, f"Node count mismatch: {node_count}"
    assert edge_count == 1203862, f"Edge count mismatch: {edge_count}"
    print(f"✅ Integrity Check Passed: {node_count} nodes, {edge_count} edges")
    db.close()

def test_cte_performance():
    """Test the performance of Recursive CTEs on high-degree nodes."""
    print("\n⚡ Testing CTE Performance (High-Degree Nodes)...")
    db = DatabaseManager()
    
    # Find a node with high degree (many connections)
    cursor = db.conn.execute("""
        SELECT source_id as id, COUNT(*) as cnt FROM edges GROUP BY source_id ORDER BY cnt DESC LIMIT 1
    """)
    start_node = cursor.fetchone()['id']
    
    # Forward traversal stress test
    start_time = time.time()
    forward_results = db.get_call_chain_with_depth(start_node, direction="forward", max_depth=3)
    forward_time = time.time() - start_time
    
    print(f"   Stress Test Node: {start_node} ({len(forward_results)} connected nodes)")
    print(f"   Forward Traversal Time: {forward_time:.4f}s")
    
    assert forward_time < 0.5, f"Forward traversal too slow: {forward_time}s"
    print("✅ CTE Performance Check Passed")
    db.close()

def test_batch_operations():
    """Test generator-based batch operations."""
    print("\n📦 Testing Batch Operations...")
    db = DatabaseManager(db_path="repo-index/test_temp.db")
    
    # Test node batching
    def node_gen():
        for i in range(100):
            yield (f"test_node_{i}", "function", "test.py", 1, 10, "{}")
    
    db.add_nodes_batch(node_gen(), batch_size=20)
    
    cursor = db.conn.execute("SELECT COUNT(*) FROM nodes")
    count = cursor.fetchone()[0]
    assert count == 100, f"Batch insert failed: {count}"
    
    # Cleanup
    db.close()
    os.remove("repo-index/test_temp.db")
    if os.path.exists("repo-index/test_temp.db-wal"):
        os.remove("repo-index/test_temp.db-wal")
    print("✅ Batch Operations Check Passed")

def test_hybrid_search_logic():
    """Test hybrid search logic and precision in an isolated environment."""
    print("\n🔍 Testing Hybrid Search Logic & Precision...")
    db = DatabaseManager(db_path="repo-index/test_temp.db", embedding_dim=1536)
    
    # 1. Setup: Create 50,000 dummy nodes and vectors for stress test
    print("   Preparing 50,000 dummy vectors...")
    dummy_vectors = []
    for i in range(50000):
        node_id = f"test_node_{i}"
        # Ensure vector dimension matches the database schema (1536)
        vec = [random.random() for _ in range(1536)]
        binary_vec = serialize_float32(vec)
        dummy_vectors.append((node_id, binary_vec))
        
        # Insert node metadata
        db.conn.execute(
            "INSERT INTO nodes VALUES (?, ?, ?, ?, ?, ?)",
            (node_id, "function", "test.py", 1, 10, '{}')
        )
    db.conn.commit()
    
    # Debug: Check if vectors table is empty before insert
    count_before = db.conn.execute("SELECT COUNT(*) FROM vec_nodes").fetchone()[0]
    print(f"   Vectors before insert: {count_before}")
    
    start_time = time.time()
    db.add_vectors_batch(dummy_vectors)
    insert_time = time.time() - start_time
    print(f"   Vector insertion time: {insert_time:.2f}s")
    
    # Debug: Check if vectors were inserted
    count_after = db.conn.execute("SELECT COUNT(*) FROM vec_nodes").fetchone()[0]
    print(f"   Vectors after insert: {count_after}")
    
    # Get one vector to test with
    test_row = db.conn.execute("SELECT node_id, embedding FROM vec_nodes LIMIT 1").fetchone()
    if test_row:
        print(f"   Testing with node: {test_row['node_id']}, Blob length: {len(test_row['embedding'])}")
    
    # 2. Precision Test: Search for a vector should return itself first
    target_vec_binary = dummy_vectors[0][1]
    print(f"   Target vector binary length: {len(target_vec_binary)}")
    
    # Try direct SQL query first
    try:
        direct_res = db.conn.execute(
            "SELECT node_id, vec_distance_cosine(embedding, ?) as dist FROM vec_nodes ORDER BY dist ASC LIMIT 1",
            [target_vec_binary]
        ).fetchone()
        print(f"   Direct SQL result: {direct_res}")
    except Exception as e:
        print(f"   Direct SQL error: {e}")
    
    # Now try hybrid_search
    results = db.hybrid_search(target_vec_binary, limit=1, graph_depth=0, alpha=1.0)
    
    assert len(results) > 0, "Hybrid search returned no results"
    assert results[0]['metadata']['id'] == 'test_node_0', f"Precision failed: got {results[0]['metadata']['id']}"
    
    # 3. Cleanup
    db.close()
    os.remove("repo-index/test_temp.db")
    if os.path.exists("repo-index/test_temp.db-wal"):
        os.remove("repo-index/test_temp.db-wal")
    print("✅ Hybrid Search Logic & Precision Check Passed")

if __name__ == "__main__":
    try:
        test_basic_integrity()
        test_cte_performance()
        test_batch_operations()
        test_hybrid_search_logic()
        print("\n🎉 All tests passed! The system is ready for production.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
