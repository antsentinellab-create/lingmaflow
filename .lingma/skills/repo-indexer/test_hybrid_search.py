#!/usr/bin/env python3
"""
Test the Hybrid Search functionality of the SQLite-based Repo Indexer.
"""
import os
import sys
import time
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))

from database_manager import DatabaseManager
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def test_hybrid_search():
    db_path = Path("repo-index/codebase.db")
    if not db_path.exists():
        print(f"❌ Error: Database not found at {db_path}")
        return

    print(f"🔍 Testing Hybrid Search on: {db_path}")
    
    # Initialize components
    db_manager = DatabaseManager(db_path=str(db_path), embedding_dim=384)
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    
    # Test Query 1: Database-related
    query_text = "How is the database manager implemented for vector storage?"
    print(f"\n{'='*80}")
    print(f"💬 Query 1: \"{query_text}\"")
    print(f"{'='*80}")
    
    # Generate embedding
    start_time = time.time()
    query_embedding = embed_model.get_text_embedding(query_text)
    embed_time = time.time() - start_time
    
    # Perform Hybrid Search
    start_search = time.time()
    results = db_manager.hybrid_search(
        query_embedding=query_embedding,
        limit=5,
        graph_depth=2,
        alpha=0.7
    )
    search_time = time.time() - start_search
    
    print(f"\n⏱️  Performance:")
    print(f"   Embedding Generation: {embed_time:.4f}s")
    print(f"   Hybrid Search (SQL + Vector): {search_time:.4f}s")
    print(f"   Total Time: {embed_time + search_time:.4f}s")
    
    print(f"\n📊 Top {len(results)} Results:")
    print("-" * 80)
    for i, res in enumerate(results, 1):
        print(f"{i}. [Score: {res['score']:.4f}] Node ID: {res['node_id']}")
        print(f"   File: {res.get('file_path', 'N/A')}")
        print(f"   Lines: {res.get('chunk_start', '?')}-{res.get('chunk_end', '?')}")
        print(f"   Content: {res.get('code_content', '')[:120]}...")
        print("-" * 80)
    
    # Test Query 2: Index building
    query_text2 = "How to build code index with AST parsing?"
    print(f"\n{'='*80}")
    print(f"💬 Query 2: \"{query_text2}\"")
    print(f"{'='*80}")
    
    start_time = time.time()
    query_embedding2 = embed_model.get_text_embedding(query_text2)
    embed_time2 = time.time() - start_time
    
    start_search = time.time()
    results2 = db_manager.hybrid_search(
        query_embedding=query_embedding2,
        limit=5,
        graph_depth=2,
        alpha=0.7
    )
    search_time2 = time.time() - start_search
    
    print(f"\n⏱️  Performance:")
    print(f"   Embedding Generation: {embed_time2:.4f}s")
    print(f"   Hybrid Search (SQL + Vector): {search_time2:.4f}s")
    print(f"   Total Time: {embed_time2 + search_time2:.4f}s")
    
    print(f"\n📊 Top {len(results2)} Results:")
    print("-" * 80)
    for i, res in enumerate(results2, 1):
        print(f"{i}. [Score: {res['score']:.4f}] Node ID: {res['node_id']}")
        print(f"   File: {res.get('file_path', 'N/A')}")
        print(f"   Lines: {res.get('chunk_start', '?')}-{res.get('chunk_end', '?')}")
        print(f"   Content: {res.get('code_content', '')[:120]}...")
        print("-" * 80)
        
    db_manager.close()

if __name__ == "__main__":
    test_hybrid_search()
