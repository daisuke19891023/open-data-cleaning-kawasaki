from __future__ import annotations

import zipfile
from typing import TYPE_CHECKING

import pandas as pd
import pandas.testing as tm
import pytest

from kawasaki_etl.core.normalize import (
    NormalizationError,
    detect_encoding_and_read_csv,
    normalize_column_name,
    normalize_csv,
    normalize_excel,
    normalize_zip_of_csv,
)

if TYPE_CHECKING:
    from pathlib import Path


def _sample_dataframe() -> pd.DataFrame:
    """テスト用のシンプルなDataFrameを生成する."""
    return pd.DataFrame({"ＩＤ": [1, 2], " 名称 ": ["テスト", "サンプル"]})  # noqa: RUF001


def test_detect_encoding_and_read_csv_cp932_success(tmp_path: Path) -> None:
    """CP932のCSVを正常に読み込めること."""
    df = _sample_dataframe()
    csv_path = tmp_path / "sample_cp932.csv"
    df.to_csv(csv_path, index=False, encoding="cp932")  # pyright: ignore[reportUnknownMemberType]

    loaded = detect_encoding_and_read_csv(csv_path)

    tm.assert_frame_equal(loaded, df)  # pyright: ignore[reportUnknownMemberType]


def test_detect_encoding_and_read_csv_raises_with_tried_encodings(
    tmp_path: Path,
) -> None:
    """全てのエンコーディングで失敗した場合に詳細なエラーを返すこと."""
    broken_path = tmp_path / "broken.csv"
    broken_path.write_bytes(b"\x82")

    with pytest.raises(NormalizationError) as excinfo:
        detect_encoding_and_read_csv(broken_path)

    assert "試したエンコーディング" in str(excinfo.value)
    assert str(broken_path) in str(excinfo.value)


def test_normalize_csv_creates_utf8_with_normalized_columns(tmp_path: Path) -> None:
    """normalize_csvがUTF-8のCSVを出力し列名を正規化すること."""
    df = _sample_dataframe()
    raw_path = tmp_path / "raw.csv"
    dest_path = tmp_path / "normalized" / "output.csv"
    df.to_csv(raw_path, index=False, encoding="cp932")  # pyright: ignore[reportUnknownMemberType]

    normalized_df = normalize_csv(raw_path, dest_path)

    assert dest_path.exists()
    loaded = pd.read_csv(dest_path, encoding="utf-8")  # pyright: ignore[reportUnknownMemberType]
    tm.assert_frame_equal(normalized_df, loaded)  # pyright: ignore[reportUnknownMemberType]
    assert list(loaded.columns) == [
        normalize_column_name("ＩＤ"),  # noqa: RUF001
        normalize_column_name(" 名称 "),
    ]


def test_normalize_excel_outputs_per_sheet(tmp_path: Path) -> None:
    """Excelの各シートが個別のUTF-8 CSVに正規化されること."""
    excel_path = tmp_path / "workbook.xlsx"
    df = _sample_dataframe()
    with pd.ExcelWriter(excel_path) as writer:  # pyright: ignore[reportUnknownVariableType]
        df.to_excel(writer, sheet_name="シート1", index=False)  # pyright: ignore[reportUnknownMemberType]
        df.to_excel(writer, sheet_name="Sheet 2", index=False)  # pyright: ignore[reportUnknownMemberType]

    dest_dir = tmp_path / "normalized"
    outputs = normalize_excel(excel_path, dest_dir)

    assert set(outputs.keys()) == {"シート1", "Sheet 2"}
    for sheet, path in outputs.items():
        assert path.exists()
        loaded = pd.read_csv(path, encoding="utf-8")  # pyright: ignore[reportUnknownMemberType]
        assert list(loaded.columns) == [
            normalize_column_name("ＩＤ"),  # noqa: RUF001
            normalize_column_name(" 名称 "),
        ]
        assert len(loaded) == len(df)
        assert sheet in outputs


def test_normalize_zip_of_csv_processes_members(tmp_path: Path) -> None:
    """ZIP内のCSVが重複名を回避しつつ正規化されること."""
    df = _sample_dataframe()
    raw_csv = tmp_path / "raw.csv"
    df.to_csv(raw_csv, index=False, encoding="cp932")  # pyright: ignore[reportUnknownMemberType]

    zip_path = tmp_path / "archive.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.write(raw_csv, arcname="folder/data.csv")

    dest_dir = tmp_path / "normalized"
    outputs = normalize_zip_of_csv(zip_path, dest_dir)

    assert len(outputs) == 1
    output_path = outputs[0]
    assert output_path.exists()
    loaded = pd.read_csv(output_path, encoding="utf-8")  # pyright: ignore[reportUnknownMemberType]
    assert list(loaded.columns) == [
        normalize_column_name("ＩＤ"),  # noqa: RUF001
        normalize_column_name(" 名称 "),
    ]
    tm.assert_frame_equal(  # pyright: ignore[reportUnknownMemberType]
        loaded,
        normalize_csv(raw_csv, dest_dir / "expected.csv"),
    )
