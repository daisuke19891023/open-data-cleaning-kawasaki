"""Utility modules for the project."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from kawasaki_etl.utils.data_extractors import (
        extract_csv,
        extract_excel,
        extract_pdf_text,
    )
    from kawasaki_etl.utils.data_fetcher import WebDataFetcher, fetch_json

__all__ = [
    "WebDataFetcher",
    "extract_csv",
    "extract_excel",
    "extract_pdf_text",
    "fetch_json",
]

_MODULE_LOOKUP = {
    "WebDataFetcher": ("kawasaki_etl.utils.data_fetcher", "WebDataFetcher"),
    "fetch_json": ("kawasaki_etl.utils.data_fetcher", "fetch_json"),
    "extract_csv": ("kawasaki_etl.utils.data_extractors", "extract_csv"),
    "extract_excel": ("kawasaki_etl.utils.data_extractors", "extract_excel"),
    "extract_pdf_text": ("kawasaki_etl.utils.data_extractors", "extract_pdf_text"),
}


def __getattr__(name: str) -> Any:  # pragma: no cover - thin compatibility shim
    if name not in _MODULE_LOOKUP:
        raise AttributeError(name)
    module_path, attr_name = _MODULE_LOOKUP[name]
    module = import_module(module_path)
    return getattr(module, attr_name)


def __dir__() -> list[str]:  # pragma: no cover - minimal reflection helper
    return sorted(set(__all__))
