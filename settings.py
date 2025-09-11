"""
Dynaconf configuration for TRIAXUS visualization system
"""

from dynaconf import Dynaconf

# Create dynaconf instance
settings = Dynaconf(
    # Main configuration files
    settings_files=[
        "configs/default.yaml",
        "configs/custom.yaml",  # Optional custom overrides
        "configs/themes/*.yaml",  # Theme files
    ],
    # Environment variables prefix
    envvar_prefix="TRIAXUS",
    # Environments
    environments=True,
    default_env="default",
    # Load additional files
    load_dotenv=True,
    # Merge with environment variables
    merge_enabled=True,
    # Validation
    validate_on_update=True,
    # Core settings
    core_loaders=["YAML", "ENV"],
    # File paths
    root_path=".",
    # Silent errors for missing files
    silent=True,
)

# Export settings
__all__ = ["settings"]
