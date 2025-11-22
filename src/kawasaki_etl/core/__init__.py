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
from kawasaki_etl.core.normalize import (
    COMMON_ENCODINGS,
    NormalizationError,
    detect_encoding_and_read_csv,
    normalize_column_name,
    normalize_columns,
    normalize_csv,
    normalize_excel,
    normalize_zip_of_csv,
)

__all__ = [
    "DatasetConfig",
    "DatasetConfigError",
    "DownloadError",
    "COMMON_ENCODINGS",
    "NormalizationError",
    "download_file",
    "download_if_needed",
    "detect_encoding_and_read_csv",
    "get_dataset_config",
    "get_raw_path",
    "load_dataset_configs",
    "normalize_column_name",
    "normalize_columns",
    "normalize_csv",
    "normalize_excel",
    "normalize_zip_of_csv",
]
