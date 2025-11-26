#!/usr/bin/env python3
"""
PIPRE Transpiler - Automatically refactors scientific code to preserve physical information
"""

import ast
import inspect
import sys
import os
from typing import Dict, List, Optional, Tuple, Any
import difflib
import argparse

# Import refactored components
from scilint.engine.mirage_detector import MirageDetector
from scilint.engine.variation_transformer import VariationTransformer
from scilint.engine.variation_tensor import VariationTensor


class Transpiler:
    """
    Main transpiler class that orchestrates the transformation process
    """
    
    def __init__(self):
        self.detector = MirageDetector()
        self.transformations = []
        
    def transpile_file(self, file_path: str, target_line: Optional[int] = None) -> str:
        """
        Transpile a Python file to preserve physical information
        
        Args:
            file_path: Path to the Python file
            target_line: Optional specific line to target
            
        Returns:
            Transformed source code
        """
        with open(file_path, 'r') as f:
            source = f.read()
        
        return self.transpile_source(source, target_line)
    
    def transpile_source(self, source: str, target_line: Optional[int] = None) -> str:
        """
        Transpile Python source code to preserve physical information
        
        Args:
            source: Python source code
            target_line: Optional specific line to target
            
        Returns:
            Transformed source code
        """
        # Parse AST
        tree = ast.parse(source)
        
        # Detect mirages
        self.detector.visit(tree)
        
        # Filter by target line if specified
        mirages = self.detector.mirages
        if target_line is not None:
            mirages = [m for m in mirages if m['line'] == target_line]
        
        if not mirages:
            print(f"No destructive operations found{' at line ' + str(target_line) if target_line else ''}")
            return source
        
        # Transform AST
        transformer = VariationTransformer(mirages)
        new_tree = transformer.visit(tree)
        
        # Fix line numbers and column offsets
        ast.fix_missing_locations(new_tree)
        
        # Generate new source
        new_source = ast.unparse(new_tree)
        
        # Store transformation info
        self.transformations = [{
            'type': m['type'],
            'line': m['line'],
            'function': m['function'],
            'transformation': f"{m['type']} -> VariationTensor"
        } for m in mirages]
        
        return new_source
    
    def get_diff(self, original: str, transformed: str) -> str:
        """Generate unified diff between original and transformed code"""
        original_lines = original.splitlines(keepends=True)
        transformed_lines = transformed.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines,
            transformed_lines,
            fromfile='original',
            tofile='transformed',
            lineterm=''
        )
        
        return ''.join(diff)
    
    def print_summary(self):
        """Print summary of transformations"""
        if not self.transformations:
            print("No transformations performed")
            return
            
        print("\n=== Scilint Transpiler Summary ===")
        for t in self.transformations:
            print(f"Line {t['line']} in {t['function']}: {t['transformation']}")
        print(f"Total transformations: {len(self.transformations)}")


def main():
    """Command-line interface for the transpiler"""
    parser = argparse.ArgumentParser(description='PIPRE Transpiler - Preserve physical information in scientific code')
    parser.add_argument('--target', required=True, help='Target file or file:line specification')
    parser.add_argument('--output', help='Output file (default: stdout)')
    parser.add_argument('--diff', action='store_true', help='Show unified diff')
    
    args = parser.parse_args()
    
    # Parse target specification
    if ':' in args.target:
        file_path, line_str = args.target.rsplit(':', 1)
        try:
            target_line = int(line_str)
        except ValueError:
            print(f"Invalid line number: {line_str}")
            sys.exit(1)
    else:
        file_path = args.target
        target_line = None
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
    
    # Run transpiler
    transpiler = Transpiler()
    
    try:
        with open(file_path, 'r') as f:
            original_source = f.read()
        
        transformed_source = transpiler.transpile_file(file_path, target_line)
        
        if args.diff:
            diff = transpiler.get_diff(original_source, transformed_source)
            print(diff)
        else:
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(transformed_source)
                print(f"Transformed source written to {args.output}")
            else:
                print(transformed_source)
        
        transpiler.print_summary()
        
    except Exception as e:
        print(f"Transpilation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()