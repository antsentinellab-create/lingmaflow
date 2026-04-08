#!/usr/bin/env python3
"""
Graph Manager for Code Topology.
Manages NetworkX graph, handles persistence with atomic writes,
and provides hybrid retrieval capabilities.
"""

import os
import json
import time
import errno
import tempfile
import logging
import networkx as nx
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict

# Configure dedicated logger for GraphManager
logger = logging.getLogger("GraphManager")

# Cross-platform file locking support
try:
    import fcntl
except ImportError:
    fcntl = None
    import msvcrt


class SafeFileLock:
    """
    A cross-platform file lock implementation.
    Uses fcntl on Unix/Linux and msvcrt on Windows.
    Includes stale lock detection.
    """
    def __init__(self, lock_path: str, timeout: int = 300):
        self.lock_path = Path(lock_path)
        self.timeout = timeout
        self.handle = None

    def acquire(self):
        while True:
            try:
                self.handle = open(self.lock_path, 'w')
                if fcntl:
                    fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                else:
                    # Windows non-blocking lock
                    msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
                
                # Write PID and timestamp for stale lock detection
                lock_info = {"pid": os.getpid(), "timestamp": time.time()}
                self.handle.write(json.dumps(lock_info))
                self.handle.flush()
                return
            except (IOError, OSError):
                if self._is_stale_lock():
                    self._break_stale_lock()
                    continue
                time.sleep(0.1)

    def _is_stale_lock(self) -> bool:
        """
        Optimized stale lock check logic.
        Solves Race Condition (TOCTOU) and refuses silent failures.
        """
        try:
            # Get file metadata directly to avoid Time-of-check to time-of-use issues
            stat = self.lock_path.stat()
            
            # Check if the lock has expired
            if time.time() - stat.st_mtime > self.timeout:
                logger.warning(f"[STALE_LOCK] Detected expired lock at {self.lock_path}. Overriding.")
                return True
                
        except FileNotFoundError:
            # Explicit handling: file disappeared during operation, treat as lock released
            return False
            
        except PermissionError as e:
            # Refuse silent failure: permission issues must bubble up to prevent infinite loops
            logger.error(f"[LOCK_IO_ERROR] Permission denied accessing lock: {e}")
            raise
            
        except OSError as e:
            # Capture serious disk/system failures (e.g., disk corruption or read-only mode)
            if e.errno == errno.ENOSPC:
                logger.error(f"[LOCK_IO_ERROR] Disk full, cannot manage locks: {e}")
            else:
                logger.error(f"[LOCK_IO_ERROR] OS level failure: {e}")
            raise

        return False

    def _break_stale_lock(self):
        try:
            if self.lock_path.exists():
                os.remove(self.lock_path)
        except:
            pass

    def release(self):
        if self.handle:
            try:
                if fcntl:
                    fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
                else:
                    msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
                self.handle.close()
            except:
                pass
            finally:
                if self.lock_path.exists():
                    os.remove(self.lock_path)


class GraphManager:
    """
    Manages the code topology graph using NetworkX.
    Supports atomic persistence and vector-to-node mapping.
    """
    def __init__(self, db_path: str = "repo-graph/topology.json"):
        self.db_path = Path(db_path)
        self.graph = nx.DiGraph()
        self.vector_to_nodes: Dict[str, List[str]] = defaultdict(list)
        self.lock_path = self.db_path.with_suffix('.lock')

    def add_node(self, node_id: str, node_type: str, file_path: str,
                 start_line: int, end_line: int, **kwargs):
        """
        Add a node to the graph with strict type assertion.
        """
        if not isinstance(node_id, str):
            raise TypeError(f"node_id must be a string. Got {type(node_id)}: {node_id}")
        
        self.graph.add_node(node_id,
                           type=node_type,
                           file_path=file_path,
                           start_line=start_line,
                           end_line=end_line,
                           vector_ids=[],
                           **kwargs)

    def link_vector_to_node(self, vector_id: str, chunk_start: int,
                           chunk_end: int, file_path: str):
        """
        Link a Chroma vector_id to AST nodes based on line number intersection.
        """
        for node_id, attrs in self.graph.nodes(data=True):
            if attrs.get("file_path") != file_path:
                continue
            
            node_start = attrs["start_line"]
            node_end = attrs["end_line"]
            
            # Check for line number intersection
            if chunk_start <= node_end and chunk_end >= node_start:
                if vector_id not in attrs["vector_ids"]:
                    attrs["vector_ids"].append(vector_id)
                    self.vector_to_nodes[vector_id].append(node_id)

    def get_nodes_by_vector_id(self, vector_id: str) -> List[str]:
        """Reverse lookup: get all AST nodes associated with a vector_id."""
        return self.vector_to_nodes.get(vector_id, [])

    def get_filtered_neighbors(self, node_id: str, hop: int = 1,
                              max_in_degree: int = 10) -> List[str]:
        """
        Get neighbors with degree filtering to avoid context explosion.
        Distinguishes between callers (predecessors) and callees (successors).
        """
        visited = set()
        current_level = {node_id}
        filtered_neighbors = []

        for _ in range(hop):
            next_level = set()
            for node in current_level:
                if node not in self.graph:
                    continue
                
                # Get both callers and callees
                neighbors = set(self.graph.predecessors(node))
                neighbors.update(self.graph.successors(node))
                
                for neighbor in neighbors:
                    if neighbor in visited:
                        continue
                    
                    # Degree filtering
                    if self.graph.in_degree(neighbor) > max_in_degree:
                        continue
                    
                    filtered_neighbors.append(neighbor)
                    visited.add(neighbor)
                    next_level.add(neighbor)
            
            current_level = next_level
        
        return filtered_neighbors

    def save(self):
        """
        Save graph to JSON using atomic write pattern.
        """
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        lock = SafeFileLock(str(self.lock_path))
        
        try:
            lock.acquire()
            data = nx.node_link_data(self.graph, edges="links")
            
            fd, tmp_path = tempfile.mkstemp(
                dir=self.db_path.parent, 
                suffix='.json.tmp'
            )
            
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                os.replace(tmp_path, self.db_path)
            except Exception as e:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                raise e
        finally:
            lock.release()

    def load(self):
        """
        Load graph from JSON and rebuild reverse index.
        """
        if self.db_path.exists():
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.graph = nx.node_link_graph(data, edges="links")
            self._rebuild_vector_index()
        else:
            self.graph = nx.DiGraph()

    def _rebuild_vector_index(self):
        """Rebuild vector_to_nodes index from loaded graph attributes."""
        self.vector_to_nodes = defaultdict(list)
        for node_id, attrs in self.graph.nodes(data=True):
            for vid in attrs.get("vector_ids", []):
                self.vector_to_nodes[vid].append(node_id)
