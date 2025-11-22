"""Static configuration values for open data pages."""

from kawasaki_etl.configs.pharmacy_closures import PHARMACY_CLOSURES_PAGE
from kawasaki_etl.configs.pharmacy_permits import PHARMACY_PERMITS_PAGE

OPEN_DATA_PAGES = (
    PHARMACY_PERMITS_PAGE,
    PHARMACY_CLOSURES_PAGE,
)

__all__ = ["OPEN_DATA_PAGES", "PHARMACY_CLOSURES_PAGE", "PHARMACY_PERMITS_PAGE"]
