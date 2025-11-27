"""
Scilint: The Scientific Integrity Platform

A comprehensive tool for ensuring scientific integrity in machine learning
and data science code. Scilint detects computational mirages, data leakage,
statistical validity issues, dimensional inconsistencies, and deep learning
integrity problems.

Philosophy: "Good Code is Good Science."

Components:
    - MirageDetector: Detects variance-destroying operations
    - TensorGuard: Deep learning integrity (PyTorch/JAX)
    - LeakageHunter: Train/test data leakage detection
    - HypothesisGuard: Anti-p-hacking and statistical validity
    - UnitGuard: Dimensional analysis and unit consistency
    - PaperGenerator: LaTeX methodology section generator
    - CIEnforcer: CI/CD pipeline integration

Usage:
    from scilint.guards import TensorGuard, LeakageHunter, HypothesisGuard, UnitGuard
    from scilint.integrations import CIEnforcer
    from scilint.generators import PaperGenerator

CLI:
    scilint analyze ./src       # Run all integrity checks
    scilint mirage model.py     # Detect computational mirages
    scilint ci . --strict       # CI/CD mode
"""

__version__ = "1.0.0"
__author__ = "Scilint Team"
__description__ = "The Scientific Integrity Platform for AI Research"

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    """Lazy loading of components to avoid import errors when dependencies aren't installed."""
    if name in ['MirageDetector']:
        from scilint.engine.mirage_detector import MirageDetector
        return MirageDetector
    elif name in ['VariationTensor']:
        from scilint.engine.variation_tensor import VariationTensor
        return VariationTensor
    elif name in ['Transpiler']:
        from scilint.engine.transpiler import Transpiler
        return Transpiler
    elif name in ['TensorGuard', 'GradientDeathDetector', 'NormalizationAnalyzer', 'RewardHackingDetector']:
        from scilint.guards import tensor_guard
        return getattr(tensor_guard, name)
    elif name in ['LeakageHunter', 'TaintAnalyzer', 'DataFlowTracker']:
        from scilint.guards import leakage_hunter
        return getattr(leakage_hunter, name)
    elif name in ['HypothesisGuard', 'BonferroniCorrector', 'ExperimentTracker']:
        from scilint.guards import hypothesis_guard
        return getattr(hypothesis_guard, name)
    elif name in ['UnitGuard', 'DimensionalAnalyzer', 'UnitInferenceEngine', 'Dimension']:
        from scilint.guards import unit_guard
        return getattr(unit_guard, name)
    elif name in ['CIEnforcer', 'ScientificIntegrityReport']:
        from scilint.integrations import ci_enforcer
        return getattr(ci_enforcer, name)
    elif name in ['TorchVariation', 'TorchModuleWrapper']:
        from scilint.integrations import torch_hooks
        return getattr(torch_hooks, name)
    elif name in ['JaxVariation', 'jax_safe_transform']:
        from scilint.integrations import jax_hooks
        return getattr(jax_hooks, name)
    elif name in ['WandBIntegration', 'MLflowIntegration']:
        from scilint.integrations import experiment_trackers
        return getattr(experiment_trackers, name)
    elif name in ['PaperGenerator', 'MethodologyExtractor']:
        from scilint.generators import paper_generator
        return getattr(paper_generator, name)
    elif name in ['IntegrityReportGenerator']:
        from scilint.generators import report_generator
        return getattr(report_generator, name)
    raise AttributeError(f"module 'scilint' has no attribute '{name}'")


__all__ = [
    # Version
    '__version__',

    # Core
    'MirageDetector',
    'VariationTensor',
    'Transpiler',

    # Guards
    'TensorGuard',
    'GradientDeathDetector',
    'NormalizationAnalyzer',
    'RewardHackingDetector',
    'LeakageHunter',
    'TaintAnalyzer',
    'DataFlowTracker',
    'HypothesisGuard',
    'BonferroniCorrector',
    'ExperimentTracker',
    'UnitGuard',
    'DimensionalAnalyzer',
    'UnitInferenceEngine',
    'Dimension',

    # Integrations
    'CIEnforcer',
    'ScientificIntegrityReport',
    'TorchVariation',
    'TorchModuleWrapper',
    'JaxVariation',
    'jax_safe_transform',
    'WandBIntegration',
    'MLflowIntegration',

    # Generators
    'PaperGenerator',
    'MethodologyExtractor',
    'IntegrityReportGenerator',
]
