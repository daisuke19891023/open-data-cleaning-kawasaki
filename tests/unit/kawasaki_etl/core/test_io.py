from __future__ import annotations

from typing import TYPE_CHECKING, Self

import pytest

import kawasaki_etl.core.io as io_module
from kawasaki_etl.core.io import (
    DownloadError,
    download_file,
    download_if_needed,
    get_raw_path,
)
from kawasaki_etl.core.models import DatasetConfig

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


class _DummyStream:
    def __init__(self, body: bytes, status_code: int = 200) -> None:
        self.body = body
        self.status_code = status_code

    def iter_bytes(self, chunk_size: int) -> Iterator[bytes]:
        _ = chunk_size
        yield self.body

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False


class _DummyClient:
    def __init__(self, body: bytes, status_code: int = 200) -> None:
        self.body = body
        self.status_code = status_code

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False

    def stream(self, method: str, url: str) -> _DummyStream:
        _ = (method, url)
        return _DummyStream(self.body, self.status_code)


def _patch_http_client(
    monkeypatch: pytest.MonkeyPatch,
    body: bytes,
    status_code: int = 200,
) -> None:
    def dummy_factory(*_args: object, **_kwargs: object) -> _DummyClient:
        return _DummyClient(body, status_code)

    monkeypatch.setattr(io_module.httpx, "Client", dummy_factory)


@pytest.fixture
def sample_dataset() -> DatasetConfig:
    """サンプルのデータセット設定を返す."""
    return DatasetConfig(
        dataset_id="wifi_2020_count",
        category="connectivity",
        url="https://example.com/data/wifi.csv",
        type="csv",
    )


def test_get_raw_path_uses_category_and_dataset(
    sample_dataset: DatasetConfig,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """カテゴリとデータセット ID がパスに反映されることを確認."""
    monkeypatch.setattr(io_module, "RAW_DATA_DIR", tmp_path)

    path = get_raw_path(sample_dataset)

    expected = tmp_path / "connectivity" / "wifi_2020_count" / "wifi.csv"
    assert path == expected


def test_download_file_saves_content(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """HTTP 200 のコンテンツが保存されることを確認."""
    _patch_http_client(monkeypatch, body=b"hello", status_code=200)

    url = "https://example.com/data/wifi.csv"
    dest = tmp_path / "wifi.csv"
    download_file(url, dest)

    assert dest.read_bytes() == b"hello"


def test_download_file_raises_on_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """HTTP エラー時に DownloadError が送出される."""
    _patch_http_client(monkeypatch, body=b"oops", status_code=404)

    url = "https://example.com/data/wifi.csv"
    dest = tmp_path / "wifi.csv"
    with pytest.raises(DownloadError):
        download_file(url, dest)

    assert not dest.exists()


def test_download_if_needed_downloads_when_missing(
    sample_dataset: DatasetConfig,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """未存在の場合はダウンロードが実行される."""
    monkeypatch.setattr(io_module, "RAW_DATA_DIR", tmp_path)
    _patch_http_client(monkeypatch, body=b"data", status_code=200)

    dest_path = download_if_needed(sample_dataset)

    assert dest_path.exists()
    assert dest_path.read_bytes() == b"data"


def test_download_if_needed_skips_existing(
    sample_dataset: DatasetConfig,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """既存ファイルがあれば再ダウンロードされない."""
    monkeypatch.setattr(io_module, "RAW_DATA_DIR", tmp_path)

    def _raise_download(*_args: object, **_kwargs: object) -> _DummyClient:
        raise AssertionError("should not download")

    monkeypatch.setattr(io_module.httpx, "Client", _raise_download)
    existing_path = get_raw_path(sample_dataset)
    existing_path.parent.mkdir(parents=True, exist_ok=True)
    existing_path.write_bytes(b"cached")

    dest_path = download_if_needed(sample_dataset)

    assert dest_path == existing_path
    assert dest_path.read_bytes() == b"cached"
