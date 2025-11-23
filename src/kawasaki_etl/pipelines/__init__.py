"""Pipeline implementations for individual datasets."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

__all__ = [
    "download_disaster_prevention_pages",
    "download_opendata_page",
    "download_population_2024_pages",
    "download_population_2025_pages",
    "iter_disaster_prevention_pages",
    "iter_population_2024_pages",
    "iter_population_2025_pages",
    "run_childcare_opendata",
    "run_tourism_irikomi",
    "run_wifi_count",
]


def __getattr__(name: str) -> Any:  # pragma: no cover - thin lazy import wrapper
    mapping = {
        "run_tourism_irikomi": (
            "kawasaki_etl.pipelines.tourism",
            "run_tourism_irikomi",
        ),
        "run_wifi_count": ("kawasaki_etl.pipelines.wifi", "run_wifi_count"),
        "download_disaster_prevention_pages": (
            "kawasaki_etl.pipelines.disaster",
            "download_disaster_prevention_pages",
        ),
        "iter_disaster_prevention_pages": (
            "kawasaki_etl.pipelines.disaster",
            "iter_disaster_prevention_pages",
        ),
        "download_population_2024_pages": (
            "kawasaki_etl.pipelines.population",
            "download_population_2024_pages",
        ),
        "download_population_2025_pages": (
            "kawasaki_etl.pipelines.population",
            "download_population_2025_pages",
        ),
        "iter_population_2024_pages": (
            "kawasaki_etl.pipelines.population",
            "iter_population_2024_pages",
        ),
        "iter_population_2025_pages": (
            "kawasaki_etl.pipelines.population",
            "iter_population_2025_pages",
        ),
        "download_opendata_page": (
            "kawasaki_etl.pipelines.opendata",
            "download_opendata_page",
        ),
        "run_childcare_opendata": (
            "kawasaki_etl.pipelines.childcare",
            "run_childcare_opendata",
        ),
    }

    if name in mapping:
        module_path, attr = mapping[name]
        module = __import__(module_path, fromlist=[attr])
        return getattr(module, attr)

    message = f"module {__name__!s} has no attribute {name!s}"
    raise AttributeError(message)


if TYPE_CHECKING:  # pragma: no cover
    from kawasaki_etl.pipelines.disaster import (
        download_disaster_prevention_pages,
        iter_disaster_prevention_pages,
    )
    from kawasaki_etl.pipelines.childcare import run_childcare_opendata
    from kawasaki_etl.pipelines.opendata import download_opendata_page
    from kawasaki_etl.pipelines.population import (
        download_population_2024_pages,
        download_population_2025_pages,
        iter_population_2024_pages,
        iter_population_2025_pages,
    )
    from kawasaki_etl.pipelines.tourism import run_tourism_irikomi
    from kawasaki_etl.pipelines.wifi import run_wifi_count
