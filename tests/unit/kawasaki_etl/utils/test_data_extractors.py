# ruff: noqa:D103

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import pandas as pd

if TYPE_CHECKING:
    from pathlib import Path

from kawasaki_etl.utils import extract_csv, extract_excel, extract_pdf_text


def test_extract_csv_returns_dataframe() -> None:
    csv_bytes = b"col1,col2\n1,2\n3,4"

    df: pd.DataFrame = extract_csv(csv_bytes)

    result = cast(
        "dict[str, list[int]]",
        df.to_dict(orient="list"),  # pyright: ignore[reportUnknownMemberType]
    )

    assert result == {"col1": [1, 3], "col2": [2, 4]}


def test_extract_excel_reads_sheet(tmp_path: Path) -> None:
    frame: pd.DataFrame = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    excel_path = tmp_path / "data.xlsx"
    frame.to_excel(excel_path, index=False)  # pyright: ignore[reportUnknownMemberType]

    df: pd.DataFrame = extract_excel(excel_path.read_bytes())
    result = cast(
        "dict[str, list[int | str]]",
        df.to_dict(orient="list"),  # pyright: ignore[reportUnknownMemberType]
    )

    assert result == {"a": [1, 2], "b": ["x", "y"]}


def test_extract_pdf_text_reads_simple_pdf() -> None:
    header = b"%PDF-1.4\n"
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n",
        b"4 0 obj\n<< /Length 44 >>\nstream\n"
        b"BT /F1 24 Tf 72 100 Td (Hello, PDF!) Tj ET\nendstream\nendobj\n",
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]

    position = len(header)
    offsets: list[int] = []
    for obj in objects:
        offsets.append(position)
        position += len(obj)

    xref_entries: list[bytes] = [f"{pos:010d} 00000 n \n".encode() for pos in offsets]
    xref = b"xref\n0 6\n0000000000 65535 f \n" + b"".join(xref_entries)
    trailer = b"trailer\n<< /Root 1 0 R /Size 6 >>\n"
    startxref = len(header + b"".join(objects))
    pdf_content = (
        header
        + b"".join(objects)
        + xref
        + trailer
        + b"startxref\n"
        + str(startxref).encode()
        + b"\n%%EOF"
    )

    text: str = extract_pdf_text(pdf_content)

    assert "Hello, PDF!" in text
