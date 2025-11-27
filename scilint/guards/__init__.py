"""
Scilint Guards - The Immune System for AI Science

This module contains specialized guards that detect various classes of
scientific integrity issues in machine learning and data science code.

Guards:
    - TensorGuard: Deep learning integrity (PyTorch/JAX)
    - LeakageHunter: Train/test data leakage detection
    - HypothesisGuard: Anti-p-hacking and statistical validity
    - UnitGuard: Dimensional analysis and unit consistency
"""

from .tensor_guard import TensorGuard, GradientDeathDetector, NormalizationAnalyzer, RewardHackingDetector
from .leakage_hunter import LeakageHunter, TaintAnalyzer, DataFlowTracker
from .hypothesis_guard import HypothesisGuard, BonferroniCorrector, ExperimentTracker
from .unit_guard import UnitGuard, DimensionalAnalyzer, UnitInferenceEngine

__all__ = [
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
]
