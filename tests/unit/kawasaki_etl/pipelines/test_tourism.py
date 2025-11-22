from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from kawasaki_etl.core.models import DatasetConfig
from kawasaki_etl.core.pdf_utils import extract_tables_from_tourism_irikomi
from kawasaki_etl.pipelines import tourism


def test_extract_tables_returns_placeholder_when_no_mock(tmp_path: Path) -> None:
    """Ensure placeholder DataFrame is returned when no mock CSV exists."""
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_text("dummy pdf content", encoding="utf-8")

    df = extract_tables_from_tourism_irikomi(pdf_path)

    assert "message" in df.columns
    assert any(df["message"].str.contains("未実装", na=False))


def test_run_tourism_irikomi_saves_csv(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """Ensure extracted data is saved as CSV."""
    dataset = DatasetConfig(
        dataset_id="tourism_r05_irikomi",
        category="tourism",
        url="https://example.com/tourism.pdf",
        type="pdf",
        parser="tourism_irikomi_pdf",
    )

    raw_pdf = tmp_path / "tourism.pdf"
    raw_pdf.write_text("dummy pdf content", encoding="utf-8")

    normalized_dir = tmp_path / "normalized"
    meta_path = tmp_path / "meta.json"

    sample_df = pd.DataFrame({"col": [1, 2, 3]})

    def _download_if_needed(_: DatasetConfig) -> Path:
        return raw_pdf

    def _calculate_sha256(_: Path) -> str:
        return "dummyhash"

    def _is_already_loaded(*_: object, **__: object) -> bool:
        return False

    def _extract(_: Path) -> pd.DataFrame:
        return sample_df

    def _mark_loaded(*_: object, **__: object) -> Path:
        return meta_path

    monkeypatch.setattr(tourism, "NORMALIZED_DATA_DIR", normalized_dir)
    monkeypatch.setattr(tourism, "download_if_needed", _download_if_needed)
    monkeypatch.setattr(tourism, "calculate_sha256", _calculate_sha256)
    monkeypatch.setattr(tourism, "is_already_loaded", _is_already_loaded)
    monkeypatch.setattr(tourism, "extract_tables_from_tourism_irikomi", _extract)
    monkeypatch.setattr(tourism, "mark_loaded", _mark_loaded)

    normalized_path = tourism.run_tourism_irikomi(dataset)

    assert normalized_path.exists()
    loaded_df = pd.read_csv(normalized_path)  # pyright: ignore[reportUnknownMemberType]
    assert_frame_equal(loaded_df, sample_df)
