from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import httpx

from kawasaki_etl.utils.logger import LoggerProtocol, get_logger

if TYPE_CHECKING:
    from kawasaki_etl.core.models import DatasetConfig

RAW_DATA_DIR = Path("data/raw")
CHUNK_SIZE = 1024 * 64
HTTP_ERROR_THRESHOLD = 400

TimeoutErrorType: type[Exception] = getattr(httpx, "TimeoutException", Exception)
RequestErrorType: type[Exception] = getattr(httpx, "RequestError", Exception)
HTTPErrorType: type[Exception] = getattr(httpx, "HTTPError", Exception)

logger: LoggerProtocol = get_logger(__name__)


class DownloadError(Exception):
    """Raised when downloading a dataset fails."""


def _extract_filename(url: str) -> str:
    parsed = urlparse(url)
    filename = Path(parsed.path).name
    if not filename:
        msg = "URL からファイル名を特定できませんでした"
        raise DownloadError(msg)
    return filename


def get_raw_path(dataset: DatasetConfig) -> Path:
    """Return the expected raw file path for a dataset."""
    filename = _extract_filename(dataset.url)
    return RAW_DATA_DIR / dataset.category / dataset.dataset_id / filename


def download_file(url: str, dest_path: Path) -> None:
    """Download a file via HTTP(S) to the specified destination."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with httpx.Client(
            timeout=30.0, follow_redirects=True,
        ) as client, client.stream("GET", url) as response:
            if response.status_code >= HTTP_ERROR_THRESHOLD:
                msg = f"HTTP {response.status_code}"
                raise DownloadError(msg)

            with dest_path.open("wb") as dest_file:
                for chunk in response.iter_bytes(chunk_size=CHUNK_SIZE):
                    dest_file.write(chunk)
    except HTTPErrorType as exc:
        if isinstance(exc, TimeoutErrorType):
            logger.error(
                "Download timed out", url=url, dest=str(dest_path), error=str(exc),
            )
            msg = "ダウンロードがタイムアウトしました"
        elif isinstance(exc, RequestErrorType):
            logger.error(
                "Download request failed",
                url=url,
                dest=str(dest_path),
                error=str(exc),
            )
            msg = "ネットワークエラーによりダウンロードに失敗しました"
        else:
            logger.error(
                "HTTP error during download",
                url=url,
                dest=str(dest_path),
                error=str(exc),
            )
            msg = "HTTP エラーによりダウンロードに失敗しました"
        raise DownloadError(msg) from exc
    except OSError as exc:
        logger.error(
            "Failed to write downloaded file",
            url=url,
            dest=str(dest_path),
            error=str(exc),
        )
        msg = "ファイルの保存に失敗しました"
        raise DownloadError(msg) from exc


def download_if_needed(dataset: DatasetConfig) -> Path:
    """Download the dataset if the raw file is not already present."""
    dest_path = get_raw_path(dataset)
    if dest_path.exists() and dest_path.stat().st_size > 0:
        logger.info(
            "Raw file already exists; skipping download",
            path=str(dest_path),
            size=dest_path.stat().st_size,
        )
        return dest_path

    logger.info(
        "Starting dataset download",
        dataset_id=dataset.dataset_id,
        url=dataset.url,
        dest=str(dest_path),
    )

    download_file(dataset.url, dest_path)

    logger.info(
        "Download completed",
        path=str(dest_path),
        size=dest_path.stat().st_size,
    )
    return dest_path
