#!/usr/bin/env python3
"""
Precision Line Code Splitter.
Extends LlamaIndex CodeSplitter to track exact character offsets and line numbers,
preventing "ghost mapping" errors caused by boilerplate code.
"""

from llama_index.core.node_parser import CodeSplitter
from llama_index.core.schema import Document, TextNode
from typing import List


class PrecisionLineCodeSplitter(CodeSplitter):
    """
    Industrial-grade splitter that tracks character offsets to calculate 
    precise line numbers for every chunk.
    """
    
    def get_nodes_from_documents(
        self, documents: List[Document], **kwargs
    ) -> List[TextNode]:
        nodes = []
        
        for doc in documents:
            file_path = doc.metadata.get("file_path", "")
            
            # Task 3.4: Cross-platform newline normalization
            try:
                with open(file_path, 'r', encoding='utf-8', newline='') as f:
                    raw_content = f.read()
            except Exception:
                continue
            
            # Normalize to LF to ensure consistent char_offset calculation
            content = raw_content.replace('\r\n', '\n').replace('\r', '\n')
            
            # Get chunks from the parent splitter logic
            # Note: We use split_text to get the raw string chunks first
            raw_chunks = self.split_text(content)
            
            current_pos = 0
            
            for chunk_text in raw_chunks:
                # Task 3.3 - 3.5: Char Offset Tracking with Strip-Matching Resilience
                # LlamaIndex may trim whitespace, so we strip for matching but track original offset
                stripped_chunk = chunk_text.strip()
                if not stripped_chunk:
                    continue
                    
                start_pos = content.find(stripped_chunk, current_pos)
                
                if start_pos == -1:
                    # Fallback: try to find the chunk with some tolerance or skip to maintain accuracy
                    # For now, we skip to ensure 100% precision (better to miss than to misalign)
                    continue
                
                # Calculate line numbers based on the START of the matched stripped content
                start_line = content[:start_pos].count('\n') + 1
                end_line = start_line + chunk_text.count('\n')
                
                # Task 3.6: Inject precise metadata
                node = TextNode(
                    text=chunk_text,
                    metadata={
                        "file_path": file_path,
                        "start_line": start_line,
                        "end_line": end_line,
                        "char_offset": start_pos
                    }
                )
                nodes.append(node)
                
                # Move pointer forward past the matched content
                current_pos = start_pos + len(stripped_chunk)
        
        return nodes
