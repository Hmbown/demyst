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
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from demyst.console import format_analysis_report, get_console


def _merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two configurations, with override taking precedence."""
    merged = base.copy()
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _merge_configs(merged[key], value)
        else:
            merged[key] = value
    return merged


# Version - use single source of truth from pyproject.toml
try:
    from importlib.metadata import version
    __version__ = version("demyst")
except Exception:
    __version__ = "1.2.0"  # Fallback for development

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
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with latin-1 as fallback
        logger.debug(f"UTF-8 decode failed for {path}, trying latin-1")
        with open(path, "r", encoding="latin-1") as f:
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

    console = get_console()
    logger.info(f"Analyzing {args.path}")

    # Load configuration
    config: Dict[str, Any] = {}
    if args.config:
        try:
            import yaml

            with open(args.config, "r") as f:
                config = yaml.safe_load(f) or {}
            logger.debug(f"Loaded config from {args.config}")
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")

    # Apply profile if specified (profile settings merge into config)
    if hasattr(args, "profile") and args.profile:
        try:
            import importlib

            profile_module = importlib.import_module(f"demyst.profiles.{args.profile}")
            profile_config = getattr(profile_module, "PROFILE", {})
            # Merge profile into config (profile provides defaults, config overrides)
            config = _merge_configs(profile_config, config)
            logger.info(f"Using {args.profile} profile")
        except ImportError:
            logger.warning(f"Profile '{args.profile}' not found")
        except Exception as e:
            logger.warning(f"Failed to load profile: {e}")

    enforcer = CIEnforcer(config=config)

    if os.path.isdir(args.path):
        with console.status(f"Analyzing directory {args.path}..."):
            report = enforcer.analyze_directory(args.path)

        if args.format == "markdown":
            print(report.to_markdown())
        elif args.format == "json":
            print(json.dumps(report.to_dict(), indent=2))
        else:
            # Use rich console for text output
            console.print_rule(f"Analysis Report: {args.path}")
            console.print_success(f"Analyzed {report.files_analyzed} files.")

            if report.total_issues > 0:
                console.print_warning(f"Found {report.total_issues} issues.")

                for check in report.checks:
                    if not check.passed:
                        console.print_rule(check.name)
                        for issue in check.issues:
                            # Reconstruct dict for print_violations
                            violation = {
                                "type": check.name,
                                "line": issue.get("line"),
                                "description": issue.get("description"),
                                "recommendation": None,
                            }
                            console.print_violations([violation], file_path=issue.get("file"))
            else:
                console.print_success("No issues detected!")

        return 0 if report.badge_status == "passing" else 1
    else:
        with console.status(f"Analyzing file {args.path}..."):
            result = enforcer.analyze_file(args.path)

        if result.get("error"):
            console.print_error(result["error"])
            return 1

        if args.format == "json":
            print(json.dumps(result, indent=2, default=str))
        elif args.format == "markdown":
            # Fallback to print for pure markdown if requested
            print(
                json.dumps(result, indent=2, default=str)
            )  # TODO: Implement markdown for single file
        else:
            # Rich text format
            format_analysis_report(result, file_path=args.path)

        has_issues = any(
            result.get(k, {}).get("issues", [])
            for k in ["mirage", "leakage", "hypothesis", "unit", "tensor"]
        )
        return 1 if has_issues else 0


def mirage_command(args: argparse.Namespace) -> int:
    """Detect computational mirages (variance-destroying operations)."""
    import ast

    from demyst.engine.mirage_detector import MirageDetector

    console = get_console()
    logger.info(f"Detecting mirages in {args.path}")

    try:
        source = safe_read_file(args.path)
    except Exception as e:
        console.print_error(str(e))
        return 1

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        console.print_error(f"Syntax error in {args.path}: {e}")
        return 1

    detector = MirageDetector()
    detector.visit(tree)

    if not detector.mirages:
        console.print_success("No computational mirages detected.")
        return 0

    # If --fix flag is set, use the transpiler to auto-fix
    if getattr(args, "fix", False):
        return _apply_mirage_fix(args.path, source, detector.mirages, args)

    # Report mirages
    console.print_rule("Computational Mirages Detected")

    violations = []
    for m in detector.mirages:
        violations.append(
            {
                "type": m["type"],
                "line": m["line"],
                "description": f"Computational mirage: {m['type']} operation destroys variance information. (Function: {m['function'] or 'module level'})",
                "recommendation": f"Use VariationTensor({m['type']}).collapse('{m['type']}')",
            }
        )

    console.print_violations(violations, file_path=args.path, source=source)
    console.print_warning(f"Total mirages: {len(detector.mirages)}")

    if not hasattr(args, "fix"):
        console.print_info("\nTip: Use --fix to automatically transform these operations")

    return 1


def _apply_mirage_fix(path: str, source: str, mirages: List[Dict], args: argparse.Namespace) -> int:
    """Apply transpiler fixes to mirages."""
    from demyst.engine.transpiler import Transpiler

    console = get_console()
    logger.info(f"Applying auto-fix to {path}")

    transpiler = Transpiler()

    try:
        transformed = transpiler.transpile_source(source)
    except Exception as e:
        console.print_error(f"Error during transformation: {e}")
        logger.debug("Transformation error", exc_info=True)
        return 1

    if not transpiler.transformations:
        console.print_info("No transformations applied.")
        return 0

    # Show diff if requested
    if getattr(args, "diff", False) or getattr(args, "dry_run", False):
        diff = transpiler.get_diff(source, transformed)
        console.print_diff(diff, title="Proposed changes")

        if getattr(args, "dry_run", False):
            console.print_warning("\n[DRY RUN] No changes written to disk.")
            return 0

    # Write the transformed code
    if getattr(args, "output", None):
        output_path = args.output
    else:
        output_path = path

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transformed)
        console.print_success(f"\nTransformed code written to {output_path}")
        # Summary could be printed here if needed
        return 0
    except Exception as e:
        console.print_error(f"Error writing file: {e}")
        return 1


def leakage_command(args: argparse.Namespace) -> int:
    """Detect data leakage issues."""
    from demyst.guards.leakage_hunter import LeakageHunter

    console = get_console()
    logger.info(f"Detecting data leakage in {args.path}")

    try:
        source = safe_read_file(args.path)
    except Exception as e:
        console.print_error(str(e))
        return 1

    hunter = LeakageHunter()
    result = hunter.analyze(source)

    if result.get("error"):
        console.print_error(result["error"])
        return 1

    violations = result.get("violations", [])

    if not violations:
        console.print_success("No data leakage detected.")
        return 0

    console.print_rule("Data Leakage Detected")
    console.print_violations(violations, file_path=args.path, source=source)

    summary = result.get("summary", {})
    console.print_warning(f"Verdict: {summary.get('verdict', 'Unknown')}")

    return 1 if any(v["severity"] == "critical" for v in violations) else 0


def hypothesis_command(args: argparse.Namespace) -> int:
    """Check statistical validity (anti-p-hacking)."""
    from demyst.guards.hypothesis_guard import HypothesisGuard

    console = get_console()
    logger.info(f"Checking statistical validity in {args.path}")

    try:
        source = safe_read_file(args.path)
    except Exception as e:
        console.print_error(str(e))
        return 1

    guard = HypothesisGuard()
    result = guard.analyze_code(source)

    if result.get("error"):
        console.print_error(result["error"])
        return 1

    violations = result.get("violations", [])

    if not violations:
        console.print_success("No statistical validity issues detected.")
        if result.get("correction_info"):
            info = result["correction_info"]
            console.print_info(f"\nNote: {info['recommendation']}")
        return 0

    console.print_rule("Statistical Validity Issues")
    console.print_violations(violations, file_path=args.path, source=source)

    if result.get("correction_info"):
        info = result["correction_info"]
        console.print_info("\nMultiple Comparisons Correction:")
        console.print_info(f"  Tests detected: {info['num_tests_detected']}")
        console.print_info(f"  Corrected alpha: {info['bonferroni_alpha']:.4f}")

    summary = result.get("summary", {})
    console.print_warning(f"\nVerdict: {summary.get('verdict', 'Unknown')}")

    return 1 if any(v["severity"] == "invalid" for v in violations) else 0


def units_command(args: argparse.Namespace) -> int:
    """Check dimensional consistency."""
    from demyst.guards.unit_guard import UnitGuard

    console = get_console()
    logger.info(f"Checking dimensional consistency in {args.path}")

    try:
        source = safe_read_file(args.path)
    except Exception as e:
        console.print_error(str(e))
        return 1

    guard = UnitGuard()
    result = guard.analyze(source)

    if result.get("error"):
        console.print_error(result["error"])
        return 1

    violations = result.get("violations", [])

    if not violations:
        console.print_success("No dimensional consistency issues detected.")
        if result.get("inferred_dimensions"):
            console.print_info("\nInferred dimensions:")
            for var, dim in result["inferred_dimensions"].items():
                console.print_info(f"  {var}: {dim}")
        return 0

    console.print_rule("Dimensional Analysis Issues")
    console.print_violations(violations, file_path=args.path, source=source)

    summary = result.get("summary", {})
    console.print_warning(f"Verdict: {summary.get('verdict', 'Unknown')}")

    return 1 if any(v["severity"] == "critical" for v in violations) else 0


def tensor_command(args: argparse.Namespace) -> int:
    """Check deep learning integrity."""
    from demyst.guards.tensor_guard import TensorGuard

    console = get_console()
    logger.info(f"Checking deep learning integrity in {args.path}")

    try:
        source = safe_read_file(args.path)
    except Exception as e:
        console.print_error(str(e))
        return 1

    guard = TensorGuard()
    result = guard.analyze(source)

    if result.get("error"):
        console.print_error(result["error"])
        return 1

    has_issues = False

    if result.get("gradient_issues"):
        has_issues = True
        console.print_rule("Gradient Flow Issues")
        console.print_violations(result["gradient_issues"], file_path=args.path, source=source)

    if result.get("normalization_issues"):
        has_issues = True
        console.print_rule("Normalization Issues")
        console.print_violations(result["normalization_issues"], file_path=args.path, source=source)

    if result.get("reward_issues"):
        has_issues = True
        console.print_rule("Reward Hacking Vulnerabilities")
        console.print_violations(result["reward_issues"], file_path=args.path, source=source)

    if not has_issues:
        console.print_success("No deep learning integrity issues detected.")
        return 0

    summary = result.get("summary", {})
    console.print_warning(f"\nVerdict: {summary.get('verdict', 'Unknown')}")

    return 1 if summary.get("critical_issues", 0) > 0 else 0


def report_command(args: argparse.Namespace) -> int:
    """Generate a full scientific integrity report."""
    from demyst.generators.report_generator import IntegrityReportGenerator
    from demyst.integrations.ci_enforcer import CIEnforcer

    console = get_console()
    logger.info(f"Generating report for {args.path}")

    enforcer = CIEnforcer()

    if os.path.isdir(args.path):
        report = enforcer.analyze_directory(args.path)
        if args.format == "html":
            print(report.to_markdown())  # Fallback to markdown for directory
        elif args.format == "json":
            print(json.dumps(report.to_dict(), indent=2))
        else:
            print(report.to_markdown())
        return 0 if report.badge_status == "passing" else 1

    # Single file - run all checks
    result = enforcer.analyze_file(args.path)

    generator = IntegrityReportGenerator(f"Integrity Report: {args.path}")

    # Add sections from results
    if result.get("mirage") and not result["mirage"].get("error"):
        issues = result["mirage"].get("issues", [])
        generator.add_section(
            "Computational Mirages",
            "fail" if issues else "pass",
            f"Found {len(issues)} variance-destroying operations",
            issues,
            ["Use VariationTensor to preserve statistical metadata"] if issues else [],
        )
        # Add other sections similarly if needed (omitted for brevity in original, preserving behavior)

    if getattr(args, "cert", False):
        # Generate certificate
        # For single file, we read content again or pass it if available.
        # Ideally CIEnforcer returns content or we read it.
        # Since analyze_file doesn't return content, we read it.
        try:
            content = safe_read_file(args.path)
            cert = generator.generate_certificate({args.path: content})
            print(json.dumps(cert, indent=2))
            return 0
        except Exception as e:
            console.print_error(f"Failed to generate certificate: {e}")
            return 1

    if args.format == "html":
        print(generator.to_html())
    elif args.format == "json":
        print(generator.to_json())
    else:
        # Render markdown using Rich
        console.print(generator.to_markdown())

    return 0


def paper_command(args: argparse.Namespace) -> int:
    """Generate LaTeX methodology section from code."""
    from demyst.generators.paper_generator import PaperGenerator

    console = get_console()
    logger.info(f"Generating LaTeX for {args.path}")

    try:
        source = safe_read_file(args.path)
    except Exception as e:
        console.print_error(str(e))
        return 1

    generator = PaperGenerator(style=args.style)

    if args.full:
        latex = generator.generate_full_paper_template(source)
    else:
        latex = generator.generate(source, title=args.title)

    if args.output:
        try:
            with open(args.output, "w") as f:
                f.write(latex)
            console.print_success(f"LaTeX written to {args.output}")
        except Exception as e:
            console.print_error(f"Error writing file: {e}")
            return 1
    else:
        print(latex)

    return 0


def ci_command(args: argparse.Namespace) -> int:
    """Run in CI/CD enforcement mode."""
    from demyst.integrations.ci_enforcer import CIEnforcer

    console = get_console()
    logger.info(f"Running CI enforcement on {args.path}")

    # Load configuration
    config: Dict[str, Any] = {}
    if args.config:
        try:
            import yaml

            with open(args.config, "r") as f:
                config = yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")

    enforcer = CIEnforcer(config=config)

    # CI command likely prints its own output, but let's ensure it uses the console if possible
    # or we capture the result. CIEnforcer.enforce returns exit code.
    # It seems CIEnforcer methods print to stdout. Ideally refactor CIEnforcer too,
    # but for now we just run it.
    exit_code = enforcer.enforce(directory=args.path, fail_on_warning=args.strict)

    return exit_code


def fix_command(args: argparse.Namespace) -> int:
    """Auto-fix command for all detected issues."""
    from demyst.fixer import DemystFixer
    from demyst.integrations.ci_enforcer import CIEnforcer

    console = get_console()
    logger.info(f"Running auto-fix on {args.path}")
    console.print_info(f"Running auto-fix on {args.path}...")

    # First analyze to find issues
    enforcer = CIEnforcer()

    if os.path.isdir(args.path):
        # Directory logic
        fixer = DemystFixer(dry_run=args.dry_run, interactive=args.interactive)
        console.print_warning("Directory auto-fix is currently in beta.")

        if args.dry_run:
            console.print_info("[DRY RUN] Would process files in directory.")
        return 0
    else:
        result = enforcer.analyze_file(args.path)
        fixer = DemystFixer(dry_run=args.dry_run, interactive=args.interactive)

        # Collect all violations
        violations = []
        if result.get("mirage") and not result["mirage"].get("error"):
            violations.extend(result["mirage"].get("issues", []))

        if not violations:
            console.print_success("No issues found to fix.")
            return 0

        fixer.fix_file(args.path, violations)

    return 0


def red_team_command(args: argparse.Namespace) -> int:
    """Run red team benchmark to stress-test Demyst detectors."""
    from demyst.red_team import RedTeamBenchmark

    console = get_console()
    console.print_rule("Demyst Red Team Benchmark")
    console.print_info("Stress-testing detectors with 50 adversarial scenarios...")
    console.print_info("Categories: Mirage, Leakage, Units, Hypothesis, Tensor,")
    console.print_info("            Reproducibility, Numerical, API, Logic, Statistical")
    console.print("")

    benchmark = RedTeamBenchmark()
    benchmark.generate_dataset()
    success = benchmark.run_attack()

    if success:
        console.print_success("\nBenchmark PASSED: All detectors operational.")
        return 0
    else:
        console.print_error("\nBenchmark FAILED: Some attacks evaded detection.")
        return 1


def version_command(args: argparse.Namespace) -> int:
    """Print version information."""
    console = get_console()

    title = f"Demyst v{__version__}"
    console.print_rule(title)
    console.print("Demystify Your Scientific Code")
    console.print("\nComponents:")
    console.print("  - [mirage]MirageDetector[/mirage]: Computational mirage detection")
    console.print("  - [tensor]TensorGuard[/tensor]: Deep learning integrity")
    console.print("  - [leakage]LeakageHunter[/leakage]: Data leakage detection")
    console.print("  - [hypothesis]HypothesisGuard[/hypothesis]: Statistical validity")
    console.print("  - [unit]UnitGuard[/unit]: Dimensional analysis")
    console.print("  - PaperGenerator: LaTeX methodology")
    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Demyst: Scientific Logic Linter",
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
        """,
    )

    parser.add_argument("--version", "-v", action="store_true", help="Show version information")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug output (implies --verbose)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Run all integrity checks")
    analyze_parser.add_argument("path", help="File or directory to analyze")
    analyze_parser.add_argument(
        "--format", "-f", choices=["markdown", "json", "text"], default="text", help="Output format"
    )
    analyze_parser.add_argument("--config", "-c", help="Path to configuration file")
    analyze_parser.add_argument(
        "--profile",
        "-p",
        choices=["physics", "biology", "chemistry", "neuroscience", "climate", "economics"],
        help="Domain-specific profile (physics enables natural units, 5σ thresholds, etc.)",
    )
    analyze_parser.set_defaults(func=analyze_command)

    # Mirage command
    mirage_parser = subparsers.add_parser("mirage", help="Detect computational mirages")
    mirage_parser.add_argument("path", help="File to analyze")
    mirage_parser.add_argument(
        "--fix", action="store_true", help="Auto-fix detected mirages using transpiler"
    )
    mirage_parser.add_argument("--output", "-o", help="Output file for fixed code")
    mirage_parser.add_argument("--diff", action="store_true", help="Show diff of changes")
    mirage_parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without making changes"
    )
    mirage_parser.set_defaults(func=mirage_command)

    # Leakage command
    leakage_parser = subparsers.add_parser("leakage", help="Detect data leakage")
    leakage_parser.add_argument("path", help="File to analyze")
    leakage_parser.set_defaults(func=leakage_command)

    # Hypothesis command
    hypothesis_parser = subparsers.add_parser("hypothesis", help="Check statistical validity")
    hypothesis_parser.add_argument("path", help="File to analyze")
    hypothesis_parser.set_defaults(func=hypothesis_command)

    # Units command
    units_parser = subparsers.add_parser("units", help="Check dimensional consistency")
    units_parser.add_argument("path", help="File to analyze")
    units_parser.set_defaults(func=units_command)

    # Tensor command
    tensor_parser = subparsers.add_parser("tensor", help="Check deep learning integrity")
    tensor_parser.add_argument("path", help="File to analyze")
    tensor_parser.set_defaults(func=tensor_command)

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate integrity report")
    report_parser.add_argument("path", help="File or directory to analyze")
    report_parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "html", "json", "text"],
        default="text",
        help="Output format",
    )
    report_parser.add_argument(
        "--cert", action="store_true", help="Generate Certificate of Integrity (JSON)"
    )
    report_parser.set_defaults(func=report_command)

    # Paper command
    paper_parser = subparsers.add_parser("paper", help="Generate LaTeX methodology")
    paper_parser.add_argument("path", help="File to analyze")
    paper_parser.add_argument("--output", "-o", help="Output file")
    paper_parser.add_argument("--title", "-t", default="Methodology", help="Section title")
    paper_parser.add_argument(
        "--style",
        "-s",
        choices=["neurips", "icml", "iclr", "arxiv"],
        default="neurips",
        help="Paper style",
    )
    paper_parser.add_argument("--full", action="store_true", help="Generate full paper template")
    paper_parser.set_defaults(func=paper_command)

    # CI command
    ci_parser = subparsers.add_parser("ci", help="CI/CD enforcement mode")
    ci_parser.add_argument("path", nargs="?", default=".", help="Directory to analyze")
    ci_parser.add_argument(
        "--strict", action="store_true", help="Fail on warnings (not just critical issues)"
    )
    ci_parser.add_argument("--config", "-c", help="Path to configuration file")
    ci_parser.set_defaults(func=ci_command)

    # Fix command
    fix_parser = subparsers.add_parser("fix", help="Auto-fix issues")
    fix_parser.add_argument("path", help="File or directory to fix")
    fix_parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    fix_parser.add_argument(
        "--interactive", "-i", action="store_true", help="Ask before applying fix"
    )
    fix_parser.set_defaults(func=fix_command)

    # Red Team command
    red_team_parser = subparsers.add_parser(
        "red-team", help="Run adversarial benchmark against Demyst detectors"
    )
    red_team_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed results for each test case"
    )
    red_team_parser.set_defaults(func=red_team_command)

    args = parser.parse_args()

    # Setup logging
    setup_logging(
        verbose=getattr(args, "verbose", False),
        debug=getattr(args, "debug", False) or bool(os.environ.get("DEMYST_DEBUG")),
    )

    if args.version:
        return version_command(args)

    if args.command is None:
        parser.print_help()
        return 0

    try:
        return int(args.func(args))
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
        if args.debug or os.environ.get("DEMYST_DEBUG"):
            logger.exception("Unexpected error")
        return 1


if __name__ == "__main__":
    sys.exit(main())
