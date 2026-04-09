#!/usr/bin/env python3
"""
Enhanced query module with SQLite Hybrid RAG (Vector + Graph).
Provides structural understanding through topology expansion and joint scoring.
"""

import sys
import os
import argparse
from pathlib import Path
from typing import List, Dict, Optional

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database_manager import DatabaseManager
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


class EnhancedCodebaseQuery:
    """Hybrid RAG query engine with graph topology expansion."""
    
    def __init__(self, db_path="./repo-index/codebase.db", repo_root=".", use_graph=False):
        self.db_path = db_path
        self.repo_root = Path(repo_root).resolve()
        self.use_graph = use_graph
        self._db_manager = None
        self._embed_model = None
        
    def _load_db(self):
        """Lazy load the SQLite Hybrid Database."""
        if self._db_manager is None:
            if not os.path.exists(self.db_path):
                raise FileNotFoundError(f"Hybrid DB not found at {self.db_path}")
            # BAAI/bge-small-en-v1.5 produces 384-dimensional vectors
            self._db_manager = DatabaseManager(db_path=self.db_path, embedding_dim=384)
            print(f"💾 Hybrid DB loaded: {self.db_path}")
        return self._db_manager
    
    def _get_embed_model(self):
        """Lazy load the embedding model."""
        if self._embed_model is None:
            self._embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        return self._embed_model
    
    def _hydrate_code_from_node_id(self, node_id: str) -> Optional[str]:
        """
        Read actual source code from file system based on AST node ID.
        """
        db = self._load_db()
        nodes = db.get_nodes_batch([node_id])
        if not nodes or node_id not in nodes:
            return None
        
        attrs = nodes[node_id]
        rel_path = attrs.get("file_path")
        start_line = attrs.get("start_line", 1)
        end_line = attrs.get("end_line", 1)
        
        if not rel_path:
            return None
        
        abs_path = self.repo_root / rel_path
        if not abs_path.exists():
            return f"# [HYDRATION_ERROR] File not found: {abs_path}"
        
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            safe_start = max(0, start_line - 1)
            safe_end = min(total_lines, end_line)
            
            if safe_start >= total_lines:
                return f"# [HYDRATION_ERROR] Start line {start_line} exceeds file length {total_lines}"
            
            snippet = ''.join(lines[safe_start:safe_end])
            return f"# File: {rel_path} (Lines {start_line}-{end_line})\n{snippet}"
        except Exception as e:
            return f"# [HYDRATION_ERROR] {str(e)}"
    
    def query_with_hybrid_rag(self, question: str, top_k: int = 5, graph_depth: int = 2, alpha: float = 0.7) -> Dict:
        """
        Perform Hybrid Retrieval using SQLite Hybrid DB.
        Combines Vector Similarity with Graph Traversal via Joint Scoring.
        """
        db = self._load_db()
        embed_model = self._get_embed_model()
        
        # Phase 1: Generate Query Embedding
        query_embedding = embed_model.get_text_embedding(question)
        
        # Phase 2: Execute Hybrid Search (SQL Level)
        results = db.hybrid_search(
            query_embedding=query_embedding,
            limit=top_k,
            graph_depth=graph_depth if self.use_graph else 0,
            alpha=alpha
        )
        
        # Phase 3: Format Results & Hydrate Code
        formatted_results = []
        hydrated_context = []
        
        for res in results:
            node_id = res['node_id']
            meta = res.get('metadata', {})
            
            # Get code content from vectors table if available
            vectors = db.get_vectors_by_node(node_id)
            code_snippet = vectors[0]['code_content'] if vectors else "# [No code content stored]"
            
            formatted_results.append({
                "id": node_id,
                "score": round(res['score'], 4),
                "vector_dist": round(res['vector_dist'], 4),
                "graph_depth": res['graph_depth'],
                "file_path": meta.get('file_path', 'N/A'),
                "preview": code_snippet[:150] + "..."
            })
            
            # Full Code Hydration
            full_code = self._hydrate_code_from_node_id(node_id)
            if full_code and "tests/" not in full_code:
                hydrated_context.append(full_code)
        
        return {
            "question": question,
            "hybrid_results": formatted_results,
            "graph_context": hydrated_context,
            "metrics": {
                "total_results": len(results),
                "hydrated_snippets": len(hydrated_context)
            }
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enhanced Codebase Query with SQLite Hybrid RAG")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--with-graph", action="store_true", help="Enable graph topology expansion")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to return")
    parser.add_argument("--graph-depth", type=int, default=2, help="Graph traversal depth")
    parser.add_argument("--alpha", type=float, default=0.7, help="Weight for vector similarity (0.0-1.0)")
    parser.add_argument("--repo-root", type=str, default=".", help="Root directory of the repository")
    
    args = parser.parse_args()
    
    print(f"🔍 Query: {args.query}")
    if args.with_graph:
        print(f"🗺️  Mode: Hybrid RAG (Vector + Graph, Depth={args.graph_depth})")
    
    engine = EnhancedCodebaseQuery(
        db_path="./repo-index/codebase.db",
        repo_root=args.repo_root,
        use_graph=args.with_graph
    )
    
    result = engine.query_with_hybrid_rag(
        args.query, 
        top_k=args.top_k, 
        graph_depth=args.graph_depth,
        alpha=args.alpha
    )
    
    print("\n" + "="*80)
    print("HYBRID SEARCH RESULTS:")
    print("="*80)
    for i, r in enumerate(result['hybrid_results'], 1):
        print(f"{i}. [Score: {r['score']}] Node: {r['id']}")
        print(f"   File: {r['file_path']} | VecDist: {r['vector_dist']} | GraphDepth: {r['graph_depth']}")
        print(f"   Preview: {r['preview']}")
        print("-" * 80)
    
    if result['graph_context']:
        print("\n" + "="*80)
        print("HYDRATED CODE CONTEXT:")
        print("="*80)
        for ctx in result['graph_context']:
            print(ctx)
            print("-" * 80)
    
    print("\n" + "="*80)
    print("[Metrics]")
    print("="*80)
    print(f"Total Results: {result['metrics']['total_results']}")
    print(f"Hydrated Snippets: {result['metrics']['hydrated_snippets']}")
