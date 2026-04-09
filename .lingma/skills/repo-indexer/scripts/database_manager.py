#!/usr/bin/env python3
"""
Database Manager for Repo Indexer.
Manages SQLite connections with WAL mode and provides basic CRUD operations
for nodes, edges, and vectors.
"""

import os
import sqlite3
import json
import logging
import struct
import itertools
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, Iterator

# Import sqlite-vec for high-performance vector search
try:
    import sqlite_vec
except ImportError:
    sqlite_vec = None
    logger.warning("sqlite-vec not installed. Vector search will be disabled.")

logger = logging.getLogger("DatabaseManager")

def serialize_float32(vector: List[float]) -> bytes:
    """Convert a list of floats to a binary blob for sqlite-vec using official API."""
    if sqlite_vec:
        return sqlite_vec.serialize_float32(vector)
    # Fallback to manual packing if sqlite_vec is not available
    return struct.pack(f'{len(vector)}f', *vector)

class DatabaseManager:
    """
    Manages the SQLite database for code topology and vector storage.
    Implements WAL mode for high-concurrency read/write operations.
    """
    
    def __init__(self, db_path: str = "repo-index/codebase.db", embedding_dim: int = 1536):
        self.db_path = Path(db_path)
        self.embedding_dim = embedding_dim
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._init_db()

    def _init_db(self):
        """Initialize database connection and configure PRAGMAs."""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
            
            # Enable sqlite-vec extension if available
            if sqlite_vec:
                sqlite_vec.load(self.conn)
            
            # Configure for performance and concurrency
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.execute("PRAGMA synchronous=NORMAL;")
            self.conn.execute("PRAGMA cache_size=-64000;")  # 64MB cache
            self.conn.execute("PRAGMA foreign_keys=ON;")
            
            logger.info(f"✅ Database initialized at {self.db_path} (WAL mode enabled)")
            self._create_tables()
            self._warmup_cache()
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
            raise

    def _create_tables(self):
        """Create schema tables if they don't exist."""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            start_line INTEGER NOT NULL,
            end_line INTEGER NOT NULL,
            metadata JSON
        );

        CREATE TABLE IF NOT EXISTS edges (
            source_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            relation_type TEXT NOT NULL,
            PRIMARY KEY (source_id, target_id, relation_type),
            FOREIGN KEY(source_id) REFERENCES nodes(id) ON DELETE CASCADE,
            FOREIGN KEY(target_id) REFERENCES nodes(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS vectors (
            vector_id TEXT PRIMARY KEY,
            node_id TEXT NOT NULL, -- Can reference nodes.id or be a custom identifier
            embedding BLOB NOT NULL,
            code_content TEXT,
            chunk_start INTEGER,
            chunk_end INTEGER
        );

        -- Performance Indexes
        CREATE INDEX IF NOT EXISTS idx_nodes_file_path ON nodes(file_path);
        CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
        CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
        CREATE INDEX IF NOT EXISTS idx_vectors_node_id ON vectors(node_id);

        -- Virtual Table for Vector Search (Dimension is parameterized)
        """
        if sqlite_vec:
            schema_sql += f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS vec_nodes USING vec0(
                vector_id TEXT PRIMARY KEY,
                node_id TEXT,
                embedding FLOAT[{self.embedding_dim}]
            );
            """
        self.conn.executescript(schema_sql)
        self.conn.commit()

    def _warmup_cache(self):
        """
        Warm up the OS page cache by scanning the vector index.
        This ensures subsequent AI queries achieve 'instant-on' performance.
        """
        try:
            if sqlite_vec:
                self.conn.execute("SELECT count(*) FROM vec_nodes")
            self.conn.execute("SELECT count(*) FROM nodes")
            self.conn.execute("SELECT count(*) FROM edges")
            logger.info("🔥 Database cache warmed up successfully")
        except Exception as e:
            logger.warning(f"Cache warm-up skipped (tables might be empty): {e}")

    # --- Node Operations ---

    def add_node(self, node_id: str, node_type: str, file_path: str, 
                 start_line: int, end_line: int, metadata: Dict = None):
        """Add or update a single node."""
        meta_json = json.dumps(metadata) if metadata else None
        try:
            self.conn.execute(
                "INSERT OR REPLACE INTO nodes VALUES (?, ?, ?, ?, ?, ?)",
                (node_id, node_type, file_path, start_line, end_line, meta_json)
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to add node {node_id}: {e}")
            self.conn.rollback()
            raise

    def add_nodes_batch(self, nodes: Iterator[Tuple] | List[Tuple], batch_size: int = 5000):
        """
        Batch insert nodes using a generator to minimize RAM usage.
        
        Args:
            nodes: An iterator or list of node tuples.
            batch_size: Number of records per transaction (default 5000).
        """
        if isinstance(nodes, list):
            nodes = iter(nodes)
            
        while True:
            batch = list(itertools.islice(nodes, batch_size))
            if not batch:
                break
            try:
                with self.conn:
                    self.conn.executemany(
                        "INSERT OR REPLACE INTO nodes VALUES (?, ?, ?, ?, ?, ?)",
                        batch
                    )
                logger.info(f"📦 Committed batch of {len(batch)} nodes")
            except Exception as e:
                logger.error(f"Failed batch node insertion: {e}")
                raise

    def execute_in_transaction(self, operations_func):
        """
        Execute a series of operations within a single transaction.
        Ensures atomicity: either all succeed or all are rolled back.
        
        Args:
            operations_func: A function that takes the connection and performs DB ops.
        """
        try:
            self.conn.execute("BEGIN TRANSACTION;")
            operations_func(self.conn)
            self.conn.commit()
            logger.info("✅ Transaction committed successfully")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ Transaction failed, rolled back: {e}")
            raise

    def get_node(self, node_id: str) -> Optional[Dict]:
        """Retrieve a single node by ID."""
        cursor = self.conn.execute("SELECT * FROM nodes WHERE id = ?", (node_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_nodes_batch(self, node_ids: List[str]) -> Dict[str, Dict]:
        """
        Batch fetch nodes by IDs to avoid N+1 query problem.
        Returns a dictionary mapping node_id to node metadata.
        """
        if not node_ids:
            return {}
        
        # Use placeholders for SQL IN clause
        placeholders = ','.join('?' * len(node_ids))
        query = f"SELECT * FROM nodes WHERE id IN ({placeholders})"
        
        cursor = self.conn.execute(query, node_ids)
        return {row['id']: dict(row) for row in cursor.fetchall()}

    # --- Edge Operations ---

    def add_edge(self, source_id: str, target_id: str, relation_type: str):
        """Add a relationship between two nodes."""
        try:
            self.conn.execute(
                "INSERT OR IGNORE INTO edges VALUES (?, ?, ?)",
                (source_id, target_id, relation_type)
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to add edge {source_id}->{target_id}: {e}")
            self.conn.rollback()
            raise

    def add_edges_batch(self, edges: Iterator[Tuple] | List[Tuple], batch_size: int = 10000):
        """
        Batch insert edges using a generator to minimize RAM usage.
        
        Args:
            edges: An iterator or list of edge tuples (source, target, relation).
            batch_size: Number of records per transaction (default 10000).
        """
        if isinstance(edges, list):
            edges = iter(edges)
            
        while True:
            batch = list(itertools.islice(edges, batch_size))
            if not batch:
                break
            try:
                with self.conn:
                    self.conn.executemany(
                        "INSERT OR IGNORE INTO edges VALUES (?, ?, ?)",
                        batch
                    )
                logger.info(f"🔗 Committed batch of {len(batch)} edges")
            except Exception as e:
                logger.error(f"Failed batch edge insertion: {e}")
                raise

    def get_predecessors(self, node_id: str, depth: int = 1) -> List[str]:
        """Get callers using Recursive CTE."""
        query = """
        WITH RECURSIVE call_chain AS (
            SELECT source_id, 1 as d FROM edges WHERE target_id = ?
            UNION ALL
            SELECT e.source_id, cc.d + 1 
            FROM edges e 
            JOIN call_chain cc ON e.target_id = cc.source_id 
            WHERE cc.d < ?
        )
        SELECT DISTINCT source_id FROM call_chain;
        """
        cursor = self.conn.execute(query, (node_id, depth))
        return [row[0] for row in cursor.fetchall()]

    def get_successors(self, node_id: str, depth: int = 1) -> List[str]:
        """Get callees using Recursive CTE."""
        query = """
        WITH RECURSIVE call_chain AS (
            SELECT target_id, 1 as d FROM edges WHERE source_id = ?
            UNION ALL
            SELECT e.target_id, cc.d + 1 
            FROM edges e 
            JOIN call_chain cc ON e.source_id = cc.target_id 
            WHERE cc.d < ?
        )
        SELECT DISTINCT target_id FROM call_chain;
        """
        cursor = self.conn.execute(query, (node_id, depth))
        return [row[0] for row in cursor.fetchall()]

    def get_call_chain_with_depth(self, start_node_id: str, direction: str = "forward", max_depth: int = 3) -> List[Tuple[str, int]]:
        """
        Get the full call chain with depth information.
        Handles both forward (callees) and backward (callers) traversal.
        """
        if direction == "forward":
            # Find nodes that this node calls (Source -> Target)
            query = """
            WITH RECURSIVE call_chain AS (
                SELECT target_id as connected_id, 1 as depth FROM edges WHERE source_id = ?
                UNION ALL
                SELECT e.target_id, cc.depth + 1 
                FROM edges e 
                JOIN call_chain cc ON e.source_id = cc.connected_id 
                WHERE cc.depth < ?
            )
            SELECT connected_id, MIN(depth) as min_depth FROM call_chain GROUP BY connected_id ORDER BY min_depth;
            """
        else: # backward
            # Find nodes that call this node (Target <- Source)
            query = """
            WITH RECURSIVE call_chain AS (
                SELECT source_id as connected_id, 1 as depth FROM edges WHERE target_id = ?
                UNION ALL
                SELECT e.source_id, cc.depth + 1 
                FROM edges e 
                JOIN call_chain cc ON e.target_id = cc.connected_id 
                WHERE cc.depth < ?
            )
            SELECT connected_id, MIN(depth) as min_depth FROM call_chain GROUP BY connected_id ORDER BY min_depth;
            """
        
        cursor = self.conn.execute(query, (start_node_id, max_depth))
        return cursor.fetchall()

    def find_shortest_path(self, source_id: str, target_id: str, max_depth: int = 10) -> Optional[List[str]]:
        """
        Find the shortest path between two nodes using BFS-like recursive CTE.
        Uses comma-delimited path matching to prevent sub-string false positives.
        """
        query = """
        WITH RECURSIVE search_path AS (
            SELECT 
                ? as current_id,
                CAST(? AS TEXT) as path,
                0 as depth
            UNION ALL
            SELECT 
                e.target_id,
                sp.path || ',' || e.target_id,
                sp.depth + 1
            FROM edges e
            JOIN search_path sp ON e.source_id = sp.current_id
            WHERE sp.depth < ?
            AND INSTR(',' || sp.path || ',', ',' || e.target_id || ',') = 0 -- Prevent cycles with boundary check
        )
        SELECT path FROM search_path WHERE current_id = ? LIMIT 1;
        """
        cursor = self.conn.execute(query, (source_id, source_id, max_depth, target_id))
        result = cursor.fetchone()
        if result:
            return result[0].split(',')
        return None

    # --- Vector Operations ---

    def add_vector(self, vector_id: str, node_id: str, embedding: bytes, 
                   code_content: str = None, chunk_start: int = None, 
                   chunk_end: int = None):
        """Store a single vector embedding."""
        try:
            self.conn.execute(
                "INSERT OR REPLACE INTO vectors VALUES (?, ?, ?, ?, ?, ?)",
                (vector_id, node_id, embedding, code_content, chunk_start, chunk_end)
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to add vector {vector_id}: {e}")
            self.conn.rollback()
            raise

    def add_vectors_batch(self, vectors_data: List[Tuple]):
        """
        Batch insert vectors into vec_nodes virtual table using a transaction.
        This is 50-100x faster than individual inserts for large datasets.
        
        Args:
            vectors_data: List of tuples (vector_id, node_id, binary_embedding).
        """
        if not sqlite_vec:
            logger.error("sqlite-vec not loaded. Cannot batch insert vectors.")
            return

        try:
            with self.conn: # Automatically handles BEGIN TRANSACTION and COMMIT
                self.conn.executemany(
                    "INSERT OR REPLACE INTO vec_nodes(vector_id, node_id, embedding) VALUES (?, ?, ?)",
                    vectors_data
                )
            logger.info(f"🚀 Batch inserted {len(vectors_data)} vectors into vec_nodes")
        except Exception as e:
            logger.error(f"Failed batch vector insertion: {e}")
            raise

    def add_vectors_metadata_batch(self, metadata_list: List[Tuple]):
        """
        Batch insert vector metadata into the 'vectors' table.
        
        Args:
            metadata_list: List of tuples (vector_id, node_id, embedding, code_content, chunk_start, chunk_end).
        """
        try:
            with self.conn:
                self.conn.executemany(
                    "INSERT OR REPLACE INTO vectors VALUES (?, ?, ?, ?, ?, ?)",
                    metadata_list
                )
            logger.info(f"🚀 Batch inserted {len(metadata_list)} vector metadata records")
        except Exception as e:
            logger.error(f"Failed batch metadata insertion: {e}")
            raise

    def get_vectors_by_node(self, node_id: str) -> List[Dict]:
        """Get all vectors associated with a node."""
        cursor = self.conn.execute(
            "SELECT * FROM vectors WHERE node_id = ?", (node_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def hybrid_search(self, query_embedding: List[float] | bytes, limit: int = 5, graph_depth: int = 2, alpha: float = 0.7) -> List[Dict]:
        """
        Advanced Hybrid Search: Combines Vector Similarity with Graph Traversal.
        
        Formula: score = alpha * vector_sim + (1 - alpha) * (1 / (graph_dist + 1))
        
        Args:
            query_embedding: The query vector (list of floats or pre-serialized bytes).
            limit: Number of final results to return.
            graph_depth: How many hops to traverse from vector matches.
            alpha: Weight for vector similarity (0.0 to 1.0).
        """
        if not sqlite_vec:
            logger.error("sqlite-vec is not loaded.")
            return []

        # Step 1: Vector Search to get initial candidates
        # Only serialize if input is a list, otherwise assume it's already serialized
        binary_query = serialize_float32(query_embedding) if isinstance(query_embedding, list) else query_embedding
        cursor = self.conn.execute(
            "SELECT vector_id, node_id, vec_distance_cosine(embedding, ?) as dist FROM vec_nodes ORDER BY dist ASC LIMIT ?",
            (binary_query, limit * 2) # Fetch more candidates for graph expansion
        )
        # Map node_id to (vector_id, distance)
        vector_results = {}
        for row in cursor.fetchall():
            vid, nid, dist = row
            if nid not in vector_results:  # Keep the closest vector for each node
                vector_results[nid] = (vid, dist)
        
        if not vector_results:
            return []

        # Step 2: Graph Traversal & Scoring
        final_scores = {}
        all_neighbor_ids = []
        neighbor_info = {} # Map ID to (seed_vec_dist, depth)

        for seed_node_id, (seed_vector_id, vec_dist) in vector_results.items():
            vec_score = 1.0 - vec_dist
            
            # Always include the seed node itself with depth 0
            if seed_node_id not in neighbor_info:
                neighbor_info[seed_node_id] = (vec_dist, 0)
                all_neighbor_ids.append(seed_node_id)
            
            # Get neighbors via CTE (only if graph_depth > 0)
            if graph_depth > 0:
                neighbors = self.get_call_chain_with_depth(seed_node_id, direction="backward", max_depth=graph_depth)
                
                for neighbor_id, depth in neighbors:
                    if neighbor_id not in neighbor_info:
                        neighbor_info[neighbor_id] = (vec_dist, depth)
                        all_neighbor_ids.append(neighbor_id)

        # Batch fetch metadata for all unique neighbors at once
        nodes_meta = self.get_nodes_batch(all_neighbor_ids)

        # Calculate combined scores
        for neighbor_id, (seed_vec_dist, depth) in neighbor_info.items():
            vec_score = 1.0 - seed_vec_dist
            graph_score = 1.0 / (depth + 1)
            
            # Combined Score with alpha weighting
            combined = alpha * vec_score + (1 - alpha) * graph_score
            
            meta = nodes_meta.get(neighbor_id)
            if meta:
                final_scores[neighbor_id] = {
                    'node_id': neighbor_id,
                    'score': combined,
                    'vector_dist': seed_vec_dist,
                    'graph_depth': depth,
                    'metadata': meta
                }

        # Sort by combined score and return top N
        sorted_results = sorted(final_scores.values(), key=lambda x: x['score'], reverse=True)[:limit]
        return sorted_results

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("🔒 Database connection closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
