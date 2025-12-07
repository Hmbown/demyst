# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-12-07

### Added
- Firebase integration for cloud deployment and authentication
- AST-based transpiler with LibCST support for safe code transformations
- VariationTensor data structure for preserving physical information
- Comprehensive guard system:
  - MirageDetector for variance-destroying operations
  - LeakageHunter for train/test data leakage detection
  - HypothesisGuard for statistical validity (anti-p-hacking)
  - UnitGuard for dimensional analysis
  - TensorGuard for deep learning integrity
- MCP (Model Context Protocol) server integration for AI agents
- Red Team benchmark suite for validation
- CLI commands for all guard types
- Auto-fix functionality for computational mirages
- LaTeX methodology generation
- Integrity certificate generation
- CI/CD integration with GitHub Actions
- Pre-commit hooks support

### Fixed
- Null byte handling in AST parsing
- Import consistency across modules
- Test suite compatibility with Python 3.14
- CLI argument parsing and error handling

### Improved
- Enhanced error messages with detailed explanations
- Better performance on large codebases
- Improved documentation and examples
- Cleaner separation of concerns between modules

### Removed
- Internal documentation and debug artifacts
- Temporary build files and caches
- AI-generated development artifacts

## [1.1.0] - 2025-11-27

### Added
- Initial public release
- Core scientific linter functionality
- Support for numpy, PyTorch, and JAX
- Basic documentation and examples

## [1.0.0] - 2025-11-20

### Added
- Project inception
- Basic architecture and design