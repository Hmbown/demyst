#!/usr/bin/env python3
"""
Demyst CLI: Demystify Your Scientific Code

A comprehensive tool for detecting and preventing scientific integrity issues
in machine learning and data science code.

Usage:
    demyst analyze <path>          # Run all integrity checks
    demyst mirage <path>           # Detect computational mirages
    demyst mirage <path> --fix     # Detect and auto-fix mirages
    demyst leakage <path>          # Detect data leakage
    demyst hypothesis <path>       # Check statistical validity
    demyst units <path>            # Check dimensional consistency
    demyst tensor <path>           # Check deep learning integrity
    demyst report <path>           # Generate full integrity report
    demyst paper <path>            # Generate LaTeX methodology
    demyst ci <path>               # CI/CD enforcement mode
    demyst fix <path>              # Auto-fix issues
"""

import argparse
import sys
import os
import json
import logging
from pathlib import Path
from typing import Optional, List, Any, Dict

# Version
__version__ = "1.0.0"

# Global logger
logger = logging.getLogger("demyst")


def setup_logging(verbose: bool = False, debug: bool = False) -> None:
    """Configure logging based on verbosity settings."""
    if debug:
        level = logging.DEBUG
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    elif verbose:
        level = logging.INFO
        fmt = "%(levelname)s: %(message)s"
    else:
        level = logging.WARNING
        fmt = "%(message)s"

    logging.basicConfig(level=level, format=fmt)
    logger.setLevel(level)


