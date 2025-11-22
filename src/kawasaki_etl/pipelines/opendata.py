from __future__ import annotations

from pathlib import Path
from urllib.parse import urljoin

from kawasaki_etl.core.io import download_file
from kawasaki_etl.models import OpenDataPage
from kawasaki_etl.utils.logger import LoggerProtocol, get_logger

logger: LoggerProtocol = get_logger(__name__)

DEFAULT_BASE_DIR = Path("data/raw/opendata")


def _ensure_absolute(url: str, base: str) -> str:
    return url if url.startswith("http") else urljoin(base, url)


def download_opendata_page(page: OpenDataPage, base_dir: Path = DEFAULT_BASE_DIR) -> list[Path]:
    """指定したオープンデータページに含まれるファイルをすべて保存する."""

    target_dir = base_dir / page.storage_dirname
    target_dir.mkdir(parents=True, exist_ok=True)

    downloaded: list[Path] = []
    for resource in page.resources:
        url = _ensure_absolute(resource.url, page.page_url)
        dest = target_dir / resource.filename

        logger.info(
            "Downloading open data resource",
            page_id=page.identifier,
            url=url,
            destination=str(dest),
            updated_at=resource.updated_at,
            format=resource.file_format,
        )
        download_file(url, dest)
        downloaded.append(dest)

    return downloaded


__all__ = ["download_opendata_page"]
