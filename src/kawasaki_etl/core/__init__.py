"""Core functionality for Kawasaki ETL."""

from kawasaki_etl.core.models import (
    DatasetConfig,
    DatasetConfigError,
    get_dataset_config,
    load_dataset_configs,
)
from kawasaki_etl.core.io import (
    DownloadError,
    download_file,
    download_if_needed,
    get_raw_path,
)

__all__ = [
    "DatasetConfig",
    "DatasetConfigError",
    "DownloadError",
    "download_file",
    "download_if_needed",
    "get_dataset_config",
    "get_raw_path",
    "load_dataset_configs",
]
