from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from kawasaki_etl.utils.logger import LoggerProtocol, get_logger

if TYPE_CHECKING:
    from kawasaki_etl.core.models import DatasetConfig

META_DATA_DIR = Path("data/meta")

logger: LoggerProtocol = get_logger(__name__)


class MetaStoreError(Exception):
    """Raised when reading or writing metadata fails."""


def get_meta_path(dataset: DatasetConfig, raw_path: Path) -> Path:
    """Return the metadata path for a given raw file.

    The path structure mirrors ``data/raw/<category>/<dataset_id>/`` and appends
    ``.json`` to the raw filename.
    """
    return (
        META_DATA_DIR
        / dataset.category
        / dataset.dataset_id
        / f"{raw_path.name}.json"
    )


def calculate_sha256(path: Path, chunk_size: int = 65536) -> str:
    """Calculate the SHA256 hash of a file."""
    digest = hashlib.sha256()
    try:
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(chunk_size), b""):
                digest.update(chunk)
    except OSError as exc:  # pragma: no cover - unexpected filesystem failure
        msg = f"Failed to read file for hashing: {path}"
        raise MetaStoreError(msg) from exc

    return digest.hexdigest()


def _ensure_isoformat(value: Any) -> str:
    if isinstance(value, datetime.datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=datetime.UTC)
        else:
            value = value.astimezone(datetime.UTC)
        return value.isoformat()
    return str(value)


def mark_loaded(
    dataset: DatasetConfig, raw_path: Path, sha256: str, processed_at: Any,
) -> Path:
    """Persist metadata indicating that a dataset file has been processed."""
    meta_path = get_meta_path(dataset, raw_path)
    meta_path.parent.mkdir(parents=True, exist_ok=True)

    downloaded_at = datetime.datetime.fromtimestamp(
        raw_path.stat().st_mtime, tz=datetime.UTC,
    ).isoformat()

    record = {
        "dataset_id": dataset.dataset_id,
        "category": dataset.category,
        "source_url": dataset.url,
        "raw_path": str(raw_path),
        "sha256": sha256,
        "downloaded_at": downloaded_at,
        "processed_at": _ensure_isoformat(processed_at),
    }

    try:
        meta_json = json.dumps(record, ensure_ascii=False, indent=2)
        meta_path.write_text(meta_json, encoding="utf-8")
    except OSError as exc:  # pragma: no cover - unexpected filesystem failure
        logger.error("Failed to write metadata", path=str(meta_path), error=str(exc))
        msg = f"Failed to write metadata file: {meta_path}"
        raise MetaStoreError(msg) from exc

    logger.info(
        "Saved metadata for dataset",
        dataset_id=dataset.dataset_id,
        meta_path=str(meta_path),
        sha256=sha256,
    )
    return meta_path


def _load_meta(meta_path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        logger.warning(
            "Metadata file is corrupted; reprocessing required",
            path=str(meta_path),
            error=str(exc),
        )
        return None
    except OSError as exc:  # pragma: no cover - unexpected filesystem failure
        logger.error("Failed to read metadata", path=str(meta_path), error=str(exc))
        msg = f"Failed to read metadata file: {meta_path}"
        raise MetaStoreError(msg) from exc


def is_already_loaded(dataset: DatasetConfig, raw_path: Path, sha256: str) -> bool:
    """Check whether the file has already been processed with the same content."""
    meta_path = get_meta_path(dataset, raw_path)
    meta = _load_meta(meta_path)
    if meta is None:
        return False

    matches_dataset = meta.get("dataset_id") == dataset.dataset_id
    matches_category = meta.get("category") == dataset.category
    matches_url = meta.get("source_url") == dataset.url
    matches_path = meta.get("raw_path") == str(raw_path)
    matches_sha = meta.get("sha256") == sha256

    if all([matches_dataset, matches_category, matches_url, matches_path, matches_sha]):
        logger.info(
            "Dataset already processed; skipping",
            dataset_id=dataset.dataset_id,
            meta_path=str(meta_path),
        )
        return True

    logger.info(
        "Dataset needs processing",
        dataset_id=dataset.dataset_id,
        meta_path=str(meta_path),
        matches_dataset=matches_dataset,
        matches_category=matches_category,
        matches_url=matches_url,
        matches_path=matches_path,
        matches_sha=matches_sha,
    )
    return False

