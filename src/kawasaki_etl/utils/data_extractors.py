"""Utilities for extracting tabular data and text from common open-data formats."""

from __future__ import annotations

# pyright: reportUnknownMemberType=false

from io import BytesIO
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from collections.abc import Callable

import pandas as pd
from pypdf import PdfReader


def extract_csv(
    data: bytes,
    /,
    *,
    encoding: str = "utf-8",
    **kwargs: Any,
) -> pd.DataFrame:
    """Parse CSV bytes into a DataFrame."""
    buffer = BytesIO(data)
    pd_read_csv: Callable[..., pd.DataFrame] = cast(  # type: ignore[assignment]
        "Callable[..., pd.DataFrame]",
        pd.read_csv,
    )
    return pd_read_csv(buffer, encoding=encoding, **kwargs)


def extract_excel(
    data: bytes,
    /,
    *,
    sheet_name: str | int | None = 0,
    **kwargs: Any,
) -> pd.DataFrame:
    """Parse the specified Excel sheet into a DataFrame."""
    buffer = BytesIO(data)
    return cast("pd.DataFrame", pd.read_excel(buffer, sheet_name=sheet_name, **kwargs))


def extract_pdf_text(data: bytes, /) -> str:
    """Extract concatenated text from all PDF pages."""
    reader = PdfReader(BytesIO(data))
    texts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(filter(None, texts))


__all__ = ["extract_csv", "extract_excel", "extract_pdf_text"]
