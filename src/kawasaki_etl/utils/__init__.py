"""Utility modules for the project."""

__all__ = [
    "WebDataFetcher",
    "extract_csv",
    "extract_excel",
    "extract_pdf_text",
    "fetch_json",
]


def __getattr__(name: str) -> object:  # type: ignore[explicit-override]
    if name in {"WebDataFetcher", "fetch_json"}:
        from kawasaki_etl.utils import data_fetcher

        return getattr(data_fetcher, name)
    if name in {"extract_csv", "extract_excel", "extract_pdf_text"}:
        from kawasaki_etl.utils import data_extractors

        return getattr(data_extractors, name)
    raise AttributeError(name)