def safe_read_file(path: str) -> str:
    """Safely read a file with proper error handling."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with latin-1 as fallback
        logger.debug(f"UTF-8 decode failed for {path}, trying latin-1")
        with open(path, 'r', encoding='latin-1') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except PermissionError:
        raise PermissionError(f"Permission denied: {path}")
    except IsADirectoryError:
        raise IsADirectoryError(f"Expected a file, got a directory: {path}")


def analyze_command(args: argparse.Namespace) -> int:
    """Run comprehensive analysis on a file or directory."""
    from demyst.integrations.ci_enforcer import CIEnforcer

    logger.info(f"Analyzing {args.path}")

    # Load configuration
    config: Dict[str, Any] = {}
    if args.config:
        try:
            import yaml
            with open(args.config, 'r') as f:
                config = yaml.safe_load(f) or {}
            logger.debug(f"Loaded config from {args.config}")
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")

    enforcer = CIEnforcer(config=config)

    if os.path.isdir(args.path):
        report = enforcer.analyze_directory(args.path)
        if args.format == 'markdown':
            print(report.to_markdown())
        elif args.format == 'json':
            print(json.dumps(report.to_dict(), indent=2))
        else:
            print(report.to_markdown())
        return 0 if report.badge_status == 'passing' else 1
    else:
        result = enforcer.analyze_file(args.path)
        if args.format == 'json':
            print(json.dumps(result, indent=2, default=str))
        else:
            # Text/markdown format for single file
            print(json.dumps(result, indent=2, default=str))

        has_issues = any(
            result.get(k, {}).get('issues', [])
            for k in ['mirage', 'leakage', 'hypothesis', 'unit', 'tensor']
        )
        return 1 if has_issues else 0


def mirage_command(args: argparse.Namespace) -> int:
    """Detect computational mirages (variance-destroying operations)."""
    from demyst.engine.mirage_detector import MirageDetector
    import ast

    logger.info(f"Detecting mirages in {args.path}")

    try:
        source = safe_read_file(args.path)
    except Exception as e:
        print(f"Error: {e}")
        return 1

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"Syntax error in {args.path}: {e}")
        return 1

    detector = MirageDetector()
    detector.visit(tree)

    if not detector.mirages:
        print("No computational mirages detected.")
        return 0

    # If --fix flag is set, use the transpiler to auto-fix
    if getattr(args, 'fix', False):
        return _apply_mirage_fix(args.path, source, detector.mirages, args)

    # Just report the mirages
    print(f"\n{'='*60}")
    print("COMPUTATIONAL MIRAGES DETECTED")
    print(f"{'='*60}\n")

    for m in detector.mirages:
        print(f"Line {m['line']}: {m['type']}()")
        print(f"  Function: {m['function'] or 'module level'}")
        print(f"  Impact: Destroys variance/distribution information")
        print(f"  Fix: Use VariationTensor({m['type']}).collapse('{m['type']}')")
        print()

    print(f"Total mirages: {len(detector.mirages)}")

    if hasattr(args, 'fix'):
        print("\nTip: Use --fix to automatically transform these operations")

    return 1


def _apply_mirage_fix(path: str, source: str, mirages: List[Dict], args: argparse.Namespace) -> int:
    """Apply transpiler fixes to mirages."""
    from demyst.engine.transpiler import Transpiler

    logger.info(f"Applying auto-fix to {path}")

    transpiler = Transpiler()

    try:
        transformed = transpiler.transpile_source(source)
    except Exception as e:
        print(f"Error during transformation: {e}")
        logger.debug("Transformation error", exc_info=True)
        return 1

    if not transpiler.transformations:
        print("No transformations applied.")
        return 0

    # Show diff if requested
    if getattr(args, 'diff', False) or getattr(args, 'dry_run', False):
        diff = transpiler.get_diff(source, transformed)
        print("Proposed changes:")
        print(diff)

        if getattr(args, 'dry_run', False):
            print("\n[DRY RUN] No changes written to disk.")
            return 0

    # Write the transformed code
    if getattr(args, 'output', None):
        output_path = args.output
    else:
        output_path = path

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(transformed)
        print(f"\nTransformed code written to {output_path}")
        transpiler.print_summary()
        return 0
    except Exception as e:
        print(f"Error writing file: {e}")
        return 1


def leakage_command(args: argparse.Namespace) -> int:
    """Detect data leakage issues."""
    from demyst.guards.leakage_hunter import LeakageHunter

    logger.info(f"Detecting data leakage in {args.path}")

    try:
        source = safe_read_file(args.path)
    except Exception as e:
        print(f"Error: {e}")
        return 1

    hunter = LeakageHunter()
    result = hunter.analyze(source)

    if result.get('error'):
        print(f"Error: {result['error']}")
        return 1

    violations = result.get('violations', [])

    if not violations:
        print("No data leakage detected.")
        return 0

    print(f"\n{'='*60}")
    print("DATA LEAKAGE DETECTED")
    print(f"{'='*60}\n")

    for v in violations:
        severity_icon = "CRITICAL" if v['severity'] == 'critical' else "WARNING"
        print(f"[{severity_icon}] Line {v['line']}: {v['type']}")
        print(f"  {v['description']}")
        print(f"  Impact: {v['scientific_impact']}")
        print(f"  Fix: {v['recommendation']}")
        print()

    summary = result.get('summary', {})
    print(f"Verdict: {summary.get('verdict', 'Unknown')}")

    return 1 if any(v['severity'] == 'critical' for v in violations) else 0


def hypothesis_command(args: argparse.Namespace) -> int:
    """Check statistical validity (anti-p-hacking)."""
    from demyst.guards.hypothesis_guard import HypothesisGuard

    logger.info(f"Checking statistical validity in {args.path}")

    try:
        source = safe_read_file(args.path)
    except Exception as e:
        print(f"Error: {e}")
        return 1

    guard = HypothesisGuard()
    result = guard.analyze_code(source)

    if result.get('error'):
        print(f"Error: {result['error']}")
        return 1

    violations = result.get('violations', [])

    if not violations:
        print("No statistical validity issues detected.")
        if result.get('correction_info'):
            info = result['correction_info']
            print(f"\nNote: {info['recommendation']}")
        return 0

    print(f"\n{'='*60}")
    print("STATISTICAL VALIDITY ISSUES")
    print(f"{'='*60}\n")

    for v in violations:
        print(f"Line {v['line']}: {v['type']}")
        print(f"  {v['description']}")
        print(f"  Impact: {v['statistical_impact']}")
        print(f"  Correct interpretation: {v['corrected_interpretation']}")
        print(f"  Fix: {v['recommendation']}")
        print()

    if result.get('correction_info'):
        info = result['correction_info']
        print(f"\nMultiple Comparisons Correction:")
        print(f"  Tests detected: {info['num_tests_detected']}")
        print(f"  Corrected alpha: {info['bonferroni_alpha']:.4f}")

    summary = result.get('summary', {})
    print(f"\nVerdict: {summary.get('verdict', 'Unknown')}")

    return 1 if any(v['severity'] == 'invalid' for v in violations) else 0


def units_command(args: argparse.Namespace) -> int:
    """Check dimensional consistency."""
    from demyst.guards.unit_guard import UnitGuard

    logger.info(f"Checking dimensional consistency in {args.path}")

    try:
        source = safe_read_file(args.path)
    except Exception as e:
        print(f"Error: {e}")
        return 1

    guard = UnitGuard()
    result = guard.analyze(source)

    if result.get('error'):
        print(f"Error: {result['error']}")
        return 1

    violations = result.get('violations', [])

    if not violations:
        print("No dimensional consistency issues detected.")
        if result.get('inferred_dimensions'):
            print("\nInferred dimensions:")
            for var, dim in result['inferred_dimensions'].items():
                print(f"  {var}: {dim}")
        return 0

    print(f"\n{'='*60}")
    print("DIMENSIONAL ANALYSIS ISSUES")
    print(f"{'='*60}\n")

    for v in violations:
        print(f"Line {v['line']}: {v['type']}")
        print(f"  Expression: {v['expression']}")
        if v.get('left_dimension') and v.get('right_dimension'):
            print(f"  Left: {v['left_dimension']}, Right: {v['right_dimension']}")
        print(f"  {v['description']}")
        print(f"  Physical meaning: {v['physical_meaning']}")
        print(f"  Fix: {v['recommendation']}")
        print()

    summary = result.get('summary', {})
    print(f"Verdict: {summary.get('verdict', 'Unknown')}")

    return 1 if any(v['severity'] == 'critical' for v in violations) else 0


def tensor_command(args: argparse.Namespace) -> int:
    """Check deep learning integrity."""
    from demyst.guards.tensor_guard import TensorGuard

    logger.info(f"Checking deep learning integrity in {args.path}")

    try:
        source = safe_read_file(args.path)
    except Exception as e:
        print(f"Error: {e}")
        return 1

    guard = TensorGuard()
    result = guard.analyze(source)

    if result.get('error'):
        print(f"Error: {result['error']}")
        return 1

    has_issues = False

    if result.get('gradient_issues'):
        has_issues = True
        print(f"\n{'='*60}")
        print("GRADIENT FLOW ISSUES")
        print(f"{'='*60}\n")

        for issue in result['gradient_issues']:
            print(f"Line {issue['line']}: {issue['type']}")
            print(f"  Severity: {issue['severity']}")
            print(f"  {issue['description']}")
            print(f"  Scientific impact: {issue['scientific_impact']}")
            print(f"  Fix: {issue['recommendation']}")
            print()

    if result.get('normalization_issues'):
        has_issues = True
        print(f"\n{'='*60}")
        print("NORMALIZATION ISSUES")
        print(f"{'='*60}\n")

        for issue in result['normalization_issues']:
            print(f"Line {issue['line']}: {issue['type']}")
            print(f"  Layer: {issue['layer']}")
            print(f"  {issue['description']}")
            print(f"  Masked statistics: {', '.join(issue['masked_statistics'])}")
            print(f"  Fix: {issue['recommendation']}")
            print()

    if result.get('reward_issues'):
        has_issues = True
        print(f"\n{'='*60}")
        print("REWARD HACKING VULNERABILITIES")
        print(f"{'='*60}\n")

        for issue in result['reward_issues']:
            print(f"Line {issue['line']}: {issue['type']}")
            print(f"  Function: {issue['function']}")
            print(f"  {issue['description']}")
            print(f"  Exploit vector: {issue['exploit_vector']}")
            print(f"  Fix: {issue['recommendation']}")
            print()

    if not has_issues:
        print("No deep learning integrity issues detected.")
        return 0

    summary = result.get('summary', {})
    print(f"\nVerdict: {summary.get('verdict', 'Unknown')}")

    return 1 if summary.get('critical_issues', 0) > 0 else 0


def report_command(args: argparse.Namespace) -> int:
    """Generate a full scientific integrity report."""
    from demyst.generators.report_generator import IntegrityReportGenerator
    from demyst.integrations.ci_enforcer import CIEnforcer

    logger.info(f"Generating report for {args.path}")

    enforcer = CIEnforcer()

    if os.path.isdir(args.path):
        report = enforcer.analyze_directory(args.path)
        if args.format == 'html':
            print(report.to_markdown())  # Fallback to markdown for directory
        elif args.format == 'json':
            print(json.dumps(report.to_dict(), indent=2))
        else:
            print(report.to_markdown())
        return 0 if report.badge_status == 'passing' else 1

    # Single file - run all checks
    result = enforcer.analyze_file(args.path)

    generator = IntegrityReportGenerator(f"Integrity Report: {args.path}")

    # Add sections from results
    if result.get('mirage') and not result['mirage'].get('error'):
        issues = result['mirage'].get('issues', [])
        generator.add_section(
            "Computational Mirages",
            'fail' if issues else 'pass',
            f"Found {len(issues)} variance-destroying operations",
            issues,
            ["Use VariationTensor to preserve statistical metadata"] if issues else []
        )

    if args.format == 'html':
        print(generator.to_html())
    elif args.format == 'json':
        print(generator.to_json())
    else:
        print(generator.to_markdown())

    return 0


def paper_command(args: argparse.Namespace) -> int:
    """Generate LaTeX methodology section from code."""
    from demyst.generators.paper_generator import PaperGenerator

    logger.info(f"Generating LaTeX for {args.path}")

    try:
        source = safe_read_file(args.path)
    except Exception as e:
        print(f"Error: {e}")
        return 1

    generator = PaperGenerator(style=args.style)

    if args.full:
        latex = generator.generate_full_paper_template(source)
    else:
        latex = generator.generate(source, title=args.title)

    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(latex)
            print(f"LaTeX written to {args.output}")
        except Exception as e:
            print(f"Error writing file: {e}")
            return 1
    else:
        print(latex)

    return 0


def ci_command(args: argparse.Namespace) -> int:
    """Run in CI/CD enforcement mode."""
    from demyst.integrations.ci_enforcer import CIEnforcer

    logger.info(f"Running CI enforcement on {args.path}")

    # Load configuration
    config: Dict[str, Any] = {}
    if args.config:
        try:
            import yaml
            with open(args.config, 'r') as f:
                config = yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")

    enforcer = CIEnforcer(config=config)
    exit_code = enforcer.enforce(
        directory=args.path,
        fail_on_warning=args.strict
    )

    return exit_code


def fix_command(args: argparse.Namespace) -> int:
    """Auto-fix command for all detected issues."""
    from demyst.integrations.ci_enforcer import CIEnforcer
    from demyst.fixer import DemystFixer

    logger.info(f"Running auto-fix on {args.path}")
    print(f"Running auto-fix on {args.path}...")

    # First analyze to find issues
    enforcer = CIEnforcer()

    if os.path.isdir(args.path):
        report = enforcer.analyze_directory(args.path)
        fixer = DemystFixer(dry_run=args.dry_run, interactive=args.interactive)

        # For now, show message about directory fix being in beta
        print("Directory auto-fix is currently in beta.")
        if args.dry_run:
            print("[DRY RUN] Would process files in directory.")
        return 0
    else:
        result = enforcer.analyze_file(args.path)
        fixer = DemystFixer(dry_run=args.dry_run, interactive=args.interactive)

        # Collect all violations
        violations = []
        if result.get('mirage') and not result['mirage'].get('error'):
            violations.extend(result['mirage'].get('issues', []))

        if not violations:
            print("No issues found to fix.")
            return 0

        fixer.fix_file(args.path, violations)

    return 0


def version_command(args: argparse.Namespace) -> int:
    """Print version information."""
    print(f"Demyst v{__version__}")
    print("Demystify Your Scientific Code")
    print("\nComponents:")
    print("  - MirageDetector: Computational mirage detection")
    print("  - TensorGuard: Deep learning integrity")
    print("  - LeakageHunter: Data leakage detection")
    print("  - HypothesisGuard: Statistical validity")
    print("  - UnitGuard: Dimensional analysis")
    print("  - PaperGenerator: LaTeX methodology")
    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Demyst: The Scientific Integrity Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  demyst analyze ./src           Run all integrity checks on a directory
  demyst mirage model.py         Detect computational mirages
  demyst mirage model.py --fix   Detect and auto-fix mirages
  demyst leakage train.py        Check for data leakage
  demyst hypothesis stats.py     Validate statistical practices
  demyst units physics.py        Check dimensional consistency
  demyst tensor network.py       Check deep learning integrity
  demyst paper model.py -o methodology.tex  Generate LaTeX
  demyst ci . --strict           CI/CD mode with strict checking

For more information: https://github.com/demyst/demyst
        """
    )

    parser.add_argument('--version', '-v', action='store_true',
                       help='Show version information')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output (implies --verbose)')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run all integrity checks')
    analyze_parser.add_argument('path', help='File or directory to analyze')
    analyze_parser.add_argument('--format', '-f', choices=['markdown', 'json', 'text'],
                               default='markdown', help='Output format')
    analyze_parser.add_argument('--config', '-c', help='Path to configuration file')
    analyze_parser.set_defaults(func=analyze_command)

    # Mirage command
    mirage_parser = subparsers.add_parser('mirage', help='Detect computational mirages')
    mirage_parser.add_argument('path', help='File to analyze')
    mirage_parser.add_argument('--fix', action='store_true',
                              help='Auto-fix detected mirages using transpiler')
    mirage_parser.add_argument('--output', '-o', help='Output file for fixed code')
    mirage_parser.add_argument('--diff', action='store_true',
                              help='Show diff of changes')
    mirage_parser.add_argument('--dry-run', action='store_true',
                              help='Show what would be done without making changes')
    mirage_parser.set_defaults(func=mirage_command)

    # Leakage command
    leakage_parser = subparsers.add_parser('leakage', help='Detect data leakage')
    leakage_parser.add_argument('path', help='File to analyze')
    leakage_parser.set_defaults(func=leakage_command)

    # Hypothesis command
    hypothesis_parser = subparsers.add_parser('hypothesis', help='Check statistical validity')
    hypothesis_parser.add_argument('path', help='File to analyze')
    hypothesis_parser.set_defaults(func=hypothesis_command)

    # Units command
    units_parser = subparsers.add_parser('units', help='Check dimensional consistency')
    units_parser.add_argument('path', help='File to analyze')
    units_parser.set_defaults(func=units_command)

    # Tensor command
    tensor_parser = subparsers.add_parser('tensor', help='Check deep learning integrity')
    tensor_parser.add_argument('path', help='File to analyze')
    tensor_parser.set_defaults(func=tensor_command)

    # Report command
    report_parser = subparsers.add_parser('report', help='Generate integrity report')
    report_parser.add_argument('path', help='File or directory to analyze')
    report_parser.add_argument('--format', '-f', choices=['markdown', 'html', 'json'],
                              default='markdown', help='Output format')
    report_parser.set_defaults(func=report_command)

    # Paper command
    paper_parser = subparsers.add_parser('paper', help='Generate LaTeX methodology')
    paper_parser.add_argument('path', help='File to analyze')
    paper_parser.add_argument('--output', '-o', help='Output file')
    paper_parser.add_argument('--title', '-t', default='Methodology',
                             help='Section title')
    paper_parser.add_argument('--style', '-s', choices=['neurips', 'icml', 'iclr', 'arxiv'],
                             default='neurips', help='Paper style')
    paper_parser.add_argument('--full', action='store_true',
                             help='Generate full paper template')
    paper_parser.set_defaults(func=paper_command)

    # CI command
    ci_parser = subparsers.add_parser('ci', help='CI/CD enforcement mode')
    ci_parser.add_argument('path', nargs='?', default='.', help='Directory to analyze')
    ci_parser.add_argument('--strict', action='store_true',
                          help='Fail on warnings (not just critical issues)')
    ci_parser.add_argument('--config', '-c', help='Path to configuration file')
    ci_parser.set_defaults(func=ci_command)

    # Fix command
    fix_parser = subparsers.add_parser('fix', help='Auto-fix issues')
    fix_parser.add_argument('path', help='File or directory to fix')
    fix_parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    fix_parser.add_argument('--interactive', '-i', action='store_true', help='Ask before applying fix')
    fix_parser.set_defaults(func=fix_command)

    args = parser.parse_args()

    # Setup logging
    setup_logging(
        verbose=getattr(args, 'verbose', False),
        debug=getattr(args, 'debug', False) or os.environ.get('DEMYST_DEBUG')
    )

    if args.version:
        return version_command(args)

    if args.command is None:
        parser.print_help()
        return 0

    try:
        return args.func(args)
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        logger.debug("File not found error", exc_info=True)
        return 1
    except PermissionError as e:
        print(f"Error: Permission denied - {e}")
        logger.debug("Permission error", exc_info=True)
        return 1
    except SyntaxError as e:
        print(f"Error: Syntax error in file - {e}")
        logger.debug("Syntax error", exc_info=True)
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        if args.debug or os.environ.get('DEMYST_DEBUG'):
            logger.exception("Unexpected error")
        return 1


if __name__ == '__main__':
    sys.exit(main())
