from __future__ import annotations

import datetime
import json
import os
from pathlib import Path

import pytest

from kawasaki_etl.core import meta_store
from kawasaki_etl.core.meta_store import (
    calculate_sha256,
    get_meta_path,
    is_already_loaded,
    mark_loaded,
)
from kawasaki_etl.core.models import DatasetConfig


@pytest.fixture
def sample_dataset() -> DatasetConfig:
    """Return a sample DatasetConfig for testing."""
    return DatasetConfig(
        dataset_id="wifi_2020_count",
        category="connectivity",
        url="https://example.com/data/wifi.csv",
        type="csv",
    )


def test_get_meta_path_mirrors_raw_structure(
    sample_dataset: DatasetConfig,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Meta files mirror the raw hierarchy and add a .json suffix."""
    monkeypatch.setattr(meta_store, "META_DATA_DIR", tmp_path)

    raw_path = Path("/anywhere/data/raw/connectivity/wifi_2020_count/wifi.csv")
    path = get_meta_path(sample_dataset, raw_path)

    assert path == tmp_path / "connectivity" / "wifi_2020_count" / "wifi.csv.json"


def test_calculate_sha256_returns_digest(tmp_path: Path) -> None:
    """Ensure SHA256 calculation matches the expected digest."""
    target = tmp_path / "file.bin"
    target.write_bytes(b"hello world")

    digest = calculate_sha256(target)

    assert digest == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"


def test_mark_loaded_and_is_already_loaded(
    sample_dataset: DatasetConfig,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Verify metadata writing and idempotency checks work as expected."""
    monkeypatch.setattr(meta_store, "META_DATA_DIR", tmp_path / "meta")

    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    raw_path = raw_dir / "wifi.csv"
    raw_path.write_text("dummy", encoding="utf-8")
    mtime = datetime.datetime(2024, 1, 1, tzinfo=datetime.UTC).timestamp()
    os.utime(raw_path, (mtime, mtime))

    sha256 = "abc123"
    processed_at = datetime.datetime(2024, 1, 2, 3, 4, 5, tzinfo=datetime.UTC)

    meta_path = mark_loaded(sample_dataset, raw_path, sha256, processed_at)

    record = json.loads(meta_path.read_text(encoding="utf-8"))
    assert record["dataset_id"] == sample_dataset.dataset_id
    assert record["category"] == sample_dataset.category
    assert record["source_url"] == sample_dataset.url
    assert record["raw_path"] == str(raw_path)
    assert record["sha256"] == sha256
    assert record["downloaded_at"].startswith("2024-01-01T00:00:00+00:00")
    assert record["processed_at"].startswith("2024-01-02T03:04:05+00:00")

    assert is_already_loaded(sample_dataset, raw_path, sha256) is True
    assert is_already_loaded(sample_dataset, raw_path, "different") is False


def test_is_already_loaded_returns_false_for_corrupted_meta(
    sample_dataset: DatasetConfig,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Corrupted metadata should not mark the dataset as processed."""
    monkeypatch.setattr(meta_store, "META_DATA_DIR", tmp_path / "meta")

    raw_path = tmp_path / "wifi.csv"
    raw_path.write_text("data", encoding="utf-8")
    meta_path = get_meta_path(sample_dataset, raw_path)
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text("{not-json", encoding="utf-8")

    assert is_already_loaded(sample_dataset, raw_path, "ignored") is False
