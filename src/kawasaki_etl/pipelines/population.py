from __future__ import annotations

from typing import TYPE_CHECKING

from kawasaki_etl.configs.population import (
    POPULATION_2022_PAGES,
    POPULATION_2023_PAGES,
    POPULATION_2024_PAGES,
    POPULATION_2025_PAGES,
)
from kawasaki_etl.pipelines.opendata import DEFAULT_BASE_DIR as OPEN_DATA_BASE_DIR
from kawasaki_etl.pipelines.opendata import download_opendata_page
from kawasaki_etl.utils.logger import LoggerProtocol, get_logger

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterator
    from pathlib import Path

    from kawasaki_etl.models import OpenDataPage

logger: LoggerProtocol = get_logger(__name__)

DEFAULT_BASE_DIR_2022 = OPEN_DATA_BASE_DIR / "population_2022"
DEFAULT_BASE_DIR_2023 = OPEN_DATA_BASE_DIR / "population_2023"
DEFAULT_BASE_DIR_2024 = OPEN_DATA_BASE_DIR / "population_2024"
DEFAULT_BASE_DIR_2025 = OPEN_DATA_BASE_DIR / "population_2025"


def _download_population_pages(
    *,
    pages: tuple[OpenDataPage, ...],
    base_dir: Path,
    year_label: str,
) -> list[Path]:
    logger.info(
        "Downloading population open data",
        year=year_label,
        count=len(pages),
        destination=str(base_dir),
    )
    outputs: list[Path] = []
    for page in pages:
        outputs.extend(download_opendata_page(page, base_dir=base_dir))
    return outputs


def download_population_2024_pages(
    base_dir: Path = DEFAULT_BASE_DIR_2024,
) -> list[Path]:
    """人口・世帯カテゴリ(2024年度)のオープンデータを一括取得する."""
    return _download_population_pages(
        pages=POPULATION_2024_PAGES,
        base_dir=base_dir,
        year_label="2024",
    )


def download_population_2023_pages(
    base_dir: Path = DEFAULT_BASE_DIR_2023,
) -> list[Path]:
    """人口・世帯カテゴリ(2023年度)のオープンデータを一括取得する."""
    return _download_population_pages(
        pages=POPULATION_2023_PAGES,
        base_dir=base_dir,
        year_label="2023",
    )


def download_population_2022_pages(
    base_dir: Path = DEFAULT_BASE_DIR_2022,
) -> list[Path]:
    """人口・世帯カテゴリ(2022年度)のオープンデータを一括取得する."""
    return _download_population_pages(
        pages=POPULATION_2022_PAGES,
        base_dir=base_dir,
        year_label="2022",
    )


def download_population_2025_pages(
    base_dir: Path = DEFAULT_BASE_DIR_2025,
) -> list[Path]:
    """人口・世帯カテゴリ(2025年度)のオープンデータを一括取得する."""
    return _download_population_pages(
        pages=POPULATION_2025_PAGES,
        base_dir=base_dir,
        year_label="2025",
    )


def iter_population_2024_pages() -> Iterator[OpenDataPage]:
    """人口・世帯カテゴリ(2024年度)のページ定義を列挙する."""
    return iter(POPULATION_2024_PAGES)


def iter_population_2023_pages() -> Iterator[OpenDataPage]:
    """人口・世帯カテゴリ(2023年度)のページ定義を列挙する."""
    return iter(POPULATION_2023_PAGES)


def iter_population_2022_pages() -> Iterator[OpenDataPage]:
    """人口・世帯カテゴリ(2022年度)のページ定義を列挙する."""
    return iter(POPULATION_2022_PAGES)


def iter_population_2025_pages() -> Iterator[OpenDataPage]:
    """人口・世帯カテゴリ(2025年度)のページ定義を列挙する."""
    return iter(POPULATION_2025_PAGES)


__all__ = [
    "download_population_2022_pages",
    "download_population_2023_pages",
    "download_population_2024_pages",
    "download_population_2025_pages",
    "iter_population_2022_pages",
    "iter_population_2023_pages",
    "iter_population_2024_pages",
    "iter_population_2025_pages",
]
