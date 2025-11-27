import ast
from typing import List, Dict, Any, Optional

class MirageDetector(ast.NodeVisitor):
    """
    AST visitor that detects destructive operations that collapse physical information
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.mirages: List[Dict[str, Any]] = []
        self.current_function: Optional[str] = None
        self.config = config or {}
        
    def visit_Call(self, node: ast.Call) -> None:
        """Detect destructive numpy operations"""
        if isinstance(node.func, ast.Attribute):
            # Detect np.mean(), np.sum(), etc.
            if (isinstance(node.func.value, ast.Name) and 
                node.func.value.id in ['np', 'numpy']):
                
                if node.func.attr in ['mean', 'sum', 'argmax', 'argmin']:
                    self.mirages.append({
                        'type': node.func.attr,
                        'node': node,
                        'line': node.lineno,
                        'col': node.col_offset,
                        'function': self.current_function
                    })
        
        # Check for premature discretization
        if isinstance(node.func, ast.Name) and node.func.id in ['round', 'int']:
            if len(node.args) > 0 and self._is_array_like(node.args[0]):
                self.mirages.append({
                    'type': 'premature_discretization',
                    'node': node,
                    'line': node.lineno,
                    'col': node.col_offset,
                    'function': self.current_function
                })
        
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track current function context"""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function
    
    def _is_array_like(self, node: ast.AST) -> bool:
        """Heuristic to determine if a node represents array-like data"""
        if isinstance(node, ast.Name):
            # More general heuristic: any variable that might contain numeric data
            return True  # Be more permissive for now
        return False
