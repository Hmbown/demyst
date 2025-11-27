"""
Physics Domain Profile

Focus: Conservation laws, uncertainty propagation, dimensional consistency.
"""

PROFILE = {
    "rules": {
        "unit": {
            "enabled": True,
            "severity": "critical"  # Dimensional errors are critical in physics
        },
        "mirage": {
            "enabled": True,
            "severity": "critical"  # Variance destruction is bad for error propagation
        },
        "hypothesis": {
            "enabled": True,
            "severity": "warning"
        },
        "leakage": {
            "enabled": True,
            "severity": "warning"
        }
    }
}
