"""Tests for population 2025 pipelines."""

from pathlib import Path

import pytest

from kawasaki_etl.configs import POPULATION_2025_PAGES
from kawasaki_etl.models import OpenDataPage
from kawasaki_etl.pipelines import population


def test_download_population_2025_pages(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Download helper should fetch all configured 2025 resources."""
    called: list[tuple[str, Path]] = []

    def _fake_download(page: OpenDataPage, base_dir: Path) -> list[Path]:
        paths: list[Path] = []
        for resource in page.resources:
            dest = base_dir / page.storage_dirname / resource.filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text("dummy", encoding="utf-8")
            paths.append(dest)
        called.append((page.identifier, base_dir))
        return paths

    monkeypatch.setattr(population, "download_opendata_page", _fake_download)

    outputs = population.download_population_2025_pages(base_dir=tmp_path)

    assert len(outputs) == sum(len(page.resources) for page in POPULATION_2025_PAGES)
    assert all(path.exists() for path in outputs)
    assert {path.parent for path in outputs} == {
        tmp_path / page.storage_dirname for page in POPULATION_2025_PAGES
    }
    assert {page_id for page_id, _ in called} == {
        page.identifier for page in POPULATION_2025_PAGES
    }


def test_iter_population_2025_pages() -> None:
    """Iterator helper should expose configured pages in order."""
    assert list(population.iter_population_2025_pages()) == list(
        POPULATION_2025_PAGES,
    )
