import tree_sitter_python as tspython
from tree_sitter import Language, Parser
import os
from typing import List, Dict, Any

class PythonASTParser:
    def __init__(self):
        # Initialize the Python language from the tree-sitter-python package
        self.PY_LANGUAGE = Language(tspython.language(), "python")
        self.parser = Parser()
        self.parser.set_language(self.PY_LANGUAGE)

    def parse_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Parses a Python file and returns semantic chunks."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(filepath, "rb") as f:
            source_code_bytes = f.read()
            
        tree = self.parser.parse(source_code_bytes)
        
        chunks = []
        root_node = tree.root_node
        
        # Extract imports for file-level context
        imports = self._extract_imports(root_node, source_code_bytes)
        
        # Extract functions and classes
        for child in root_node.children:
            if child.type == "function_definition":
                chunks.append(self._create_chunk(child, source_code_bytes, "function", filepath, imports))
            elif child.type == "class_definition":
                chunks.append(self._create_chunk(child, source_code_bytes, "class", filepath, imports))
                
        # If no classes or functions, treat the whole file as a chunk
        if not chunks:
            source_code = source_code_bytes.decode("utf-8", errors="replace")
            chunks.append({
                "filepath": filepath,
                "type": "module",
                "content": source_code,
                "start_line": 1,
                "end_line": len(source_code.splitlines())
            })
            
        return chunks

    def extract_import_modules(self, filepath: str) -> List[str]:
        """Parses a Python file and returns a list of imported module/package names."""
        if not os.path.exists(filepath):
            return []
            
        with open(filepath, "rb") as f:
            source_code_bytes = f.read()
            
        tree = self.parser.parse(source_code_bytes)
        modules = []
        
        def traverse(node):
            if node.type == "import_statement":
                for child in node.children:
                    if child.type == "dotted_name":
                        modules.append(source_code_bytes[child.start_byte:child.end_byte].decode("utf-8", errors="ignore"))
                    elif child.type == "aliased_import":
                        for subchild in child.children:
                            if subchild.type == "dotted_name":
                                modules.append(source_code_bytes[subchild.start_byte:subchild.end_byte].decode("utf-8", errors="ignore"))
            elif node.type == "import_from_statement":
                for child in node.children:
                    if child.type == "dotted_name":
                        modules.append(source_code_bytes[child.start_byte:child.end_byte].decode("utf-8", errors="ignore"))
                        break
            for child in node.children:
                traverse(child)
                
        traverse(tree.root_node)
        return list(set(modules))

    def _extract_imports(self, root_node, source_code_bytes: bytes) -> str:
        """Extracts all import statements from the file to prepend as context."""
        imports = []
        for child in root_node.children:
            if child.type in ["import_statement", "import_from_statement"]:
                start_byte = child.start_byte
                end_byte = child.end_byte
                imports.append(source_code_bytes[start_byte:end_byte].decode("utf-8", errors="replace"))
        return "\n".join(imports)

    def _create_chunk(self, node, source_code_bytes: bytes, chunk_type: str, filepath: str, context: str) -> Dict[str, Any]:
        """Creates a semantic chunk enriched with context."""
        start_byte = node.start_byte
        end_byte = node.end_byte
        raw_content = source_code_bytes[start_byte:end_byte].decode("utf-8", errors="replace")
        
        # Prepend file-level imports as context so the LLM understands dependencies
        enriched_content = f"# File: {filepath}\n{context}\n\n{raw_content}" if context else f"# File: {filepath}\n\n{raw_content}"
        
        return {
            "filepath": filepath,
            "type": chunk_type,
            "content": enriched_content,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1
        }

