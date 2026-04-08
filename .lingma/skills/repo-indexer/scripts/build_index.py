#!/usr/bin/env python3
"""
Build codebase vector index using LlamaIndex + Chroma with AST-first topology graph.
This script implements the dual-dimension indexing:
1. AST-based Call Graph (NetworkX)
2. Vector Index (Chroma) with precise line number mapping
"""

import os
import sys
from pathlib import Path
import psutil

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llama_index.core import SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.schema import Document
import chromadb

from call_graph import CallGraphAnalyzer
from graph_manager import GraphManager
from precision_splitter import PrecisionLineCodeSplitter


def build_index(input_dir=".", output_dir="./repo-index", extensions=None):
    """
    Build dual-dimension index: Vector (Chroma) + Graph (NetworkX).
    
    Phase 1: AST Parsing & Graph Construction (Source of Truth)
    Phase 2: Document Loading & Precision Chunking
    Phase 3: Embedding & Chroma Storage with UUID Binding
    Phase 4: Persistence with Memory Monitoring
    """
    if extensions is None:
        extensions = [".py"]
    
    repo_root = Path(input_dir).resolve()
    graph_db_path = repo_root / "repo-graph" / "topology.json"
    
    print(f"📂 Repo Root: {repo_root}")
    print(f"🗺️  Graph DB: {graph_db_path}")
    print(f"💾 Vector Store: {output_dir}")
    
    # ============================================================
    # PHASE 1: AST PARSING & GRAPH CONSTRUCTION (Source of Truth)
    # ============================================================
    print("\n" + "="*60)
    print("PHASE 1: AST Parsing & Graph Construction")
    print("="*60)
    
    graph_manager = GraphManager(db_path=str(graph_db_path))
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
    
    # ============================================================
    # PHASE 2: DOCUMENT LOADING & PRECISION CHUNKING
    # ============================================================
    print("\n" + "="*60)
    print("PHASE 2: Document Loading & Precision Chunking")
    print("="*60)
    
    documents = SimpleDirectoryReader(
        input_dir=str(repo_root),
        recursive=True,
        required_exts=extensions,
        exclude=["**/.*", "**/.venv/*", "**/__pycache__/*"]
    ).load_data()
    
    print(f"📄 Loaded {len(documents)} documents")
    
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
    # PHASE 3: EMBEDDING & CHROMA STORAGE WITH UUID BINDING
    # ============================================================
    print("\n" + "="*60)
    print("PHASE 3: Embedding & Chroma Storage")
    print("="*60)
    
    os.makedirs(output_dir, exist_ok=True)
    client = chromadb.PersistentClient(path=output_dir)
    collection = client.get_or_create_collection("codebase")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    
    # Process nodes and bind to graph
    print("🔤 Embedding and binding nodes to graph...")
    batch_size = 100
    
    for i in range(0, len(nodes), batch_size):
        batch_nodes = nodes[i:i+batch_size]
        
        # Get embeddings
        texts = [node.text for node in batch_nodes]
        embeddings = embed_model.get_text_embedding_batch(texts)
        
        # Prepare Chroma data
        ids = [f"node_{i+j}" for j in range(len(batch_nodes))]
        metadatas = []
        
        for j, node in enumerate(batch_nodes):
            # Task 4.5: Ensure relative path consistency
            abs_path = node.metadata.get("file_path", "")
            try:
                rel_path = str(Path(abs_path).relative_to(repo_root))
            except ValueError:
                rel_path = abs_path
            
            metadata = {
                "file_path": rel_path,
                "start_line": node.metadata.get("start_line", 0),
                "end_line": node.metadata.get("end_line", 0),
                **{k: v for k, v in node.metadata.items() if k not in ["file_path", "start_line", "end_line"]}
            }
            metadatas.append(metadata)
            
            # Task 4.4: Link vector_id to ALL intersecting AST nodes (many-to-many)
            vector_id = ids[j]
            graph_manager.link_vector_to_node(
                vector_id=vector_id,
                chunk_start=metadata["start_line"],
                chunk_end=metadata["end_line"],
                file_path=rel_path
            )
        
        # Add to Chroma
        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=texts
        )
        
        # Task 4.6: RSS Memory Monitoring every 100 files
        if (i // batch_size + 1) % 100 == 0:
            process = psutil.Process(os.getpid())
            rss_mb = process.memory_info().rss / 1024 / 1024
            print(f"   📊 RSS Memory: {rss_mb:.2f} MB (processed {i+len(batch_nodes)}/{len(nodes)} nodes)")
    
    print(f"✅ Phase 3 Complete: {len(nodes)} nodes embedded and bound")
    
    # ============================================================
    # PHASE 4: PERSISTENCE WITH MEMORY MONITORING
    # ============================================================
    print("\n" + "="*60)
    print("PHASE 4: Graph Persistence")
    print("="*60)
    
    process = psutil.Process(os.getpid())
    rss_before = process.memory_info().rss / 1024 / 1024
    print(f"📊 RSS before save: {rss_before:.2f} MB")
    
    graph_manager.save()
    
    rss_after = process.memory_info().rss / 1024 / 1024
    print(f"📊 RSS after save: {rss_after:.2f} MB")
    print(f"📈 Memory delta: {rss_after - rss_before:.2f} MB")
    
    print(f"\n✅ Index complete!")
    print(f"📁 Vector Store: {output_dir}")
    print(f"🗺️  Topology Graph: {graph_db_path}")
    print(f"📊 Total Nodes: {graph_manager.graph.number_of_nodes()}")
    print(f"📊 Total Edges: {graph_manager.graph.number_of_edges()}")
    print(f"📊 Vector Mappings: {sum(len(v) for v in graph_manager.vector_to_nodes.values())}")
    print("\n💡 You can now use enhanced_query.py --with-graph to search")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build Hybrid RAG Index (Vector + Graph)")
    parser.add_argument("--input-dir", type=str, default=".", help="Root directory of the repository")
    parser.add_argument("--output-dir", type=str, default="./repo-index", help="Path for Chroma vector store")
    args = parser.parse_args()

    # Enforce absolute paths to avoid ambiguity in relative path calculations
    abs_input = os.path.abspath(args.input_dir)
    if not os.path.exists(abs_input):
        print(f"❌ Error: Input directory {abs_input} not found.")
        sys.exit(1)
        
    build_index(input_dir=abs_input, output_dir=args.output_dir)
