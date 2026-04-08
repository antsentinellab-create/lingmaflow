#!/usr/bin/env python3
"""
Migration Script: JSON Topology to SQLite.
Converts the existing NetworkX JSON graph into the new SQLite schema.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add scripts directory to path
sys.path.append(os.path.dirname(__file__))
from database_manager import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MigrationScript")

def migrate_data(json_path="repo-graph/topology.json", db_path="repo-index/codebase.db"):
    """
    Migrate data from JSON topology file to SQLite database.
    Uses transaction control to ensure atomicity.
    """
    json_file = Path(json_path)
    if not json_file.exists():
        logger.error(f"❌ JSON file not found: {json_path}")
        return

    logger.info(f"📂 Loading topology from {json_path}...")
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"❌ Failed to load JSON: {e}")
        return

    nodes_data = data.get("nodes", [])
    links_data = data.get("links", [])
    
    logger.info(f"📊 Found {len(nodes_data)} nodes and {len(links_data)} edges.")

    # Initialize Database Manager
    db = DatabaseManager(db_path=db_path)
    
    try:
        # --- Migrate Nodes ---
        def insert_nodes(conn):
            node_tuples = [
                (
                    n["id"], 
                    n.get("type", "unknown"), 
                    n.get("file_path", ""), 
                    n.get("start_line", 0), 
                    n.get("end_line", 0), 
                    json.dumps({k: v for k, v in n.items() if k not in ["id", "type", "file_path", "start_line", "end_line"]})
                )
                for n in nodes_data
            ]
            conn.executemany(
                "INSERT OR REPLACE INTO nodes VALUES (?, ?, ?, ?, ?, ?)",
                node_tuples
            )
            logger.info(f"✅ Prepared {len(node_tuples)} nodes for insertion.")

        logger.info("🚀 Starting node migration transaction...")
        db.execute_in_transaction(insert_nodes)

        # --- Migrate Edges ---
        def insert_edges(conn):
            edge_tuples = [
                (link["source"], link["target"], link.get("relation_type", "CALLS"))
                for link in links_data
            ]
            conn.executemany(
                "INSERT OR IGNORE INTO edges VALUES (?, ?, ?)",
                edge_tuples
            )
            logger.info(f"✅ Prepared {len(edge_tuples)} edges for insertion.")

        logger.info("🚀 Starting edge migration transaction...")
        db.execute_in_transaction(insert_edges)

        logger.info("✨ Migration completed successfully!")
        
        # Verification
        cursor = db.conn.execute("SELECT COUNT(*) FROM nodes")
        node_count = cursor.fetchone()[0]
        cursor = db.conn.execute("SELECT COUNT(*) FROM edges")
        edge_count = cursor.fetchone()[0]
        logger.info(f"📈 Verification: {node_count} nodes and {edge_count} edges in SQLite.")

    except Exception as e:
        logger.error(f"💥 Migration failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_data()
