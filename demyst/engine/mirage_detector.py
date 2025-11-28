import ast
from typing import Any, Dict, List, Optional, Set, Tuple


class VarianceContextCollector(ast.NodeVisitor):
    """
    First-pass collector that identifies all variance operations (std, var)
    and the variables they operate on, indexed by line number.
    """

    # Operations that compute variance/spread - these preserve uncertainty info
    VARIANCE_OPS = {"std", "var", "nanstd", "nanvar", "std_", "var_"}

    def __init__(self) -> None:
        # Map: (variable_name, function_scope) -> set of line numbers where variance computed
        self.variance_contexts: Dict[Tuple[Optional[str], Optional[str]], Set[int]] = {}
        self.current_function: Optional[str] = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_Call(self, node: ast.Call) -> None:
        """Collect variance operations."""
        var_name = None
        is_variance_op = False

        # Check for np.std(x), np.var(x)
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id in ["np", "numpy"]:
                if node.func.attr in self.VARIANCE_OPS:
                    is_variance_op = True
                    if node.args and isinstance(node.args[0], ast.Name):
                        var_name = node.args[0].id

            # Check for x.std(), x.var() (array method calls)
            elif node.func.attr in self.VARIANCE_OPS:
                is_variance_op = True
                if isinstance(node.func.value, ast.Name):
                    var_name = node.func.value.id

        if is_variance_op:
            key = (var_name, self.current_function)
            if key not in self.variance_contexts:
                self.variance_contexts[key] = set()
            self.variance_contexts[key].add(node.lineno)

        self.generic_visit(node)


class MirageDetector(ast.NodeVisitor):
    """
    AST visitor that detects destructive operations that collapse physical information.

    Config options:
        check_variance_context: bool - Suppress mean/sum warning if std/var is
            computed on same data nearby (default: True)
    """

    # Context window: variance computed within this many lines suppresses warning
    VARIANCE_CONTEXT_LINES = 10

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.mirages: List[Dict[str, Any]] = []
        self.current_function: Optional[str] = None
        self.config = config or {}
        self.check_variance_context = self.config.get("check_variance_context", True)

        # Will be populated by pre-pass if variance context checking enabled
        self.variance_contexts: Dict[Tuple[Optional[str], Optional[str]], Set[int]] = {}

    def analyze(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Analyze an AST tree with optional variance context awareness.

        This performs a two-pass analysis when check_variance_context is enabled:
        1. First pass: collect all variance operations (std, var)
        2. Second pass: detect mirages, suppressing those with variance context
        """
        if self.check_variance_context:
            # First pass: collect variance contexts
            collector = VarianceContextCollector()
            collector.visit(tree)
            self.variance_contexts = collector.variance_contexts

        # Second pass: detect mirages
        self.visit(tree)
        return self.mirages

    def _has_variance_context(self, var_name: Optional[str], line: int) -> bool:
        """
        Check if variance is computed on the same variable nearby.

        Returns True if std/var is called on the same variable within
        VARIANCE_CONTEXT_LINES lines, in the same function scope.
        """
        if not self.check_variance_context or not var_name:
            return False

        key = (var_name, self.current_function)
        if key not in self.variance_contexts:
            return False

        # Check if any variance operation is within the context window
        for variance_line in self.variance_contexts[key]:
            if abs(variance_line - line) <= self.VARIANCE_CONTEXT_LINES:
                return True

        return False

    def visit_Call(self, node: ast.Call) -> None:
        """Detect destructive numpy operations"""
        if isinstance(node.func, ast.Attribute):
            # Detect np.mean(), np.sum(), etc.
            if isinstance(node.func.value, ast.Name) and node.func.value.id in ["np", "numpy"]:
                if node.func.attr in ["mean", "sum", "argmax", "argmin"]:
                    # Get the variable being operated on
                    var_name = None
                    if node.args and isinstance(node.args[0], ast.Name):
                        var_name = node.args[0].id

                    # Skip if variance is computed on same data nearby (for mean/sum only)
                    if node.func.attr in ["mean", "sum"]:
                        if self._has_variance_context(var_name, node.lineno):
                            self.generic_visit(node)
                            return  # Suppress warning - variance is tracked

                    self.mirages.append(
                        {
                            "type": node.func.attr,
                            "node": node,
                            "line": node.lineno,
                            "col": node.col_offset,
                            "function": self.current_function,
                            "variable": var_name,
                        }
                    )

        # Check for premature discretization
        if isinstance(node.func, ast.Name) and node.func.id in ["round", "int"]:
            if len(node.args) > 0 and self._is_array_like(node.args[0]):
                self.mirages.append(
                    {
                        "type": "premature_discretization",
                        "node": node,
                        "line": node.lineno,
                        "col": node.col_offset,
                        "function": self.current_function,
                    }
                )

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
