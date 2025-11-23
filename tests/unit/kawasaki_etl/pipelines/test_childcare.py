from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from kawasaki_etl.configs import (
    CHILDCARE_ACCEPTANCE_PAGE,
    CHILDCARE_ADJUSTMENT_PAGE,
)
from kawasaki_etl.core import DatasetConfig
from kawasaki_etl.pipelines import opendata
from kawasaki_etl.pipelines.childcare import (
    ChildcarePipelineError,
    run_childcare_opendata,
)

if TYPE_CHECKING:
    from pathlib import Path

    from kawasaki_etl.models import OpenDataPage

PAGES: list[OpenDataPage] = [
    CHILDCARE_ACCEPTANCE_PAGE,
    CHILDCARE_ADJUSTMENT_PAGE,
]
PAGE_IDS = [page.identifier for page in PAGES]


def _make_dataset_config(page: OpenDataPage) -> DatasetConfig:
    return DatasetConfig(
        dataset_id=page.identifier,
        category="childcare",
        url=page.page_url,
        type="pdf",
        parser="childcare_opendata",
        key_fields=[],
    )


@pytest.mark.parametrize("page", PAGES, ids=PAGE_IDS)
def test_childcare_pages_have_absolute_urls(page: OpenDataPage) -> None:
    """Verify that each childcare resource URL is absolute."""
    urls = [resource.url for resource in page.resources]
    assert all(url.startswith("http") for url in urls)


@pytest.mark.parametrize("page", PAGES, ids=PAGE_IDS)
def test_run_childcare_opendata_downloads(
    page: OpenDataPage,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Ensure childcare files are downloaded to the expected directory."""
    created_paths: list[Path] = []

    def _fake_download(url: str, dest: Path) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("dummy", encoding="utf-8")
        assert url
        created_paths.append(dest)

    monkeypatch.setattr(opendata, "download_file", _fake_download)

    config = _make_dataset_config(page)
    outputs = run_childcare_opendata(config, base_dir=tmp_path)

    assert len(outputs) == len(page.resources)
    assert all(path.exists() for path in outputs)
    assert {dest.parent for dest in created_paths} == {
        tmp_path / page.storage_dirname,
    }


def test_run_childcare_opendata_unknown_dataset() -> None:
    """Raise an error when the dataset_id is not registered."""
    config = DatasetConfig(
        dataset_id="unknown_childcare",
        category="childcare",
        url="https://example.com",
        type="pdf",
    )

    with pytest.raises(ChildcarePipelineError):
        run_childcare_opendata(config)
