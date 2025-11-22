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
from kawasaki_etl.core.db import (
    DBConfigError,
    DBConnectionError,
    UpsertError,
    get_engine,
    upsert_dataframe,
)
from kawasaki_etl.core.meta_store import (
    calculate_sha256,
    get_meta_path,
    is_already_loaded,
    mark_loaded,
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
    "COMMON_ENCODINGS",
    "DBConfigError",
    "DBConnectionError",
    "DatasetConfig",
    "DatasetConfigError",
    "DownloadError",
    "NormalizationError",
    "UpsertError",
    "calculate_sha256",
    "detect_encoding_and_read_csv",
    "download_file",
    "download_if_needed",
    "get_dataset_config",
    "get_engine",
    "get_meta_path",
    "get_raw_path",
    "is_already_loaded",
    "load_dataset_configs",
    "mark_loaded",
    "normalize_column_name",
    "normalize_columns",
    "normalize_csv",
    "normalize_excel",
    "normalize_zip_of_csv",
    "upsert_dataframe",
]
