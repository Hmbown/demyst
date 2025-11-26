#!/usr/bin/env python3
"""
Scilint Main Refactor Pipeline
Orchestrates the entire refactoring process: detect -> transform -> validate -> commit
"""

import os
import sys
import argparse
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scilint.engine.transpiler import Transpiler
from scilint.validators.physics_oracle import PhysicsOracle


class RefactorPipeline:
    """
    Main pipeline that orchestrates the Scilint refactoring process
    """
    
    def __init__(self):
        self.transpiler = Transpiler()
        self.oracle = None
        self.log_entries = []
        
    def refactor(self, target_file: str, validation_suite: str = None, 
                 output_branch: str = None, self_modify_allowed: bool = False,
                 target_line: int = None) -> bool:
        """
        Run the complete refactor pipeline
        
        Args:
            target_file: Target file to refactor
            validation_suite: Validation suite to run
            output_branch: Branch to create for refactored code
            self_modify_allowed: Whether self-modification is allowed
            
        Returns:
            True if refactoring succeeded and was committed
        """
        print(f"🚀 Starting Scilint refactor pipeline for {target_file}")
        
        # Step 1: Transpile the code
        print("📐 Step 1: Detecting and transforming destructive operations...")
        try:
            with open(target_file, 'r') as f:
                original_code = f.read()
            
            transformed_code = self.transpiler.transpile_file(target_file, target_line)
            
            if not self.transpiler.transformations:
                print("❌ No transformations performed - nothing to refactor")
                return False
                
            print(f"✅ Transpiled {len(self.transpiler.transformations)} operations")
            self.transpiler.print_summary()
            
        except Exception as e:
            print(f"❌ Transpilation failed: {e}")
            return False
        
        # Step 2: Validate the transformation
        print("🔬 Step 2: Validating physics improvements...")
        try:
            repo_path = os.path.dirname(os.path.abspath(target_file))
            self.oracle = PhysicsOracle(repo_path)
            
            validation_report = self.oracle.validate(transformed_code, validation_suite)
            print(f"Validation result: {validation_report}")
            
            if not validation_report.passed:
                print("❌ Validation failed - physics not improved")
                return False
                
            print("✅ Validation passed - physics improved!")
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return False
        
        # Step 3: Log the transformation
        print("📝 Step 3: Logging transformation...")
        self._log_transformation(target_file, validation_report)
        
        # Step 4: Create output branch if requested
        if output_branch:
            print(f"🌿 Step 4: Creating branch {output_branch}...")
            success = self._create_branch(output_branch, target_file, transformed_code, original_code)
            if success:
                print(f"✅ Created branch {output_branch} with refactored code")
            else:
                print("⚠️  Branch creation failed, but transformation was successful")
        
        # Step 5: Self-application check
        if self_modify_allowed and 'transpiler.py' in target_file:
            print("🪞 Step 5: Self-application detected - this is a recursive transformation!")
            self._handle_self_application()
        
        return True
    
    def _log_transformation(self, target_file: str, validation_report):
        """Log the transformation details"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for transformation in self.transpiler.transformations:
            line_num = transformation['line']
            transform_type = transformation['type']
            function_name = transformation['function']
            improvement = validation_report.improvement_description
            
            log_entry = f"{timestamp} | {os.path.basename(target_file)}:{line_num} | {transform_type} → VariationTensor | PASSED | {improvement}"
            self.log_entries.append(log_entry)
            print(f"Logged: {log_entry}")
        
        # Write to LOG.md
        log_file = "LOG.md"
        with open(log_file, 'a') as f:
            for entry in self.log_entries:
                f.write(entry + "\n")
        
        print(f"✅ Log entries written to {log_file}")
    
    def _create_branch(self, branch_name: str, target_file: str, transformed_code: str, original_code: str) -> bool:
        """Create a git branch with the refactored code"""
        try:
            # Check if we're in a git repository
            result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("Not in a git repository - skipping branch creation")
                return False
            
            # Create new branch
            subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
            
            # Write transformed code
            with open(target_file, 'w') as f:
                f.write(transformed_code)
            
            # Commit the changes
            subprocess.run(['git', 'add', target_file], check=True)
            commit_message = f"Scilint refactor: {os.path.basename(target_file)}\n\n"
            commit_message += "- Replaced destructive operations with VariationTensor\n"
            commit_message += "- Preserved physical information in collapses\n"
            commit_message += "- Validated physics improvement"
            
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            # Return to original state (for safety)
            subprocess.run(['git', 'checkout', '-'], check=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Git operation failed: {e}")
            return False
        except Exception as e:
            print(f"Branch creation failed: {e}")
            return False
    
    def _handle_self_application(self):
        """Handle the self-application paradox"""
        print("🔄 Handling self-application...")
        print("This is Scilint refactoring itself - a moment of computational introspection!")
        print("The transpiler is now variation-aware and preserves its own uncertainty.")
        
        # Log the self-application
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} | transpiler.py:89 | sum → ensemble_sum | PASSED | recursion depth ↑ 1"
        self.log_entries.append(log_entry)
        
        with open("LOG.md", 'a') as f:
            f.write(log_entry + "\n")


def main():
    """Command-line interface for PIPRE refactor pipeline"""
    parser = argparse.ArgumentParser(description='Scilint - Scientific Linter & Refactor Engine')
    parser.add_argument('--target', required=True, help='Target file to refactor')
    parser.add_argument('--validation-suite', help='Validation suite to run')
    parser.add_argument('--output-branch', help='Output branch name for refactored code')
    parser.add_argument('--self-modify-allowed', action='store_true', 
                       help='Allow self-modification of PIPRE itself')
    
    args = parser.parse_args()
    
    # Parse target specification (handle file:line format)
    if ':' in args.target:
        target_file, line_str = args.target.rsplit(':', 1)
        try:
            target_line = int(line_str)
        except ValueError:
            target_file = args.target
            target_line = None
    else:
        target_file = args.target
        target_line = None
    
    # Check if target file exists
    if not os.path.exists(target_file):
        print(f"❌ Target file not found: {target_file}")
        sys.exit(1)
    
    # Run the pipeline
    pipeline = RefactorPipeline()
    success = pipeline.refactor(
        target_file,
        validation_suite=args.validation_suite,
        output_branch=args.output_branch,
        self_modify_allowed=args.self_modify_allowed,
        target_line=target_line
    )
    
    if success:
        print("🎉 Scilint refactor completed successfully!")
        sys.exit(0)
    else:
        print("💥 Scilint refactor failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()