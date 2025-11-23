"""Tests for population 2025 pipelines."""

from pathlib import Path

import pytest

from kawasaki_etl.configs import POPULATION_2025_PAGES
from kawasaki_etl.models import OpenDataPage, OpenDataResource
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


def _dummy_page(identifier: str) -> OpenDataPage:
    resource = OpenDataResource(
        title="dummy",
        url="https://example.com/dummy.csv",
        file_format="csv",
        updated_at="2023-01-01",
    )
    return OpenDataPage(
        identifier=identifier,
        page_url="https://example.com/page.html",
        description="desc",
        resources=(resource,),
    )


def test_download_population_dynamic_years(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """Dynamic year downloaders should delegate to config and downloader."""
    dynamic_pages = (_dummy_page("p2023"),)
    recorded: list[tuple[str, Path]] = []

    def _fake_get_population_pages(year: int) -> tuple[OpenDataPage, ...]:
        assert year in {2022, 2023}
        return dynamic_pages

    monkeypatch.setattr(
        population, "get_population_pages_for_year", _fake_get_population_pages,
    )

    def _fake_download(page: OpenDataPage, base_dir: Path) -> list[Path]:
        dest = base_dir / page.storage_dirname / page.resources[0].filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("ok", encoding="utf-8")
        recorded.append((page.identifier, base_dir))
        return [dest]

    monkeypatch.setattr(population, "download_opendata_page", _fake_download)

    outputs_2023 = population.download_population_2023_pages(
        base_dir=tmp_path / "p23",
    )
    outputs_2022 = population.download_population_2022_pages(
        base_dir=tmp_path / "p22",
    )

    assert outputs_2023
    assert outputs_2022
    assert {path.parent for path in outputs_2023} == {tmp_path / "p23" / "p2023"}
    assert {path.parent for path in outputs_2022} == {tmp_path / "p22" / "p2023"}
    assert {page_id for page_id, _ in recorded} == {"p2023"}


def test_iter_population_dynamic_years(monkeypatch: pytest.MonkeyPatch) -> None:
    """Iter helper should surface dynamic pages."""
    dynamic_pages = (_dummy_page("p2022"),)

    def _fake_get_population_pages(year: int) -> tuple[OpenDataPage, ...]:
        assert year in {2022, 2023}
        return dynamic_pages

    monkeypatch.setattr(
        population, "get_population_pages_for_year", _fake_get_population_pages,
    )

    assert list(population.iter_population_2023_pages()) == list(dynamic_pages)
    assert list(population.iter_population_2022_pages()) == list(dynamic_pages)
