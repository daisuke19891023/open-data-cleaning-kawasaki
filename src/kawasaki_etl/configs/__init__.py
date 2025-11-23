"""Static configuration values for open data pages."""

from kawasaki_etl.configs.aed_locations import AED_LOCATIONS_PAGE
from kawasaki_etl.configs.childcare import (
    CHILDCARE_ACCEPTANCE_PAGE,
    CHILDCARE_ADJUSTMENT_PAGE,
    CHILDCARE_PAGES,
    CHILDCARE_PAGES_BY_ID,
)
from kawasaki_etl.configs.disaster_prevention import (
    DISASTER_PREVENTION_PAGES,
    EVACUATION_PAGE,
    FIRE_CISTERN_PAGE,
    FIRE_EQUIPMENT_PAGE,
    FIRE_HYDRANT_PAGE,
    FIRE_STATION_PAGE,
    HAZARD_PAGE,
    WATER_SUPPLY_PAGE,
)
from kawasaki_etl.configs.population import BASE_CATEGORY_URL, POPULATION_2025_PAGES
from kawasaki_etl.configs.pharmacy_permits import PHARMACY_PERMITS_PAGE

__all__ = [
    "AED_LOCATIONS_PAGE",
    "BASE_CATEGORY_URL",
    "CHILDCARE_ACCEPTANCE_PAGE",
    "CHILDCARE_ADJUSTMENT_PAGE",
    "CHILDCARE_PAGES",
    "CHILDCARE_PAGES_BY_ID",
    "DISASTER_PREVENTION_PAGES",
    "EVACUATION_PAGE",
    "FIRE_CISTERN_PAGE",
    "FIRE_EQUIPMENT_PAGE",
    "FIRE_HYDRANT_PAGE",
    "FIRE_STATION_PAGE",
    "HAZARD_PAGE",
    "PHARMACY_PERMITS_PAGE",
    "POPULATION_2025_PAGES",
    "WATER_SUPPLY_PAGE",
]
