"""Tests for disaster prevention OpenDataPage definitions."""

from kawasaki_etl.configs import DISASTER_PREVENTION_PAGES


def test_disaster_pages_have_absolute_urls() -> None:
    """Ensure all disaster prevention resources use absolute URLs."""
    resources = [
        resource for page in DISASTER_PREVENTION_PAGES for resource in page.resources
    ]
    assert resources
    assert all(resource.url.startswith("http") for resource in resources)


def test_disaster_pages_have_unique_storage_dirname() -> None:
    """OpenDataPage identifiers should map to unique storage directories."""
    dirnames = [page.storage_dirname for page in DISASTER_PREVENTION_PAGES]
    assert len(dirnames) == len(set(dirnames))
