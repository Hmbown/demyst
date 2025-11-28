"""
Demyst MCP Server.

Exposes Demyst scientific integrity checks as Model Context Protocol (MCP) tools.
This allows AI agents (Claude, Cursor, etc.) to verify their own scientific code.
"""

import ast
import ast
import json
import logging
import os
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from demyst.engine.mirage_detector import MirageDetector
from demyst.guards.unit_guard import UnitGuard
from demyst.config.manager import ConfigManager

# Initialize FastMCP server
mcp = FastMCP("demyst")

# Setup logging
logger = logging.getLogger("demyst.mcp")
logging.basicConfig(level=logging.INFO)



class MirageResult(BaseModel):
    """Result of mirage detection."""
    has_mirages: bool = Field(..., description="Whether any computational mirages were found")
    mirages: List[Dict[str, Any]] = Field(..., description="List of detected mirages")
    recommendations: List[str] = Field(..., description="Recommendations for fixing mirages")

class UnitResult(BaseModel):
    """Result of unit consistency check."""
    consistent: bool = Field(..., description="Whether units are consistent")
    violations: List[Dict[str, Any]] = Field(..., description="List of unit violations")
    inferred_dimensions: Dict[str, str] = Field(..., description="Inferred dimensions of variables")

class SignedCertificate(BaseModel):
    """Cryptographic proof of verification."""
    code_hash: str = Field(..., description="SHA-256 hash of the code")
    verdict: str = Field(..., description="Verification verdict (PASS/FAIL)")
    timestamp: str = Field(..., description="ISO timestamp of verification")
    signature: str = Field(..., description="HMAC-SHA256 signature")

@mcp.tool()
def detect_mirage(code: str) -> str:
    """
    Detects computational mirages (variance-destroying operations) in scientific code.
    
    Use this tool to check if code performs operations like `mean`, `sum`, or `argmax`
    on high-variance or heavy-tailed distributions without proper handling.
    
    Args:
        code: The Python code to analyze.
        
    Returns:
        JSON string containing detection results and recommendations.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return json.dumps({"error": f"Syntax error: {e}"})

    config_manager = ConfigManager()
    detector = MirageDetector(config=config_manager.get_rule_config("mirage"))
    detector.visit(tree)

    # Clean up mirages for serialization (remove AST nodes)
    serializable_mirages = []
    for m in detector.mirages:
        clean_m = m.copy()
        if "node" in clean_m:
            del clean_m["node"]
        serializable_mirages.append(clean_m)

    recommendations = []
    if serializable_mirages:
        recommendations.append("Use VariationTensor to preserve statistical metadata.")
        recommendations.append("Check if the distribution is heavy-tailed before aggregating.")

    result = MirageResult(
        has_mirages=bool(serializable_mirages),
        mirages=serializable_mirages,
        recommendations=recommendations
    )
    
    return result.model_dump_json()

@mcp.tool()
def check_units(code: str) -> str:
    """
    Checks for dimensional consistency in scientific code.
    
    Use this tool to verify that physical units are handled correctly (e.g., not adding
    meters to seconds).
    
    Args:
        code: The Python code to analyze.
        
    Returns:
        JSON string containing consistency results and inferred dimensions.
    """
    config_manager = ConfigManager()
    guard = UnitGuard(config=config_manager.get_rule_config("unit"))
    
    try:
        analysis = guard.analyze(code)
    except Exception as e:
        return json.dumps({"error": f"Analysis failed: {e}"})
        
    violations = analysis.get("violations", [])
    
    result = UnitResult(
        consistent=len(violations) == 0,
        violations=violations,
        inferred_dimensions=analysis.get("inferred_dimensions", {})
    )
    
    return result.model_dump_json()

@mcp.tool()
def sign_verification(code: str, verdict: str) -> str:
    """
    Generates a cryptographic certificate of integrity for verified code.
    
    Use this tool AFTER running checks to freeze the code state and prove it passed.
    
    Args:
        code: The verified Python code.
        verdict: The result of the checks (e.g., "PASS", "FAIL").
        
    Returns:
        JSON string containing the certificate with signature.
    """
    from demyst.security import sign_code
    
    cert_dict = sign_code(code, verdict)
    
    cert = SignedCertificate(
        code_hash=cert_dict["code_hash"],
        verdict=cert_dict["verdict"],
        timestamp=cert_dict["timestamp"],
        signature=cert_dict["signature"]
    )
    
    return cert.model_dump_json()

if __name__ == "__main__":
    mcp.run()
