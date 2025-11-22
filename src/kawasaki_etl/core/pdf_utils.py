from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
from kawasaki_etl.utils.logger import LoggerProtocol, get_logger

if TYPE_CHECKING:
    from pathlib import Path

logger: LoggerProtocol = get_logger(__name__)


class TourismPdfExtractionError(Exception):
    """Raised when tourism PDF extraction fails."""


def extract_tables_from_tourism_irikomi(pdf_path: Path) -> pd.DataFrame:
    """Extract tabular data from the tourism visitor PDF.

    現時点では PDF 解析ライブラリは導入せず、モック/簡易実装で形だけを整える。
    将来的には camelot や tabula などのテーブル抽出ライブラリに差し替える予定。
    """
    if not pdf_path.exists():
        msg = f"PDF が見つかりません: {pdf_path}"
        raise TourismPdfExtractionError(msg)

    mock_csv = pdf_path.with_suffix(".csv")
    if mock_csv.exists():
        try:
            df = pd.read_csv(mock_csv)  # pyright: ignore[reportUnknownMemberType]
        except Exception as exc:  # pragma: no cover - unexpected CSV failure
            logger.warning(
                "Failed to load mock CSV; falling back to placeholder",
                pdf_path=str(pdf_path),
                mock_csv=str(mock_csv),
                error=str(exc),
            )
        else:
            logger.info(
                "Loaded mock CSV for tourism PDF extraction",
                pdf_path=str(pdf_path),
                mock_csv=str(mock_csv),
            )
            return df

    logger.warning(
        "観光入込客数 PDF のパースは未実装です。",
        hint="今後 camelot / tabula-py 等でテーブル抽出を実装する予定です。",
    )
    return pd.DataFrame(
        {
            "message": [
                "PDF パーサは未実装です。camelot / tabula-py などで拡張予定。",
            ],
            "pdf_path": [str(pdf_path)],
        },
    )

