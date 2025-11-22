from __future__ import annotations

from typing import TYPE_CHECKING

from kawasaki_etl.configs import DISASTER_PREVENTION_PAGES
from kawasaki_etl.pipelines.opendata import DEFAULT_BASE_DIR as OPEN_DATA_BASE_DIR
from kawasaki_etl.pipelines.opendata import download_opendata_page
from kawasaki_etl.utils.logger import LoggerProtocol, get_logger

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterator
    from pathlib import Path

    from kawasaki_etl.models import OpenDataPage

logger: LoggerProtocol = get_logger(__name__)

DEFAULT_BASE_DIR = OPEN_DATA_BASE_DIR / "disaster_prevention"


def download_disaster_prevention_pages(
    base_dir: Path = DEFAULT_BASE_DIR,
) -> list[Path]:
    """防災カテゴリに含まれるオープンデータを一括取得する."""
    logger.info(
        "Downloading disaster prevention open data",
        count=len(DISASTER_PREVENTION_PAGES),
        destination=str(base_dir),
    )
    outputs: list[Path] = []
    for page in DISASTER_PREVENTION_PAGES:
        outputs.extend(download_opendata_page(page, base_dir=base_dir))
    return outputs


def iter_disaster_prevention_pages() -> Iterator[OpenDataPage]:
    """防災カテゴリのページ定義を列挙する."""
    return iter(DISASTER_PREVENTION_PAGES)


__all__ = ["download_disaster_prevention_pages", "iter_disaster_prevention_pages"]
