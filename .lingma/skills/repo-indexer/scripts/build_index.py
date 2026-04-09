#!/usr/bin/env python3
"""
Build codebase vector index using SQLite Hybrid DB (Vector + Graph).
This script implements the dual-dimension indexing:
1. AST-based Call Graph (SQLite Edges)
2. Vector Index (sqlite-vec) with precise line number mapping
"""

import os
import sys
import bisect
from pathlib import Path
import psutil

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import SimpleDirectoryReader

from call_graph import CallGraphAnalyzer
from graph_manager import GraphManager
from precision_splitter import PrecisionLineCodeSplitter
from database_manager import DatabaseManager, serialize_float32


def build_index(input_dir=".", output_dir="./repo-index", extensions=None):
    """
    Build dual-dimension index: Vector (sqlite-vec) + Graph (SQLite).
    
    Phase 1: AST Parsing & Graph Construction (Source of Truth)
    Phase 2: Document Loading & Precision Chunking
    Phase 3: Embedding & SQLite Storage with UUID Binding
    Phase 4: Persistence with Memory Monitoring
    """
    if extensions is None:
        extensions = [".py"]
    
    repo_root = Path(input_dir).resolve()
    db_path = Path(output_dir) / "codebase.db"
    
    print(f"📂 Repo Root: {repo_root}")
    print(f"💾 Hybrid DB: {db_path}")
    
    # ============================================================
    # PHASE 1: AST PARSING & GRAPH CONSTRUCTION (Source of Truth)
    # ============================================================
    print("\n" + "="*60)
    print("PHASE 1: AST Parsing & Graph Construction")
    print("="*60)
    
    # Initialize SQLite Database Manager
    embedding_dim = 384  # BAAI/bge-small-en-v1.5 produces 384-dimensional vectors
    db_manager = DatabaseManager(db_path=str(db_path), embedding_dim=embedding_dim)
    
    # Use temporary GraphManager for in-memory AST processing
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
        temp_graph_path = tmp.name
    
    graph_manager = GraphManager(db_path=temp_graph_path)
    analyzer = CallGraphAnalyzer()
    
    python_files = list(repo_root.rglob("*.py"))
    print(f"🔍 Found {len(python_files)} Python files")
    
    failed_files = []
    for idx, py_file in enumerate(python_files, 1):
        try:
            # Convert to relative path for consistency
            rel_path = str(py_file.relative_to(repo_root))
            if not analyzer.parse_file_to_graph(
                file_path=str(py_file), 
                graph_manager=graph_manager, 
                rel_path=rel_path
            ):
                failed_files.append(rel_path)
            
            if idx % 100 == 0:
                print(f"   Processed {idx}/{len(python_files)} files...")
        except Exception as e:
            print(f"   ⚠️  [MISSING_GRAPH_NODES] Unexpected error for {py_file}: {e}")
            failed_files.append(str(py_file.relative_to(repo_root)))
    
    if failed_files:
        print(f"\n⚠️  [MISSING_GRAPH_NODES] {len(failed_files)} files failed AST parsing.")
        print("   These files will have vector embeddings but no graph nodes (Orphan Vectors).")
    
    print(f"✅ Phase 1 Complete: {graph_manager.graph.number_of_nodes()} nodes in graph")
    
    # Migrate graph to SQLite
    print("   🚀 Migrating graph to SQLite...")
    def node_generator():
        for node_id, data in graph_manager.graph.nodes(data=True):
            yield (
                node_id,
                data.get("type", "unknown"),
                data.get("file_path", ""),
                data.get("start_line", 0),
                data.get("end_line", 0),
                str({k: v for k, v in data.items() if k not in ["type", "file_path", "start_line", "end_line"]})
            )
    
    db_manager.add_nodes_batch(node_generator(), batch_size=5000)
    
    def edge_generator():
        for source, target, data in graph_manager.graph.edges(data=True):
            yield (source, target, data.get("relation_type", "CALLS"))
    
    db_manager.add_edges_batch(edge_generator(), batch_size=10000)
    print(f"   ✅ Graph migrated: {graph_manager.graph.number_of_edges()} edges")
    
    # Cleanup temporary graph file
    try:
        os.remove(temp_graph_path)
        if os.path.exists(temp_graph_path.replace('.json', '.lock')):
            os.remove(temp_graph_path.replace('.json', '.lock'))
    except:
        pass
    
    # ============================================================
    # PHASE 2: DOCUMENT LOADING & PRECISION CHUNKING
    # ============================================================
    print("\n" + "="*60)
    print("PHASE 2: Document Loading & Precision Chunking")
    print("="*60)
    
    # Aggressively filter out unwanted directories before loading
    all_files = list(repo_root.rglob("*.py"))
    filtered_files = [
        str(f) for f in all_files 
        if ".venv" not in f.parts and 
           "node_modules" not in f.parts and 
           "__pycache__" not in f.parts and
           not f.name.startswith(".")
    ]
    print(f"📄 Found {len(filtered_files)} Python files (filtered from {len(all_files)})")
    
    # Use SimpleDirectoryReader with parallel processing
    reader = SimpleDirectoryReader(input_files=filtered_files)
    documents = reader.load_data()
    print(f"📄 Loaded {len(documents)} documents via Parallel Reader")
    
    if not documents:
        print("❌ No documents found.")
        sys.exit(1)
    
    # Use PrecisionLineCodeSplitter for exact line number tracking
    splitter = PrecisionLineCodeSplitter(
        language="python",
        chunk_lines=40,
        chunk_lines_overlap=5,
        max_chars=1500
    )
    
    nodes = splitter.get_nodes_from_documents(documents)
    print(f"✂️  Created {len(nodes)} nodes with precise line numbers")
    
    # ============================================================
    # PHASE 3: EMBEDDING & SQLITE STORAGE WITH UUID BINDING
    # ============================================================
    print("\n" + "="*60)
    print("PHASE 3: Embedding & SQLite Storage")
    print("="*60)
    
    # Initialize Embedding Model (Lazy Loading)
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    embedding_dim = 384
    
    # Build Line-to-Node Mapping using Sorted Array + Binary Search (Memory Optimized)
    print("   🗺️  Building optimized line-to-node mapping...")
    node_ranges = []
    for node_id, data in graph_manager.graph.nodes(data=True):
        fp = data.get("file_path", "")
        start = data.get("start_line", 0)
        end = data.get("end_line", 0)
        node_ranges.append((fp, start, end, node_id))
    
    # CRITICAL: Sort by file_path and start_line for bisect to work correctly
    node_ranges.sort(key=lambda x: (x[0], x[1]))
    
    def find_node_by_line(file_path, line_no):
        """O(log N) lookup using binary search."""
        # Create a dummy key for searching
        lo = bisect.bisect_left(node_ranges, (file_path, line_no))
        # Check backwards to see if the line falls within any range
        for i in range(lo - 1, max(-1, lo - 5), -1): # Check a few previous entries
            if i < 0: break
            fp, start, end, nid = node_ranges[i]
            if fp == file_path and start <= line_no <= end:
                return nid
        return f"{file_path}:{line_no}" # Fallback

    # Process nodes and bind to graph
    print("🔤 Embedding and binding nodes to graph...")
    batch_size = 100
    vector_metadata_batch = [] # For 'vectors' table
    vec_nodes_batch = []       # For 'vec_nodes' virtual table
    
    for i in range(0, len(nodes), batch_size):
        batch_nodes = nodes[i:i+batch_size]
        
        # Get embeddings
        texts = [node.text for node in batch_nodes]
        embeddings = embed_model.get_text_embedding_batch(texts)
        
        for j, node in enumerate(batch_nodes):
            abs_path = node.metadata.get("file_path", "")
            try:
                rel_path = str(Path(abs_path).relative_to(repo_root))
            except ValueError:
                rel_path = abs_path
            
            chunk_start = node.metadata.get("start_line", 0)
            chunk_end = node.metadata.get("end_line", 0)
            
            # Find the most representative AST node ID using Binary Search
            linked_node_id = find_node_by_line(rel_path, chunk_start)
            
            vector_id = f"vec_{i+j}"
            binary_embedding = serialize_float32(embeddings[j])
            
            # Prepare batches
            vector_metadata_batch.append((
                vector_id, 
                linked_node_id, 
                binary_embedding, 
                node.text[:500], 
                chunk_start, 
                chunk_end
            ))
            # For vec_nodes, include vector_id as primary key and node_id for graph traversal
            vec_nodes_batch.append((vector_id, linked_node_id, binary_embedding))
        
        # RSS Memory Monitoring every 10 batches
        if (i // batch_size + 1) % 10 == 0:
            process = psutil.Process(os.getpid())
            rss_mb = process.memory_info().rss / 1024 / 1024
            print(f"   📊 RSS Memory: {rss_mb:.2f} MB (processed {i+len(batch_nodes)}/{len(nodes)} nodes)")
    
    # Execute Batch Insertions
    print(f"   🚀 Batch inserting {len(vector_metadata_batch)} vectors into SQLite...")
    db_manager.add_vectors_metadata_batch(vector_metadata_batch)
    db_manager.add_vectors_batch(vec_nodes_batch)
    
    print(f"✅ Phase 3 Complete: {len(nodes)} nodes embedded and stored in SQLite")
    
    # ============================================================
    # PHASE 4: FINALIZATION
    # ============================================================
    print("\n" + "="*60)
    print("PHASE 4: Finalization")
    print("="*60)
    
    process = psutil.Process(os.getpid())
    rss_mb = process.memory_info().rss / 1024 / 1024
    print(f"📊 Final RSS Memory: {rss_mb:.2f} MB")
    
    db_manager.close()
    
    print(f"\n✅ Index complete!")
    print(f"💾 Hybrid DB: {db_path}")
    print(f"📊 Total Nodes: {graph_manager.graph.number_of_nodes()}")
    print(f"📊 Total Edges: {graph_manager.graph.number_of_edges()}")
    print("\n💡 You can now use enhanced_query.py --with-graph to search")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build Hybrid RAG Index (Vector + Graph)")
    parser.add_argument("--input-dir", type=str, default=".", help="Root directory of the repository")
    parser.add_argument("--output-dir", type=str, default="./repo-index", help="Path for SQLite Hybrid DB")
    args = parser.parse_args()

    # Enforce absolute paths to avoid ambiguity in relative path calculations
    abs_input = os.path.abspath(args.input_dir)
    if not os.path.exists(abs_input):
        print(f"❌ Error: Input directory {abs_input} not found.")
        sys.exit(1)
        
    build_index(input_dir=abs_input, output_dir=args.output_dir)
