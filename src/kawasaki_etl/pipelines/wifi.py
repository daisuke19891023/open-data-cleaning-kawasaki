from __future__ import annotations

import datetime
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pandas as pd
from pandas import DataFrame, Series

from kawasaki_etl.core import (
    DatasetConfig,
    DownloadError,
    NormalizationError,
    calculate_sha256,
    download_if_needed,
    is_already_loaded,
    mark_loaded,
    normalize_column_name,
    normalize_csv,
)
from kawasaki_etl.core.db import UpsertError, get_engine, upsert_dataframe
from kawasaki_etl.utils.logger import LoggerProtocol, get_logger

if TYPE_CHECKING:
    from collections.abc import Iterable
    from sqlalchemy.engine import Engine

NORMALIZED_DATA_DIR = Path("data/normalized")
DEFAULT_TABLE_NAME = "wifi_access_counts"
DEFAULT_KEY_FIELDS = ["date", "spot_id"]

logger: LoggerProtocol = get_logger(__name__)

DEFAULT_COLUMN_CANDIDATES: dict[str, list[str]] = {
    "date": ["date", "日付", "年月日", "収集日"],
    "spot_id": ["spot_id", "スポットid", "スポットID", "地点ID"],
    "spot_name": ["spot_name", "スポット名", "施設名"],
    "connection_count": ["接続数", "接続回数", "利用回数", "connections"],
}


class WifiPipelineError(Exception):
    """Raised when Wi-Fi pipeline fails."""


def _resolve_column_name(  # pyright: ignore[reportUnknownArgumentType,reportUnknownVariableType,reportUnknownMemberType]
    df: DataFrame, target: str, candidates: Iterable[str],
) -> str:
    column_names: list[str] = [
        str(col) for col in cast("list[object]", df.columns.to_list())
    ]
    normalized_columns: dict[str, str] = {}
    for name in column_names:
        normalized_key: str = normalize_column_name(name).lower()  # pyright: ignore[reportUnknownArgumentType]
        normalized_columns[normalized_key] = name
    for candidate in candidates:
        key = normalize_column_name(str(candidate)).lower()
        if key in normalized_columns:
            return normalized_columns[key]

    msg = f"Required column for '{target}' not found; checked: {candidates}"
    raise WifiPipelineError(msg)


def _rename_wifi_columns(df: DataFrame, config: DatasetConfig) -> DataFrame:
    column_mapping_raw = config.extra.get("column_mapping", {})
    column_mapping: dict[str, list[str] | str] = cast(
        "dict[str, list[str] | str]",
        column_mapping_raw,
    )
    resolved: dict[str, str] = {}

    for logical_name, default_candidates in DEFAULT_COLUMN_CANDIDATES.items():
        custom_candidates_raw = column_mapping.get(logical_name)
        if custom_candidates_raw is None:
            candidates: list[str] = default_candidates
        elif isinstance(custom_candidates_raw, str):
            candidates = [custom_candidates_raw]
        elif isinstance(custom_candidates_raw, list):  # pyright: ignore[reportUnnecessaryIsInstance]
            candidates = [str(item) for item in custom_candidates_raw]
        else:
            msg = f"column_mapping for '{logical_name}' must be string or list"
            raise WifiPipelineError(msg)

        source_name = _resolve_column_name(df, logical_name, candidates)
        resolved[source_name] = logical_name

    return df.rename(columns=resolved)


def _prepare_wifi_dataframe(df: DataFrame, config: DatasetConfig) -> DataFrame:
    renamed = _rename_wifi_columns(df, config)
    required_columns = ["date", "spot_id", "connection_count"]

    missing = [col for col in required_columns if col not in renamed.columns]
    if missing:
        msg = f"Missing required columns after renaming: {missing}"
        raise WifiPipelineError(msg)

    processed: DataFrame = renamed.copy()
    # Normalize Series typing for downstream datetime/astype operations
    date_raw: Series = cast(
        "Series", processed.loc[:, "date"],
    )  # pyright: ignore[reportUnnecessaryCast]
    date_series: Series = pd.to_datetime(  # pyright: ignore[reportUnknownMemberType]
        date_raw,
        errors="coerce",
    )
    processed["date"] = date_series.dt.date  # pyright: ignore[reportUnknownMemberType]

    spot_id_raw: Series = cast(
        "Series", processed.loc[:, "spot_id"],
    )  # pyright: ignore[reportUnnecessaryCast]
    processed["spot_id"] = spot_id_raw.astype(str)  # pyright: ignore[reportUnknownMemberType]

    connection_raw: Series = cast(
        "Series", processed.loc[:, "connection_count"],
    )  # pyright: ignore[reportUnnecessaryCast]
    connection_series: Series = cast(
        "Series",
        pd.to_numeric(  # pyright: ignore[reportUnknownMemberType]
            connection_raw,
            errors="coerce",
        ),
    )  # pyright: ignore[reportUnnecessaryCast]
    processed["connection_count"] = connection_series.fillna(0)  # pyright: ignore[reportUnknownMemberType]

    processed = processed.dropna(subset=["date", "spot_id"])  # pyright: ignore[reportUnknownMemberType]

    if config.snapshot_date:
        processed["snapshot_date"] = config.snapshot_date
    processed["dataset_id"] = config.dataset_id

    # Keep only known columns to simplify table mapping
    keep_columns = [
        "dataset_id",
        "date",
        "spot_id",
        "spot_name",
        "connection_count",
        "snapshot_date",
    ]
    extra_columns: list[str] = [
        str(col) for col in processed.columns if str(col) not in keep_columns  # pyright: ignore[reportUnknownArgumentType,reportUnknownVariableType]
    ]
    if extra_columns:
        processed = processed.drop(columns=extra_columns)

    return processed


def _normalized_path(dataset: DatasetConfig, raw_path: Path) -> Path:
    directory = NORMALIZED_DATA_DIR / dataset.category / dataset.dataset_id
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{raw_path.stem}_normalized.csv"


def run_wifi_count(config: DatasetConfig, engine: Engine | None = None) -> None:
    """Run Wi-Fi connection count pipeline."""
    logger.info("Starting Wi-Fi pipeline", dataset_id=config.dataset_id)

    table_name = config.table or DEFAULT_TABLE_NAME
    key_fields = config.key_fields or DEFAULT_KEY_FIELDS

    try:
        raw_path = download_if_needed(config)
        sha256 = calculate_sha256(raw_path)

        if is_already_loaded(config, raw_path, sha256):
            return

        normalized_path = _normalized_path(config, raw_path)
        normalized_df = normalize_csv(raw_path, normalized_path)
        prepared_df = _prepare_wifi_dataframe(normalized_df, config)

        db_engine = engine or get_engine()
        upsert_dataframe(prepared_df, table_name, key_fields, db_engine)

        mark_loaded(
            config,
            raw_path,
            sha256,
            processed_at=datetime.datetime.now(tz=datetime.UTC),
        )
        logger.info("Wi-Fi pipeline completed", dataset_id=config.dataset_id)
    except (DownloadError, NormalizationError, UpsertError, WifiPipelineError) as exc:
        logger.error(
            "Wi-Fi pipeline failed", dataset_id=config.dataset_id, error=str(exc),
        )
        raise
