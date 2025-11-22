from __future__ import annotations

import re
import tempfile
import unicodedata
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import pandas as pd

from kawasaki_etl.utils.logger import LoggerProtocol, get_logger

DataFrame = pd.DataFrame


class NormalizationError(Exception):
    """Raised when file normalization fails."""


COMMON_ENCODINGS: tuple[str, ...] = (
    "utf-8",
    "utf-8-sig",
    "cp932",
    "shift_jis",
    "euc_jp",
)

logger: LoggerProtocol = get_logger(__name__)


if TYPE_CHECKING:
    from collections.abc import Sequence


def normalize_column_name(name: str) -> str:
    """Normalize a column name by trimming spaces and converting to half-width.

    Args:
        name: Original column name.

    Returns:
        Normalized column name.

    """
    normalized = unicodedata.normalize("NFKC", name).strip()
    return re.sub(r"\s+", " ", normalized)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the DataFrame with normalized column names."""
    copy = df.copy()
    normalized_columns: list[str] = [
        normalize_column_name(str(col))
        for col in cast("list[object]", copy.columns.to_list())
    ]
    copy.columns = normalized_columns
    return copy


def detect_encoding_and_read_csv(
    path: Path,
    *,
    encodings: Sequence[str] | None = None,
    **kwargs: Any,
) -> pd.DataFrame:
    """Read a CSV file by trying multiple encodings.

    Args:
        path: Path to the CSV file.
        encodings: Optional custom encoding candidates.
        **kwargs: Additional arguments forwarded to ``pandas.read_csv``.

    Returns:
        Loaded DataFrame.

    Raises:
        NormalizationError: If decoding fails for all encodings.

    """
    tried = list(encodings) if encodings else list(COMMON_ENCODINGS)
    last_error: Exception | None = None

    for encoding in tried:
        try:
            if "iterator" in kwargs or "chunksize" in kwargs:
                msg = "iterator/chunksize options are not supported for normalization"
                raise NormalizationError(msg)

            data: DataFrame = pd.read_csv(  # pyright: ignore[reportUnknownMemberType]
                path,
                encoding=encoding,
                iterator=False,
                chunksize=None,
                **kwargs,
            )
        except UnicodeDecodeError as exc:
            last_error = exc
            logger.debug(
                "Failed to decode CSV with encoding",
                path=str(path),
                encoding=encoding,
            )
            continue
        else:
            return data

    msg = (
        "CSV の読み込みに失敗しました: "
        f"{path} (試したエンコーディング: {', '.join(tried)})"
    )
    raise NormalizationError(msg) from last_error


def normalize_csv(path: Path, dest: Path) -> pd.DataFrame:
    """Normalize a CSV file to UTF-8 with cleaned column names."""
    df = detect_encoding_and_read_csv(path)
    df = normalize_columns(df)
    dest.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dest, index=False, encoding="utf-8")  # pyright: ignore[reportUnknownMemberType]
    logger.info(
        "Normalized CSV written",
        source=str(path),
        dest=str(dest),
        rows=len(df),
    )
    return df


def _sanitize_sheet_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", name)


def normalize_excel(path: Path, dest_dir: Path) -> dict[str, Path]:
    """Normalize all sheets in an Excel workbook to UTF-8 CSV files."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    sheets = cast(
        "dict[str, DataFrame]",
        pd.read_excel(path, sheet_name=None),  # pyright: ignore[reportUnknownMemberType]
    )
    output_paths: dict[str, Path] = {}

    for sheet_name, df in sheets.items():
        normalized_df = normalize_columns(df)
        safe_sheet = _sanitize_sheet_name(str(sheet_name)) or "sheet"
        dest = dest_dir / f"{path.stem}_{safe_sheet}.csv"
        normalized_df.to_csv(  # pyright: ignore[reportUnknownMemberType]
            dest,
            index=False,
            encoding="utf-8",
        )
        output_paths[str(sheet_name)] = dest
        logger.info(
            "Normalized Excel sheet",
            sheet=str(sheet_name),
            source=str(path),
            dest=str(dest),
        )

    return output_paths


def normalize_zip_of_csv(zip_path: Path, dest_dir: Path) -> list[Path]:
    """Normalize all CSV files contained in a ZIP archive."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    output_paths: list[Path] = []
    used_names: set[Path] = set()

    with zipfile.ZipFile(zip_path) as archive, tempfile.TemporaryDirectory() as tmpdir:
        for info in archive.infolist():
            if info.is_dir():
                continue
            if not info.filename.lower().endswith(".csv"):
                continue

            member_path = Path(info.filename)
            member_name = member_path.name
            raw_tmp = Path(tmpdir) / member_name
            with archive.open(info) as source, raw_tmp.open("wb") as tmp_file:
                tmp_file.write(source.read())

            df = detect_encoding_and_read_csv(raw_tmp)
            df = normalize_columns(df)

            member_stem = member_path.stem
            base_dest = dest_dir / f"{zip_path.stem}_{member_stem}.csv"
            dest = base_dest
            counter = 1
            while dest in used_names or dest.exists():
                dest = dest_dir / f"{zip_path.stem}_{member_stem}_{counter}.csv"
                counter += 1

            df.to_csv(  # pyright: ignore[reportUnknownMemberType]
                dest,
                index=False,
                encoding="utf-8",
            )
            used_names.add(dest)
            output_paths.append(dest)
            logger.info(
                "Normalized CSV from ZIP",
                source=str(zip_path),
                member=info.filename,
                dest=str(dest),
            )

    return output_paths
