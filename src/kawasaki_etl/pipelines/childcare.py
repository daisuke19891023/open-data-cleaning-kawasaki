from __future__ import annotations

from typing import TYPE_CHECKING

from kawasaki_etl.configs import CHILDCARE_PAGES_BY_ID
from kawasaki_etl.pipelines.opendata import DEFAULT_BASE_DIR as OPEN_DATA_BASE_DIR
from kawasaki_etl.pipelines.opendata import download_opendata_page
from kawasaki_etl.utils.logger import LoggerProtocol, get_logger

if TYPE_CHECKING:  # pragma: no cover
    from kawasaki_etl.core import DatasetConfig
    from pathlib import Path

logger: LoggerProtocol = get_logger(__name__)

DEFAULT_BASE_DIR = OPEN_DATA_BASE_DIR / "childcare"


class ChildcarePipelineError(Exception):
    """Raised when childcare pipeline fails."""


def run_childcare_opendata(
    config: DatasetConfig,
    base_dir: Path = DEFAULT_BASE_DIR,
) -> list[Path]:
    """Download childcare-related open data resources defined in configs.

    Args:
        config: Dataset configuration with dataset_id matching predefined pages.
        base_dir: Base directory to save downloaded files.

    Returns:
        List of downloaded file paths.

    Raises:
        ChildcarePipelineError: When the dataset_id is not supported.

    """
    page = CHILDCARE_PAGES_BY_ID.get(config.dataset_id)
    if page is None:
        msg = f"Unknown childcare dataset_id: {config.dataset_id}"
        raise ChildcarePipelineError(msg)

    logger.info(
        "Downloading childcare open data",
        dataset_id=config.dataset_id,
        url=config.url,
    )
    return download_opendata_page(page, base_dir=base_dir)
