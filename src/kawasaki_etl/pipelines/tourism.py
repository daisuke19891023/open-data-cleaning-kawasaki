from __future__ import annotations

import datetime
from pathlib import Path

from typing import TYPE_CHECKING


from kawasaki_etl.core import (
    DatasetConfig,
    DownloadError,
    calculate_sha256,
    download_if_needed,
    is_already_loaded,
    mark_loaded,
)
from kawasaki_etl.core.pdf_utils import (
    TourismPdfExtractionError,
    extract_tables_from_tourism_irikomi,
)
from kawasaki_etl.utils.logger import LoggerProtocol, get_logger

if TYPE_CHECKING:
    import pandas as pd


NORMALIZED_DATA_DIR = Path("data/normalized")

logger: LoggerProtocol = get_logger(__name__)


class TourismPipelineError(Exception):
    """Raised when tourism pipelines fail."""


def _normalized_path(dataset: DatasetConfig, raw_path: Path) -> Path:
    directory = NORMALIZED_DATA_DIR / dataset.category / dataset.dataset_id
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{raw_path.stem}_extracted.csv"


def run_tourism_irikomi(config: DatasetConfig) -> Path:
    """Run the tourism visitor PDF pipeline."""
    logger.info(
        "Starting tourism PDF pipeline",
        dataset_id=config.dataset_id,
        url=config.url,
    )
    try:
        raw_path = download_if_needed(config)
        sha256 = calculate_sha256(raw_path)

        if is_already_loaded(config, raw_path, sha256):
            normalized_path = _normalized_path(config, raw_path)
            logger.info(
                "Already processed tourism PDF; skipping extraction",
                dataset_id=config.dataset_id,
                normalized_path=str(normalized_path),
            )
        else:
            extracted: pd.DataFrame = extract_tables_from_tourism_irikomi(raw_path)
            normalized_path = _normalized_path(config, raw_path)
            normalized_path_str = str(normalized_path)
            extracted.to_csv(normalized_path_str, index=False)  # pyright: ignore[reportUnknownMemberType]

            mark_loaded(
                config,
                raw_path,
                sha256,
                processed_at=datetime.datetime.now(tz=datetime.UTC),
            )
            logger.info(
                "Tourism PDF pipeline completed",
                dataset_id=config.dataset_id,
                normalized_path=str(normalized_path),
            )
    except (DownloadError, TourismPdfExtractionError) as exc:
        logger.error(
            "Tourism PDF pipeline failed",
            dataset_id=config.dataset_id,
            error=str(exc),
        )
        raise TourismPipelineError(str(exc)) from exc

    return normalized_path

