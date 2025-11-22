"""Core functionality for Kawasaki ETL."""

from kawasaki_etl.core.models import (
    DatasetConfig,
    DatasetConfigError,
    get_dataset_config,
    load_dataset_configs,
)

__all__ = [
    "DatasetConfig",
    "DatasetConfigError",
    "get_dataset_config",
    "load_dataset_configs",
]
