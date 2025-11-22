from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import yaml


class DatasetConfigError(Exception):
    """Raised when dataset configuration loading fails."""


def _default_key_fields() -> list[str]:
    return []


def _default_extra() -> dict[str, Any]:
    return {}


@dataclass
class DatasetConfig:
    """Dataset configuration loaded from YAML."""

    dataset_id: str
    category: str
    url: str
    type: str
    parser: str | None = None
    table: str | None = None
    key_fields: list[str] = field(default_factory=_default_key_fields)
    snapshot_date: str | None = None
    extra: dict[str, Any] = field(default_factory=_default_extra)

    @classmethod
    def from_mapping(cls, dataset_id: str, data: Mapping[str, Any]) -> DatasetConfig:
        """Create a DatasetConfig from a mapping loaded from YAML."""
        required_fields = ["category", "url", "type"]
        missing = [field for field in required_fields if data.get(field) is None]
        if missing:
            msg = (
                f"Dataset '{dataset_id}' is missing required fields: "
                f"{', '.join(sorted(missing))}"
            )
            raise DatasetConfigError(msg)

        key_fields_candidate = data.get("key_fields")
        key_fields_data: list[Any]
        if key_fields_candidate is None:
            key_fields_data = []
        elif isinstance(key_fields_candidate, list):
            key_fields_data = cast("list[Any]", key_fields_candidate)
        else:
            msg = f"Dataset '{dataset_id}' has invalid key_fields (must be a list)"
            raise DatasetConfigError(msg)
        key_fields = [str(field) for field in key_fields_data]

        extra_candidate = data.get("extra")
        if extra_candidate is None:
            extra_candidate = {}
        if not isinstance(extra_candidate, Mapping):
            msg = (
                f"Dataset '{dataset_id}' has invalid extra section (must be a mapping)"
            )
            raise DatasetConfigError(msg)
        extra_mapping = cast("Mapping[str, Any]", extra_candidate)
        extra = {str(key): value for key, value in extra_mapping.items()}

        snapshot_date_raw = data.get("snapshot_date")
        if snapshot_date_raw is not None and not isinstance(
            snapshot_date_raw,
            (str, int, float),
        ):
            msg = (
                f"Dataset '{dataset_id}' has invalid snapshot_date "
                "(must be string or number)"
            )
            raise DatasetConfigError(msg)

        return cls(
            dataset_id=dataset_id,
            category=str(data["category"]),
            url=str(data["url"]),
            type=str(data["type"]),
            parser=str(data["parser"]) if data.get("parser") is not None else None,
            table=str(data["table"]) if data.get("table") is not None else None,
            key_fields=key_fields,
            snapshot_date=(
                str(snapshot_date_raw) if snapshot_date_raw is not None else None
            ),
            extra=extra,
        )


def _extract_dataset_entries(raw_data: object | None) -> Mapping[str, Any]:
    if raw_data is None:
        return {}

    if not isinstance(raw_data, Mapping):
        msg = "datasets.yml must contain a mapping at the top level"
        raise DatasetConfigError(msg)

    mapping_data = cast("Mapping[str, Any]", raw_data)
    dataset_entries = mapping_data.get("datasets", mapping_data)
    if dataset_entries is None:
        return {}

    if not isinstance(dataset_entries, Mapping):
        msg = "The 'datasets' section must map dataset_id to configuration objects"
        raise DatasetConfigError(msg)

    return cast("Mapping[str, Any]", dataset_entries)


def load_dataset_configs(
    config_path: str | Path = Path("configs/datasets.yml"),
) -> dict[str, DatasetConfig]:
    """Load dataset configurations from a YAML file."""
    path = Path(config_path)
    if not path.exists():
        msg = f"Dataset configuration file not found: {path}"
        raise DatasetConfigError(msg)

    try:
        raw_yaml = path.read_text(encoding="utf-8")
    except OSError as exc:  # pragma: no cover - extremely rare filesystem errors
        msg = f"Failed to read dataset configuration: {path}"
        raise DatasetConfigError(msg) from exc

    try:
        loaded = yaml.safe_load(raw_yaml)
    except yaml.YAMLError as exc:
        msg = f"Failed to parse YAML in {path}: {exc}"
        raise DatasetConfigError(msg) from exc

    parsed_data: Mapping[str, Any] | None
    if loaded is None:
        parsed_data = None
    elif isinstance(loaded, Mapping):
        parsed_data = cast("Mapping[str, Any]", loaded)
    else:
        msg = "datasets.yml must contain a mapping at the top level"
        raise DatasetConfigError(msg)

    dataset_entries = _extract_dataset_entries(parsed_data)

    configs: dict[str, DatasetConfig] = {}
    for dataset_id, dataset_data in dataset_entries.items():
        configs[str(dataset_id)] = DatasetConfig.from_mapping(
            str(dataset_id),
            dataset_data,
        )

    return configs


def get_dataset_config(
    dataset_id: str,
    config_path: str | Path = Path("configs/datasets.yml"),
) -> DatasetConfig:
    """Get a single dataset configuration by ID."""
    configs = load_dataset_configs(config_path)
    try:
        return configs[dataset_id]
    except KeyError as exc:
        msg = f"Dataset id '{dataset_id}' is not defined in {Path(config_path)}"
        raise DatasetConfigError(msg) from exc
