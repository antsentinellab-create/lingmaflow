#!/usr/bin/env python3
"""
Enhanced query module with Hybrid RAG (Vector + Graph) and Code Hydration.
Provides structural understanding through topology expansion.
"""

import sys
import os
import argparse
from pathlib import Path
import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from typing import List, Dict, Optional, Set

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from graph_manager import GraphManager


class EnhancedCodebaseQuery:
    """Hybrid RAG query engine with graph topology expansion."""
    
    def __init__(self, index_path="./repo-index", repo_root=".", use_graph=False):
        self.index_path = index_path
        self.repo_root = Path(repo_root).resolve()
        self.use_graph = use_graph
        self._index = None
        self._embed_model = None
        self._graph_manager = None
        
    def _load_index(self):
        """Lazy load the vector index."""
        if self._index is None:
            client = chromadb.PersistentClient(path=self.index_path)
            collection = client.get_collection("codebase")
            vector_store = ChromaVectorStore(chroma_collection=collection)
            
            self._embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
            self._index = VectorStoreIndex.from_vector_store(
                vector_store, 
                embed_model=self._embed_model
            )
        return self._index
    
    def _load_graph(self):
        """Load topology graph with error handling and fallback."""
        if self._graph_manager is None and self.use_graph:
            graph_db_path = self.repo_root / "repo-graph" / "topology.json"
            try:
                self._graph_manager = GraphManager(db_path=str(graph_db_path))
                self._graph_manager.load()
                print(f"🗺️  Topology graph loaded: {self._graph_manager.graph.number_of_nodes()} nodes")
            except Exception as e:
                print(f"\033[91m⚠️  [GRAPH_LOAD_FAILED] Failed to load topology graph: {e}\033[0m")
                print("💡 Falling back to pure vector mode.")
                self.use_graph = False
                self._graph_manager = None
        return self._graph_manager
    
    def _hydrate_code(self, node_id: str) -> Optional[str]:
        """
        Read actual source code from file system based on node metadata.
        Includes defensive programming for boundary checks.
        """
        if not self._graph_manager or node_id not in self._graph_manager.graph:
            return None
        
        attrs = self._graph_manager.graph.nodes[node_id]
        rel_path = attrs.get("file_path")
        start_line = attrs.get("start_line", 1)
        end_line = attrs.get("end_line", 1)
        
        # Task 5.8: Path resolution using repo_root
        abs_path = self.repo_root / rel_path
        
        if not abs_path.exists():
            return f"# [HYDRATION_ERROR] File not found: {abs_path}"
        
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Defensive check for line boundaries
            total_lines = len(lines)
            safe_start = max(0, start_line - 1)
            safe_end = min(total_lines, end_line)
            
            if safe_start >= total_lines:
                return f"# [HYDRATION_ERROR] Start line {start_line} exceeds file length {total_lines}"
            
            snippet = ''.join(lines[safe_start:safe_end])
            return f"# File: {rel_path} (Lines {start_line}-{end_line})\n{snippet}"
        except Exception as e:
            return f"# [HYDRATION_ERROR] {str(e)}"
    
    def query_with_hybrid_rag(self, question: str, top_k: int = 5, max_in_degree: int = 10) -> Dict:
        """
        Perform Hybrid Retrieval: Vector Search -> Graph Expansion -> Code Hydration.
        """
        index = self._load_index()
        graph_mgr = self._load_graph()
        
        # Phase 1: Vector Search
        retriever = index.as_retriever(similarity_top_k=top_k)
        vector_nodes = retriever.retrieve(question)
        
        vector_results = []
        expanded_node_ids: Set[str] = set()
        filtered_count = 0
        
        for node in vector_nodes:
            vid = node.node_id
            vector_results.append({
                "id": vid,
                "score": round(node.score, 3),
                "text": node.text[:200] + "..."
            })
            
            # Phase 2: Graph Expansion
            if graph_mgr:
                ast_nodes = graph_mgr.get_nodes_by_vector_id(vid)
                for ast_node_id in ast_nodes:
                    neighbors = graph_mgr.get_filtered_neighbors(ast_node_id, hop=1, max_in_degree=max_in_degree)
                    for n_id in neighbors:
                        if n_id not in expanded_node_ids:
                            # Check degree filtering
                            if graph_mgr.graph.in_degree(n_id) > max_in_degree:
                                filtered_count += 1
                                continue
                            expanded_node_ids.add(n_id)
        
        # Phase 3: Code Hydration
        graph_context = []
        hydrated_count = 0
        max_hydration = 10  # Task 5.6: Limit context explosion
        
        for n_id in list(expanded_node_ids)[:max_hydration]:
            code_snippet = self._hydrate_code(n_id)
            if code_snippet:
                graph_context.append(code_snippet)
                hydrated_count += 1
        
        return {
            "question": question,
            "vector_results": vector_results,
            "graph_context": graph_context,
            "metrics": {
                "expanded_nodes": len(expanded_node_ids),
                "hydrated_snippets": hydrated_count,
                "filtered_high_degree_nodes": filtered_count
            }
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enhanced Codebase Query with Hybrid RAG")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--with-graph", action="store_true", help="Enable graph topology expansion")
    parser.add_argument("--max-in-degree", type=int, default=10, help="Max in-degree filter threshold")
    parser.add_argument("--repo-root", type=str, default=".", help="Root directory of the repository")
    
    args = parser.parse_args()
    
    print(f"🔍 Query: {args.query}")
    if args.with_graph:
        print(f"🗺️  Mode: Hybrid RAG (Vector + Graph)")
    
    engine = EnhancedCodebaseQuery(
        index_path="./repo-index",
        repo_root=args.repo_root,
        use_graph=args.with_graph
    )
    
    result = engine.query_with_hybrid_rag(args.query, max_in_degree=args.max_in_degree)
    
    print("\n" + "="*60)
    print("VECTOR RESULTS:")
    print("="*60)
    for i, r in enumerate(result['vector_results'], 1):
        print(f"{i}. Score: {r['score']} | Preview: {r['text']}")
    
    if result['graph_context']:
        print("\n" + "="*60)
        print("GRAPH CONTEXT (Hydrated Code):")
        print("="*60)
        for ctx in result['graph_context']:
            print(ctx)
            print("-" * 40)
    
    print("\n" + "="*60)
    print("[Graph Metrics]")
    print("="*60)
    print(f"Expanded Nodes: {result['metrics']['expanded_nodes']}")
    print(f"Hydrated Snippets: {result['metrics']['hydrated_snippets']}")
    print(f"Filtered High-Degree Nodes: {result['metrics']['filtered_high_degree_nodes']}")
        
    def _load_index(self):
        """Lazy load the index and reranker."""
        if self._index is None:
            client = chromadb.PersistentClient(path=self.index_path)
            collection = client.get_collection("codebase")
            vector_store = ChromaVectorStore(chroma_collection=collection)
            
            # Use the same embedding model as build_index.py
            self._embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
            self._index = VectorStoreIndex.from_vector_store(
                vector_store, 
                embed_model=self._embed_model
            )
            
            # Initialize reranker if enabled
            if self.use_reranker and self._reranker is None:
                print("🔄 Loading reranker model (this may take a moment)...")
                try:
                    from llama_index.postprocessor.flag_embedding_reranker import FlagEmbeddingReranker
                    self._reranker = FlagEmbeddingReranker(
                        model="BAAI/bge-reranker-base",
                        top_n=5,
                        use_fp16=False  # Disable fp16 for compatibility
                    )
                except Exception as e:
                    print(f"⚠️  Reranker initialization failed: {e}")
                    print("💡 Falling back to embedding-only search")
                    self.use_reranker = False
                    self._reranker = None
        
        return self._index
    
    def query_codebase(
        self, 
        question: str, 
        top_k: int = 5,
        use_reranker: Optional[bool] = None
    ) -> List[Dict]:
        """
        Query the codebase with optional reranking for better accuracy.
        
        Args:
            question: Natural language question about the codebase
            top_k: Number of results to return
            use_reranker: Override default reranker setting
            
        Returns:
            List of dicts with keys: file, score, code, metadata
        """
        index = self._load_index()
        should_rerank = use_reranker if use_reranker is not None else self.use_reranker
        
        # Initial retrieval
        retriever = index.as_retriever(similarity_top_k=top_k * 2 if should_rerank else top_k)
        nodes = retriever.retrieve(question)
        
        # Apply reranker if enabled
        if should_rerank and self._reranker:
            try:
                nodes = self._reranker.postprocess_nodes(nodes, query_str=question)
                # Limit to top_k after reranking
                nodes = nodes[:top_k]
            except Exception as e:
                print(f"⚠️  Reranking failed: {e}")
                print("💡 Using original embedding results")
                nodes = nodes[:top_k]
        
        # Format results with enhanced metadata
        output = []
        for node in nodes:
            result = {
                "file": node.metadata.get("file_name", "Unknown"),
                "score": round(node.score, 3),
                "code": node.text,
                "metadata": {
                    "start_line": node.metadata.get("start_line"),
                    "end_line": node.metadata.get("end_line"),
                    "language": node.metadata.get("language", "python")
                }
            }
            output.append(result)
        
        return output
    
    def query_with_context(
        self, 
        question: str, 
        top_k: int = 5,
        include_call_graph: bool = False
    ) -> Dict:
        """
        Query with structured context for AI agents.
        
        Args:
            question: Natural language question
            top_k: Number of results
            include_call_graph: Whether to include call graph info
            
        Returns:
            Dict with formatted context for AI agents
        """
        results = self.query_codebase(question, top_k=top_k)
        
        # Format context for LLM
        context_text = "\n\n".join([
            f"### File: {r['file']}\n"
            f"**Relevance Score:** {r['score']}\n"
            f"```python\n{r['code']}\n```"
            for r in results
        ])
        
        response = {
            "question": question,
            "context": context_text,
            "results": results,
            "result_count": len(results)
        }
        
        return response


# Convenience function for backward compatibility
def query_codebase(question: str, top_k: int = 5, index_path="./repo-index"):
    """Simple query function (backward compatible)."""
    query_engine = EnhancedCodebaseQuery(index_path=index_path, use_reranker=True)
    return query_engine.query_codebase(question, top_k=top_k)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_query.py <question>")
        print("Example: python enhanced_query.py 'how does authentication work?'")
        sys.exit(1)
    
    question = " ".join(sys.argv[1:])
    print(f"🔍 Searching for: {question}\n")
    
    # Test with reranker
    query_engine = EnhancedCodebaseQuery(use_reranker=True)
    results = query_engine.query_codebase(question, top_k=3)
    
    if not results:
        print("❌ No results found")
    else:
        print(f"✅ Found {len(results)} relevant snippets (with reranker):\n")
        for i, r in enumerate(results, 1):
            print(f"--- Result {i} ---")
            print(f"File: {r['file']}")
            print(f"Score: {r['score']}")
            print(f"Lines: {r['metadata']['start_line']}-{r['metadata']['end_line']}")
            print(f"Code:\n{r['code'][:500]}...")
            print()
