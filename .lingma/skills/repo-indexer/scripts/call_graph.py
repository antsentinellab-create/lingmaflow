#!/usr/bin/env python3
"""
Call graph analyzer using tree-sitter.
Builds function call relationships for better code understanding.
"""

import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json


class CallGraphAnalyzer:
    """Analyzes Python code to build call graphs."""
    
    def __init__(self):
        self.language = Language(tspython.language())
        self.parser = Parser(self.language)
        
        # Store call relationships: {caller: [callee1, callee2, ...]}
        self.call_graph: Dict[str, Set[str]] = {}
        # Store function definitions: {file: {function_name: line_number}}
        self.function_defs: Dict[str, Dict[str, int]] = {}
        
    def parse_file_to_graph(self, file_path: str, graph_manager, rel_path: str = None) -> bool:
        """
        Parse a Python file and add AST nodes to the GraphManager.
        
        Returns:
            True if parsing was successful, False otherwise.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            tree = self.parser.parse(bytes(source_code, "utf8"))
            root_node = tree.root_node
            
            # Use relative path if provided, otherwise use absolute
            node_file_path = rel_path if rel_path else file_path
            
            # Task: Create a module-level node to catch bare code (e.g., __main__ logic)
            module_node_id = f"module:{node_file_path}"
            graph_manager.add_node(
                node_id=module_node_id,
                node_type="module",
                file_path=node_file_path,
                start_line=1,
                end_line=len(source_code.splitlines())
            )
            
            # Extract function/class definitions and add to graph
            has_nodes = self._extract_nodes_to_graph(root_node, graph_manager, node_file_path, source_code, parent_id=module_node_id)
            
            # Also extract call relationships for edges
            functions = self._extract_functions(root_node, file_path)
            
            for func_name, func_node in functions.items():
                calls = self._extract_calls(func_node)
                
                # Add edges between caller and callees
                for callee in calls:
                    try:
                        graph_manager.graph.add_edge(func_name, callee)
                    except:
                        pass  # Edge creation may fail if nodes don't exist yet
            
            return True
                    
        except Exception as e:
            print(f"⚠️  [MISSING_GRAPH_NODES] Failed to parse {file_path}: {e}")
            return False
    
    def _extract_nodes_to_graph(self, node, graph_manager, file_path: str, source_code: str, parent_id: str = None) -> bool:
        """Extract AST nodes and add them to the graph with line numbers."""
        has_nodes = False
        
        if node.type in ['function_definition', 'class_definition']:
            # Get node name
            name_node = node.child_by_field_name('name')
            if name_node:
                node_name = name_node.text.decode('utf-8')
                
                # Calculate line numbers
                start_line = node.start_point[0] + 1  # tree-sitter uses 0-based indexing
                end_line = node.end_point[0] + 1
                
                node_type = 'function' if node.type == 'function_definition' else 'class'
                
                # Add node to graph with strict type assertion
                graph_manager.add_node(
                    node_id=node_name,
                    node_type=node_type,
                    file_path=file_path,
                    start_line=start_line,
                    end_line=end_line
                )
                
                # Link to parent (module or class)
                if parent_id:
                    try:
                        graph_manager.graph.add_edge(parent_id, node_name)
                    except:
                        pass
                
                has_nodes = True
        
        # Recursively process child nodes
        for child in node.children:
            if self._extract_nodes_to_graph(child, graph_manager, file_path, source_code, parent_id):
                has_nodes = True
                
        return has_nodes
    
    def parse_file(self, file_path: str) -> None:
        """Parse a single Python file and extract call relationships."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            tree = self.parser.parse(bytes(source_code, "utf8"))
            root_node = tree.root_node
            
            # Extract function definitions
            functions = self._extract_functions(root_node, file_path)
            
            # Extract function calls within each function
            for func_name, func_node in functions.items():
                calls = self._extract_calls(func_node)
                
                if func_name not in self.call_graph:
                    self.call_graph[func_name] = set()
                self.call_graph[func_name].update(calls)
                
        except Exception as e:
            print(f"⚠️  Error parsing {file_path}: {e}")
    
    def _extract_functions(self, node, file_path: str) -> Dict[str, any]:
        """Extract all function definitions from AST."""
        functions = {}
        
        if node.type == 'function_definition':
            # Get function name
            for child in node.children:
                if child.type == 'identifier':
                    func_name = child.text.decode('utf-8')
                    functions[func_name] = node
                    
                    # Store function definition location
                    if file_path not in self.function_defs:
                        self.function_defs[file_path] = {}
                    self.function_defs[file_path][func_name] = node.start_point[0] + 1
                    break
        
        # Recursively process children
        for child in node.children:
            functions.update(self._extract_functions(child, file_path))
        
        return functions
    
    def _extract_calls(self, node) -> Set[str]:
        """Extract all function calls from a node."""
        calls = set()
        
        if node.type == 'call':
            # Get the called function name
            func_name_node = node.child_by_field_name('function')
            if func_name_node:
                if func_name_node.type == 'identifier':
                    calls.add(func_name_node.text.decode('utf-8'))
                elif func_name_node.type == 'attribute':
                    # Handle method calls like obj.method()
                    calls.add(func_name_node.text.decode('utf-8'))
        
        # Recursively process children
        for child in node.children:
            calls.update(self._extract_calls(child))
        
        return calls
    
    def analyze_directory(self, directory: str, extensions: List[str] = ['.py']) -> None:
        """Analyze all Python files in a directory."""
        path = Path(directory)
        python_files = []
        
        for ext in extensions:
            python_files.extend(path.rglob(f'*{ext}'))
        
        print(f"📊 Analyzing {len(python_files)} files for call graph...")
        
        for file_path in python_files:
            self.parse_file(str(file_path))
        
        print(f"✅ Found {len(self.call_graph)} functions with call relationships")
    
    def get_callers(self, function_name: str) -> List[str]:
        """Find all functions that call the given function."""
        callers = []
        for caller, callees in self.call_graph.items():
            if function_name in callees:
                callers.append(caller)
        return callers
    
    def get_callees(self, function_name: str) -> List[str]:
        """Find all functions called by the given function."""
        return list(self.call_graph.get(function_name, set()))
    
    def find_call_chain(self, start_func: str, max_depth: int = 5) -> List[List[str]]:
        """Find call chains starting from a function."""
        chains = []
        self._dfs_call_chain(start_func, [start_func], chains, max_depth, set())
        return chains
    
    def _dfs_call_chain(
        self, 
        current: str, 
        path: List[str], 
        chains: List[List[str]], 
        max_depth: int,
        visited: Set[str]
    ) -> None:
        """DFS to find call chains."""
        if len(path) > 1:
            chains.append(path.copy())
        
        if len(path) >= max_depth:
            return
        
        callees = self.get_callees(current)
        for callee in callees:
            if callee not in visited:
                visited.add(callee)
                path.append(callee)
                self._dfs_call_chain(callee, path, chains, max_depth, visited)
                path.pop()
                visited.discard(callee)
    
    def export_to_json(self, output_path: str) -> None:
        """Export call graph to JSON file."""
        # Convert sets to lists for JSON serialization
        serializable_graph = {
            caller: list(callees) 
            for caller, callees in self.call_graph.items()
        }
        
        data = {
            "call_graph": serializable_graph,
            "function_definitions": self.function_defs
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Call graph exported to: {output_path}")
    
    def query_related_functions(self, question: str, query_results: List[Dict]) -> List[Dict]:
        """
        Enhance query results with related functions from call graph.
        
        Args:
            question: Original query
            query_results: Results from vector search
            
        Returns:
            Enhanced results with related functions
        """
        enhanced_results = []
        
        for result in query_results:
            file_path = result['file']
            
            # Find functions in this file
            if file_path in self.function_defs:
                functions_in_file = list(self.function_defs[file_path].keys())
                
                # Get call relationships for these functions
                related_funcs = set()
                for func in functions_in_file:
                    # Add callees (functions this function calls)
                    related_funcs.update(self.get_callees(func))
                    # Add callers (functions that call this function)
                    related_funcs.update(self.get_callers(func))
                
                result['related_functions'] = list(related_funcs)[:10]  # Limit to 10
            
            enhanced_results.append(result)
        
        return enhanced_results


def build_call_graph(directory: str = ".", output_file: str = "call_graph.json"):
    """Build call graph for a directory."""
    analyzer = CallGraphAnalyzer()
    analyzer.analyze_directory(directory)
    analyzer.export_to_json(output_file)
    return analyzer


if __name__ == "__main__":
    import sys
    
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    output_file = sys.argv[2] if len(sys.argv) > 2 else "call_graph.json"
    
    print(f"🔍 Building call graph for: {directory}")
    analyzer = build_call_graph(directory, output_file)
    
    # Show some statistics
    print(f"\n📊 Statistics:")
    print(f"   Total functions: {len(analyzer.call_graph)}")
    print(f"   Total call relationships: {sum(len(callees) for callees in analyzer.call_graph.values())}")
    
    # Example: Show call chain for a function
    if analyzer.call_graph:
        sample_func = list(analyzer.call_graph.keys())[0]
        chains = analyzer.find_call_chain(sample_func, max_depth=3)
        if chains:
            print(f"\n🔗 Sample call chain for '{sample_func}':")
            for i, chain in enumerate(chains[:3], 1):
                print(f"   {i}. {' -> '.join(chain)}")
