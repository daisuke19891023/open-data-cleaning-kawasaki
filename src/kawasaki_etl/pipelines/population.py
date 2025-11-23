from __future__ import annotations

from typing import TYPE_CHECKING

from kawasaki_etl.configs.population import POPULATION_2025_PAGES
from kawasaki_etl.pipelines.opendata import DEFAULT_BASE_DIR as OPEN_DATA_BASE_DIR
from kawasaki_etl.pipelines.opendata import download_opendata_page
from kawasaki_etl.utils.logger import LoggerProtocol, get_logger

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterator
    from pathlib import Path

    from kawasaki_etl.models import OpenDataPage

logger: LoggerProtocol = get_logger(__name__)

DEFAULT_BASE_DIR = OPEN_DATA_BASE_DIR / "population_2025"


def download_population_2025_pages(base_dir: Path = DEFAULT_BASE_DIR) -> list[Path]:
    """人口・世帯カテゴリ(2025年度)のオープンデータを一括取得する."""
    logger.info(
        "Downloading 2025 population open data",
        count=len(POPULATION_2025_PAGES),
        destination=str(base_dir),
    )
    outputs: list[Path] = []
    for page in POPULATION_2025_PAGES:
        outputs.extend(download_opendata_page(page, base_dir=base_dir))
    return outputs


def iter_population_2025_pages() -> Iterator[OpenDataPage]:
    """人口・世帯カテゴリ(2025年度)のページ定義を列挙する."""
    return iter(POPULATION_2025_PAGES)


__all__ = ["download_population_2025_pages", "iter_population_2025_pages"]
