import tree_sitter_python as tspython
from tree_sitter import Language, Parser
import os
from typing import List, Dict, Any

class PythonASTParser:
    def __init__(self):
        # Initialize the Python language from the tree-sitter-python package
        self.PY_LANGUAGE = Language(tspython.language())
        self.parser = Parser(self.PY_LANGUAGE)

    def parse_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Parses a Python file and returns semantic chunks."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            source_code = f.read()
            
        tree = self.parser.parse(bytes(source_code, "utf8"))
        
        chunks = []
        root_node = tree.root_node
        
        # Extract imports for file-level context
        imports = self._extract_imports(root_node, source_code)
        
        # Extract functions and classes
        for child in root_node.children:
            if child.type == "function_definition":
                chunks.append(self._create_chunk(child, source_code, "function", filepath, imports))
            elif child.type == "class_definition":
                chunks.append(self._create_chunk(child, source_code, "class", filepath, imports))
                
        # If no classes or functions, treat the whole file as a chunk
        if not chunks:
            chunks.append({
                "filepath": filepath,
                "type": "module",
                "content": source_code,
                "start_line": 1,
                "end_line": len(source_code.splitlines())
            })
            
        return chunks

    def _extract_imports(self, root_node, source_code: str) -> str:
        """Extracts all import statements from the file to prepend as context."""
        imports = []
        for child in root_node.children:
            if child.type in ["import_statement", "import_from_statement"]:
                start_byte = child.start_byte
                end_byte = child.end_byte
                imports.append(source_code[start_byte:end_byte])
        return "\n".join(imports)

    def _create_chunk(self, node, source_code: str, chunk_type: str, filepath: str, context: str) -> Dict[str, Any]:
        """Creates a semantic chunk enriched with context."""
        start_byte = node.start_byte
        end_byte = node.end_byte
        raw_content = source_code[start_byte:end_byte]
        
        # Prepend file-level imports as context so the LLM understands dependencies
        enriched_content = f"# File: {filepath}\n{context}\n\n{raw_content}" if context else f"# File: {filepath}\n\n{raw_content}"
        
        return {
            "filepath": filepath,
            "type": chunk_type,
            "content": enriched_content,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1
        }
