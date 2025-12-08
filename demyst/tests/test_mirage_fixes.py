import ast
from pathlib import Path

from demyst.engine.cst_transformer import CSTTranspiler
from demyst.engine.parallel import _analyze_file_worker
from demyst.engine.mirage_detector import MirageDetector


def test_cst_preserves_axis_keepdims(tmp_path: Path) -> None:
    source = "import numpy as np\nresult = np.mean(x, axis=1, keepdims=True)\n"
    transformed = CSTTranspiler().transpile_source(source)

    assert "VariationTensor" in transformed
    assert ("axis=1" in transformed) or ("axis = 1" in transformed)
    assert ("keepdims=True" in transformed) or ("keepdims = True" in transformed)
    assert ".collapse('mean')" in transformed


def test_cst_transforms_argmax() -> None:
    source = "import numpy as np\nval = np.argmax(x)\n"
    transformed = CSTTranspiler().transpile_source(source)

    assert "VariationTensor" in transformed
    assert ".collapse('argmax')" in transformed


def test_cst_discretization_wrapper() -> None:
    source = "val = int(x)\n"
    transformed = CSTTranspiler().transpile_source(source)

    assert "VariationTensor" in transformed
    assert ".discretize('int')" in transformed


def test_parallel_respects_inline_suppression(tmp_path: Path) -> None:
    code = "import numpy as np\nx = np.array([1, 2, 3])\nnp.mean(x)  # demyst: ignore-mirage\n"
    file_path = tmp_path / "suppressed.py"
    file_path.write_text(code)

    result = _analyze_file_worker(
        (
            str(file_path),
            {
                "mirage": True,
                "leakage": False,
                "hypothesis": False,
                "unit": False,
                "tensor": False,
            },
        )
    )

    assert result.mirage_count == 0


def test_mean_with_variance_context_not_flagged() -> None:
    code = """
import numpy as np

def analyze(values):
    mu = np.mean(values)
    sigma = np.std(values)
    return mu / sigma
"""
    detector = MirageDetector()
    tree = ast.parse(code)
    issues = detector.analyze(tree, source=code)

    # Variance context should suppress the mean mirage
    assert all(issue["type"] != "mean" for issue in issues)
