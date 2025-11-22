"""Pipeline implementations for individual datasets."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

__all__ = ["download_opendata_page", "run_tourism_irikomi", "run_wifi_count"]


def __getattr__(name: str) -> Any:  # pragma: no cover - thin lazy import wrapper
    if name == "run_tourism_irikomi":
        from kawasaki_etl.pipelines.tourism import run_tourism_irikomi

        return run_tourism_irikomi
    if name == "run_wifi_count":
        from kawasaki_etl.pipelines.wifi import run_wifi_count

        return run_wifi_count
    if name == "download_opendata_page":
        from kawasaki_etl.pipelines.opendata import download_opendata_page

        return download_opendata_page
    message = f"module {__name__!s} has no attribute {name!s}"
    raise AttributeError(message)


if TYPE_CHECKING:  # pragma: no cover
    from kawasaki_etl.pipelines.opendata import download_opendata_page
    from kawasaki_etl.pipelines.tourism import run_tourism_irikomi
    from kawasaki_etl.pipelines.wifi import run_wifi_count
