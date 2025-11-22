"""Tests for dataset configuration models and loader."""

from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING

import pytest

from kawasaki_etl.core.models import (
    DatasetConfigError,
    get_dataset_config,
    load_dataset_configs,
)

if TYPE_CHECKING:
    from pathlib import Path


class TestDatasetConfigLoader:
    """Verify YAML configs are loaded into DatasetConfig objects."""

    def test_load_dataset_configs_parses_valid_yaml(self, tmp_path: Path) -> None:
        """Valid YAML yields populated DatasetConfig objects."""
        config_path = tmp_path / "datasets.yml"
        config_path.write_text(
            textwrap.dedent(
                """
                datasets:
                  wifi_counts:
                    category: connectivity
                    url: https://example.com/wifi.csv
                    type: csv
                    key_fields: [spot_id, date]
                    extra:
                      encoding: utf-8
                """,
            ),
            encoding="utf-8",
        )

        configs = load_dataset_configs(config_path)

        wifi_config = configs["wifi_counts"]
        assert wifi_config.dataset_id == "wifi_counts"
        assert wifi_config.category == "connectivity"
        assert wifi_config.url == "https://example.com/wifi.csv"
        assert wifi_config.key_fields == ["spot_id", "date"]
        assert wifi_config.extra == {"encoding": "utf-8"}

    def test_load_dataset_configs_supports_top_level_mapping(
        self,
        tmp_path: Path,
    ) -> None:
        """Top-level mappings without a datasets key are accepted."""
        config_path = tmp_path / "datasets.yml"
        config_path.write_text(
            textwrap.dedent(
                """
                wifi_counts:
                  category: connectivity
                  url: https://example.com/wifi.csv
                  type: csv
                """,
            ),
            encoding="utf-8",
        )

        configs = load_dataset_configs(config_path)

        assert set(configs) == {"wifi_counts"}

    def test_missing_file_raises_error(self, tmp_path: Path) -> None:
        """Missing file surfaces a DatasetConfigError."""
        missing_path = tmp_path / "missing.yml"

        with pytest.raises(DatasetConfigError):
            load_dataset_configs(missing_path)

    def test_invalid_yaml_structure_raises_error(self, tmp_path: Path) -> None:
        """Non-mapping YAML fails with a clear error."""
        config_path = tmp_path / "datasets.yml"
        config_path.write_text("- not-a-mapping", encoding="utf-8")

        with pytest.raises(DatasetConfigError):
            load_dataset_configs(config_path)

    def test_missing_required_fields_raise_error(self, tmp_path: Path) -> None:
        """Required fields are validated."""
        config_path = tmp_path / "datasets.yml"
        config_path.write_text(
            textwrap.dedent(
                """
                datasets:
                  broken:
                    category: connectivity
                """,
            ),
            encoding="utf-8",
        )

        with pytest.raises(DatasetConfigError, match="missing required fields"):
            load_dataset_configs(config_path)

    def test_get_dataset_config_handles_unknown_id(self, tmp_path: Path) -> None:
        """Unknown dataset IDs raise DatasetConfigError."""
        config_path = tmp_path / "datasets.yml"
        config_path.write_text(
            textwrap.dedent(
                """
                datasets:
                  wifi_counts:
                    category: connectivity
                    url: https://example.com/wifi.csv
                    type: csv
                """,
            ),
            encoding="utf-8",
        )

        with pytest.raises(DatasetConfigError, match="not defined"):
            get_dataset_config("unknown", config_path)
