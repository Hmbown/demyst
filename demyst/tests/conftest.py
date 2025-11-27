"""
Demyst Test Configuration and Fixtures

Provides shared fixtures for all test modules:
- Path fixtures for project root and examples directory
- Source code fixtures for each example file
- Guard instance fixtures (mirage_detector, hypothesis_guard, unit_guard)
"""

import pytest
from pathlib import Path


# Project root detection
@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def examples_dir(project_root) -> Path:
    """Return the examples directory."""
    return project_root / "examples"


# Example file paths
@pytest.fixture(scope="session")
def swarm_collapse_path(examples_dir) -> Path:
    """Path to swarm_collapse.py example."""
    return examples_dir / "swarm_collapse.py"


@pytest.fixture(scope="session")
def random_walk_path(examples_dir) -> Path:
    """Path to random_walk.py example."""
    return examples_dir / "random_walk.py"


@pytest.fixture(scope="session")
def physics_kinematics_path(examples_dir) -> Path:
    """Path to physics_kinematics.py example."""
    return examples_dir / "physics_kinematics.py"


@pytest.fixture(scope="session")
def biology_gene_expression_path(examples_dir) -> Path:
    """Path to biology_gene_expression.py example."""
    return examples_dir / "biology_gene_expression.py"


@pytest.fixture(scope="session")
def chemistry_stoichiometry_path(examples_dir) -> Path:
    """Path to chemistry_stoichiometry.py example."""
    return examples_dir / "chemistry_stoichiometry.py"


# Source code fixtures
@pytest.fixture(scope="session")
def swarm_collapse_source(swarm_collapse_path) -> str:
    """Source code of swarm_collapse.py."""
    return swarm_collapse_path.read_text()


@pytest.fixture(scope="session")
def random_walk_source(random_walk_path) -> str:
    """Source code of random_walk.py."""
    return random_walk_path.read_text()


@pytest.fixture(scope="session")
def physics_kinematics_source(physics_kinematics_path) -> str:
    """Source code of physics_kinematics.py."""
    return physics_kinematics_path.read_text()


@pytest.fixture(scope="session")
def biology_gene_expression_source(biology_gene_expression_path) -> str:
    """Source code of biology_gene_expression.py."""
    return biology_gene_expression_path.read_text()


@pytest.fixture(scope="session")
def chemistry_stoichiometry_source(chemistry_stoichiometry_path) -> str:
    """Source code of chemistry_stoichiometry.py."""
    return chemistry_stoichiometry_path.read_text()


# Guard instances
@pytest.fixture
def mirage_detector():
    """Fresh MirageDetector instance."""
    from demyst.engine.mirage_detector import MirageDetector
    return MirageDetector()


@pytest.fixture
def hypothesis_guard():
    """Fresh HypothesisGuard instance."""
    from demyst.guards.hypothesis_guard import HypothesisGuard
    return HypothesisGuard()


@pytest.fixture
def unit_guard():
    """Fresh UnitGuard instance."""
    from demyst.guards.unit_guard import UnitGuard
    return UnitGuard()


@pytest.fixture
def tensor_guard():
    """Fresh TensorGuard instance."""
    from demyst.guards.tensor_guard import TensorGuard
    return TensorGuard()


@pytest.fixture
def leakage_hunter():
    """Fresh LeakageHunter instance."""
    from demyst.guards.leakage_hunter import LeakageHunter
    return LeakageHunter()
