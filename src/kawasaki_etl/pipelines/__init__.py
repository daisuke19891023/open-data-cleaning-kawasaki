"""Pipeline implementations for individual datasets."""

from kawasaki_etl.pipelines.tourism import run_tourism_irikomi
from kawasaki_etl.pipelines.wifi import run_wifi_count

__all__ = ["run_tourism_irikomi", "run_wifi_count"]
