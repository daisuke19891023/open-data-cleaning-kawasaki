"""Tests for disaster prevention pipelines."""

from pathlib import Path

import pytest

from kawasaki_etl.configs import DISASTER_PREVENTION_PAGES
from kawasaki_etl.models import OpenDataPage
from kawasaki_etl.pipelines import disaster


def test_download_disaster_prevention_pages(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Download helper should save all configured resources under the base dir."""
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

    monkeypatch.setattr(disaster, "download_opendata_page", _fake_download)

    outputs = disaster.download_disaster_prevention_pages(base_dir=tmp_path)

    assert len(outputs) == sum(
        len(page.resources) for page in DISASTER_PREVENTION_PAGES
    )
    assert all(path.exists() for path in outputs)
    expected_dirs = {
        tmp_path / page.storage_dirname for page in DISASTER_PREVENTION_PAGES
    }
    assert {path.parent for path in outputs} == expected_dirs
    assert {dirname for dirname, _ in called} == {
        page.identifier for page in DISASTER_PREVENTION_PAGES
    }


def test_iter_disaster_prevention_pages() -> None:
    """Iterator helper should expose the configured pages."""
    pages = list(disaster.iter_disaster_prevention_pages())
    assert pages == list(DISASTER_PREVENTION_PAGES)
