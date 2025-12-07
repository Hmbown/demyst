"""
Demyst LangChain Integration.

Provides a verification tool for LangChain agents to self-correct scientific code.

Note: Full functionality requires Python 3.10+ for MCP integration.
"""

import json
import logging
import sys
from typing import Any, Dict, Optional, Type

try:
    from langchain_core.tools import BaseTool
except Exception as e:  # pragma: no cover - import guard
    raise ImportError(
        "LangChain integration requires the optional dependency 'langchain-core'. "
        "Install with `pip install langchain-core` or `pip install demyst[all]`."
    ) from e

from pydantic import BaseModel, Field

from demyst.integrations.ci_enforcer import CIEnforcer

# MCP features require Python 3.10+ and optional mcp dependency
if sys.version_info >= (3, 10):
    try:
        from demyst.mcp import sign_verification
    except ImportError:
        sign_verification = None  # type: ignore[assignment]
else:
    sign_verification = None  # type: ignore[assignment]

logger = logging.getLogger("demyst.agents")


class DemystVerifierInput(BaseModel):
    code: str = Field(..., description="The Python code to verify.")


class DemystVerifier(BaseTool):
    """
    A LangChain tool that verifies scientific code integrity.

    If the code passes all checks, it returns a signed certificate.
    If it fails, it returns a structured error report to help the agent fix it.
    """

    name: str = "demyst_verify"
    description: str = (
        "Verifies scientific code for integrity issues (mirages, leakage, units). "
        "Use this BEFORE returning code to the user. "
        "Returns a signed certificate if valid, or error details if invalid."
    )
    args_schema: Type[BaseModel] = DemystVerifierInput

    def _run(self, code: str, run_manager: Optional[Any] = None) -> str:
        """Run the verification."""
        enforcer = CIEnforcer()

        # We need to analyze the code string. CIEnforcer.analyze_file takes a path.
        # We'll use the internal guards directly or save to a temp file.
        # Using internal logic is cleaner for an agent loop.

        # Re-using logic similar to magic.py/mcp.py
        results = self._analyze_code(enforcer, code)

        if results["passed"]:
            # Generate certificate (requires Python 3.10+ for MCP)
            if sign_verification is not None:
                cert_json = sign_verification(code, "PASS")
                return f"VERIFICATION PASSED.\nCertificate: {cert_json}"
            else:
                return "VERIFICATION PASSED. (Certificate signing requires Python 3.10+)"
        else:
            # Format feedback
            feedback = ["VERIFICATION FAILED. Please fix the following issues:"]
            for issue in results["issues"]:
                feedback.append(f"- [{issue['type']}] {issue['description']}")
                if issue.get("recommendation"):
                    feedback.append(f"  Tip: {issue['recommendation']}")

            return "\n".join(feedback)

    async def _arun(self, code: str, run_manager: Optional[Any] = None) -> str:
        """Async version (just calls sync for now)."""
        return self._run(code, run_manager)

    def _analyze_code(self, enforcer: CIEnforcer, code: str) -> Dict[str, Any]:
        """Run all checks on the code string."""
        issues = []

        # 1. Mirage
        if enforcer.config_manager.is_rule_enabled("mirage"):
            try:
                import ast

                tree = ast.parse(code)
                detector = enforcer.MirageDetector(
                    config=enforcer.config_manager.get_rule_config("mirage")
                )
                detector.visit(tree)
                for m in detector.mirages:
                    issues.append(
                        {
                            "type": "Mirage",
                            "description": f"Computational mirage detected: {m['type']}",
                            "recommendation": "Use VariationTensor to preserve variance.",
                        }
                    )
            except Exception as e:
                logger.debug(f"Mirage check failed: {e}")

        # 2. Units
        if enforcer.config_manager.is_rule_enabled("unit"):
            try:
                guard = enforcer.UnitGuard(config=enforcer.config_manager.get_rule_config("unit"))
                res = guard.analyze(code)
                for v in res.get("violations", []):
                    issues.append(
                        {
                            "type": "Units",
                            "description": v["description"],
                            "recommendation": v.get("recommendation"),
                        }
                    )
            except Exception as e:
                logger.debug(f"Unit check failed: {e}")

        # 3. Leakage
        if enforcer.config_manager.is_rule_enabled("leakage"):
            try:
                hunter = enforcer.LeakageHunter(
                    config=enforcer.config_manager.get_rule_config("leakage")
                )
                res = hunter.analyze(code)
                for v in res.get("violations", []):
                    issues.append(
                        {
                            "type": "Leakage",
                            "description": v["description"],
                            "recommendation": "Separate training and test data.",
                        }
                    )
            except Exception as e:
                logger.debug(f"Leakage check failed: {e}")

        return {"passed": len(issues) == 0, "issues": issues}
