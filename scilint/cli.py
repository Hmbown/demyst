#!/usr/bin/env python3
"""
Scilint CLI: The Scientific Integrity Platform

A comprehensive tool for detecting and preventing scientific integrity issues
in machine learning and data science code.

Usage:
    scilint analyze <path>          # Run all integrity checks
    scilint mirage <path>           # Detect computational mirages
    scilint leakage <path>          # Detect data leakage
    scilint hypothesis <path>       # Check statistical validity
    scilint units <path>            # Check dimensional consistency
    scilint tensor <path>           # Check deep learning integrity
    scilint report <path>           # Generate full integrity report
    scilint paper <path>            # Generate LaTeX methodology
    scilint ci <path>               # CI/CD enforcement mode
"""

import argparse
import sys
import os
import json
from pathlib import Path
from typing import Optional, List

# Version
__version__ = "1.0.0"


def analyze_command(args):
    """Run comprehensive analysis on a file or directory."""
    from scilint.integrations.ci_enforcer import CIEnforcer

    enforcer = CIEnforcer()

    if os.path.isdir(args.path):
        report = enforcer.analyze_directory(args.path)
    else:
        result = enforcer.analyze_file(args.path)
        # Convert single file result to report format
        print(json.dumps(result, indent=2, default=str))
        return 0 if not any(
            result.get(k, {}).get('issues', [])
            for k in ['mirage', 'leakage', 'hypothesis', 'unit', 'tensor']
        ) else 1

    if args.format == 'markdown':
        print(report.to_markdown())
    elif args.format == 'json':
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.to_markdown())

    return 0 if report.badge_status == 'passing' else 1


def mirage_command(args):
    """Detect computational mirages (variance-destroying operations)."""
    from scilint.engine.mirage_detector import MirageDetector
    import ast

    with open(args.path, 'r') as f:
        source = f.read()

    tree = ast.parse(source)
    detector = MirageDetector()
    detector.visit(tree)

    if not detector.mirages:
        print("No computational mirages detected.")
        return 0

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
    return 1 if detector.mirages else 0


def leakage_command(args):
    """Detect data leakage issues."""
    from scilint.guards.leakage_hunter import LeakageHunter

    with open(args.path, 'r') as f:
        source = f.read()

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


def hypothesis_command(args):
    """Check statistical validity (anti-p-hacking)."""
    from scilint.guards.hypothesis_guard import HypothesisGuard

    with open(args.path, 'r') as f:
        source = f.read()

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


def units_command(args):
    """Check dimensional consistency."""
    from scilint.guards.unit_guard import UnitGuard

    with open(args.path, 'r') as f:
        source = f.read()

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


def tensor_command(args):
    """Check deep learning integrity."""
    from scilint.guards.tensor_guard import TensorGuard

    with open(args.path, 'r') as f:
        source = f.read()

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


def report_command(args):
    """Generate a full scientific integrity report."""
    from scilint.generators.report_generator import IntegrityReportGenerator
    from scilint.integrations.ci_enforcer import CIEnforcer

    enforcer = CIEnforcer()

    if os.path.isdir(args.path):
        report = enforcer.analyze_directory(args.path)
    else:
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

    if args.format == 'html':
        # For directory, we'd need to extend the report
        print(report.to_markdown())  # Fallback to markdown
    elif args.format == 'json':
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.to_markdown())

    return 0 if report.badge_status == 'passing' else 1


def paper_command(args):
    """Generate LaTeX methodology section from code."""
    from scilint.generators.paper_generator import PaperGenerator

    with open(args.path, 'r') as f:
        source = f.read()

    generator = PaperGenerator(style=args.style)

    if args.full:
        latex = generator.generate_full_paper_template(source)
    else:
        latex = generator.generate(source, title=args.title)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(latex)
        print(f"LaTeX written to {args.output}")
    else:
        print(latex)

    return 0


def ci_command(args):
    """Run in CI/CD enforcement mode."""
    from scilint.integrations.ci_enforcer import CIEnforcer

    enforcer = CIEnforcer()
    exit_code = enforcer.enforce(
        directory=args.path,
        fail_on_warning=args.strict
    )

    return exit_code


def version_command(args):
    """Print version information."""
    print(f"Scilint v{__version__}")
    print("The Scientific Integrity Platform")
    print("\nComponents:")
    print("  - MirageDetector: Computational mirage detection")
    print("  - TensorGuard: Deep learning integrity")
    print("  - LeakageHunter: Data leakage detection")
    print("  - HypothesisGuard: Statistical validity")
    print("  - UnitGuard: Dimensional analysis")
    print("  - PaperGenerator: LaTeX methodology")
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Scilint: The Scientific Integrity Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scilint analyze ./src           Run all integrity checks on a directory
  scilint mirage model.py         Detect computational mirages
  scilint leakage train.py        Check for data leakage
  scilint hypothesis stats.py     Validate statistical practices
  scilint units physics.py        Check dimensional consistency
  scilint tensor network.py       Check deep learning integrity
  scilint paper model.py -o methodology.tex  Generate LaTeX
  scilint ci . --strict           CI/CD mode with strict checking

For more information: https://github.com/scilint/scilint
        """
    )

    parser.add_argument('--version', '-v', action='store_true',
                       help='Show version information')

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Run all integrity checks')
    analyze_parser.add_argument('path', help='File or directory to analyze')
    analyze_parser.add_argument('--format', '-f', choices=['markdown', 'json', 'text'],
                               default='markdown', help='Output format')
    analyze_parser.set_defaults(func=analyze_command)

    # Mirage command
    mirage_parser = subparsers.add_parser('mirage', help='Detect computational mirages')
    mirage_parser.add_argument('path', help='File to analyze')
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
    ci_parser.set_defaults(func=ci_command)

    args = parser.parse_args()

    if args.version:
        return version_command(args)

    if args.command is None:
        parser.print_help()
        return 0

    try:
        return args.func(args)
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        if os.environ.get('SCILINT_DEBUG'):
            raise
        return 1


if __name__ == '__main__':
    sys.exit(main())
