"""Tests for population pipelines."""

from pathlib import Path
from collections.abc import Callable

import pytest

from kawasaki_etl.configs import POPULATION_2024_PAGES, POPULATION_2025_PAGES
from kawasaki_etl.models import OpenDataPage
from kawasaki_etl.pipelines import population


@pytest.mark.parametrize(
    ("pages", "download_func", "iter_func"),  # type: ignore[arg-type]
    [
        (
            POPULATION_2024_PAGES,
            population.download_population_2024_pages,
            population.iter_population_2024_pages,
        ),
        (
            POPULATION_2025_PAGES,
            population.download_population_2025_pages,
            population.iter_population_2025_pages,
        ),
    ],
)
def test_download_population_pages(
    pages: tuple[OpenDataPage, ...],
    download_func: Callable[..., list[Path]],
    iter_func: Callable[[], tuple[OpenDataPage, ...] | list[OpenDataPage]],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Download helper should fetch all configured resources for each year."""
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

    outputs = download_func(base_dir=tmp_path)

    assert len(outputs) == sum(len(page.resources) for page in pages)
    assert all(path.exists() for path in outputs)
    assert {path.parent for path in outputs} == {
        tmp_path / page.storage_dirname for page in pages
    }
    assert {page_id for page_id, _ in called} == {page.identifier for page in pages}

    assert list(iter_func()) == list(pages)
