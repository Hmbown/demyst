"""
Configuration Manager for Demyst

Handles loading and merging of configuration from:
1. Default settings
2. Domain profiles
3. User .demystrc.yaml file
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigManager:
    """Manages Demyst configuration."""

    DEFAULT_CONFIG = {
        "profile": "default",
        "rules": {
            "mirage": {
                "enabled": True,
                "severity": "critical",
                "exclude": []
            },
            "tensor": {
                "enabled": True,
                "severity": "critical",
                "exclude": []
            },
            "leakage": {
                "enabled": True,
                "severity": "critical",
                "exclude": []
            },
            "hypothesis": {
                "enabled": True,
                "severity": "warning",
                "exclude": []
            },
            "unit": {
                "enabled": True,
                "severity": "warning",
                "exclude": []
            }
        },
        "ignore_patterns": [
            "**/test_*", "**/*_test.py", "**/tests/**",
            "**/.git/**", "**/venv/**", "**/__pycache__/**"
        ]
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or ".demystrc.yaml"
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load and merge configuration."""
        config = self.DEFAULT_CONFIG.copy()

        # Load from file if exists
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        config = self._merge_configs(config, user_config)
            except Exception as e:
                print(f"Warning: Failed to load config file {self.config_path}: {e}")

        # Load profile if specified
        profile_name = config.get("profile", "default")
        if profile_name != "default":
             profile_config = self._load_profile(profile_name)
             if profile_config:
                 # Profile overrides defaults, but user config overrides profile
                 # So we merge profile into defaults, then user config into that
                 # Re-loading user config to ensure it takes precedence
                 base_config = self.DEFAULT_CONFIG.copy()
                 merged_with_profile = self._merge_configs(base_config, profile_config)

                 if os.path.exists(self.config_path):
                     with open(self.config_path, 'r') as f:
                         user_config = yaml.safe_load(f)
                         if user_config:
                             config = self._merge_configs(merged_with_profile, user_config)
                         else:
                             config = merged_with_profile
                 else:
                     config = merged_with_profile

        return config

    def _load_profile(self, profile_name: str) -> Dict[str, Any]:
        """Load a domain-specific profile."""
        try:
            # Dynamic import of profile module
            module_name = f"demyst.profiles.{profile_name}"
            import importlib
            module = importlib.import_module(module_name)
            return getattr(module, "PROFILE", {})
        except ImportError:
            print(f"Warning: Profile '{profile_name}' not found. Using default.")
            return {}
        except Exception as e:
            print(f"Warning: Error loading profile '{profile_name}': {e}")
            return {}

    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two configurations."""
        merged = base.copy()
        for key, value in override.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged

    def get_rule_config(self, rule_name: str) -> Dict[str, Any]:
        """Get configuration for a specific rule."""
        return self.config.get("rules", {}).get(rule_name, {})

    def is_rule_enabled(self, rule_name: str) -> bool:
        """Check if a rule is enabled."""
        return self.get_rule_config(rule_name).get("enabled", True)

    def get_ignore_patterns(self) -> list:
        """Get global ignore patterns."""
        return self.config.get("ignore_patterns", [])
