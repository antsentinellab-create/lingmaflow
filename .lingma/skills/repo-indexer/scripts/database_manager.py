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
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

logger = logging.getLogger("DatabaseManager")

class DatabaseManager:
    """
    Manages the SQLite database for code topology and vector storage.
    Implements WAL mode for high-concurrency read/write operations.
    """
    
    def __init__(self, db_path: str = "repo-index/codebase.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._init_db()

    def _init_db(self):
        """Initialize database connection and configure PRAGMAs."""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
            
            # Configure for performance and concurrency
            self.conn.execute("PRAGMA journal_mode=WAL;")
            self.conn.execute("PRAGMA synchronous=NORMAL;")
            self.conn.execute("PRAGMA cache_size=-64000;")  # 64MB cache
            self.conn.execute("PRAGMA foreign_keys=ON;")
            
            logger.info(f"✅ Database initialized at {self.db_path} (WAL mode enabled)")
            self._create_tables()
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
            node_id TEXT NOT NULL,
            embedding BLOB NOT NULL,
            code_content TEXT,
            chunk_start INTEGER,
            chunk_end INTEGER,
            FOREIGN KEY(node_id) REFERENCES nodes(id) ON DELETE CASCADE
        );

        -- Performance Indexes
        CREATE INDEX IF NOT EXISTS idx_nodes_file_path ON nodes(file_path);
        CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
        CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
        CREATE INDEX IF NOT EXISTS idx_vectors_node_id ON vectors(node_id);
        """
        self.conn.executescript(schema_sql)
        self.conn.commit()

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

    def add_nodes_batch(self, nodes: List[Tuple]):
        """Batch insert nodes for better performance (Auto-commits)."""
        try:
            self.conn.executemany(
                "INSERT OR REPLACE INTO nodes VALUES (?, ?, ?, ?, ?, ?)",
                nodes
            )
            self.conn.commit()
            logger.info(f"📦 Batch inserted {len(nodes)} nodes")
        except Exception as e:
            logger.error(f"Failed batch node insertion: {e}")
            self.conn.rollback()
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

    def add_edges_batch(self, edges: List[Tuple]):
        """Batch insert edges."""
        try:
            self.conn.executemany(
                "INSERT OR IGNORE INTO edges VALUES (?, ?, ?)",
                edges
            )
            self.conn.commit()
            logger.info(f"🔗 Batch inserted {len(edges)} edges")
        except Exception as e:
            logger.error(f"Failed batch edge insertion: {e}")
            self.conn.rollback()
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

    # --- Vector Operations ---

    def add_vector(self, vector_id: str, node_id: str, embedding: bytes, 
                   code_content: str = None, chunk_start: int = None, 
                   chunk_end: int = None):
        """Store a vector embedding."""
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

    def get_vectors_by_node(self, node_id: str) -> List[Dict]:
        """Get all vectors associated with a node."""
        cursor = self.conn.execute(
            "SELECT * FROM vectors WHERE node_id = ?", (node_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("🔒 Database connection closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
