from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from kawasaki_etl.configs import AED_LOCATIONS_PAGE, PHARMACY_PERMITS_PAGE
from kawasaki_etl.pipelines import opendata
from kawasaki_etl.pipelines.opendata import download_opendata_page

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path
    from kawasaki_etl.models import OpenDataPage


@pytest.mark.parametrize(
    "page",
    [PHARMACY_PERMITS_PAGE, AED_LOCATIONS_PAGE],
    ids=lambda page: page.identifier,
)
def test_config_has_absolute_urls(page: OpenDataPage) -> None:
    """すべてのリソースURLが絶対パスであることを確認する."""
    urls = [resource.url for resource in page.resources]
    assert all(url.startswith("http") for url in urls)


@pytest.mark.parametrize(
    "page",
    [PHARMACY_PERMITS_PAGE, AED_LOCATIONS_PAGE],
    ids=lambda page: page.identifier,
)
def test_download_opendata_page(
    page: OpenDataPage,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """ダウンロード関数が各リソースを保存することを確認する."""
    called: list[tuple[str, Path]] = []

    def _fake_download(url: str, dest: Path) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("dummy", encoding="utf-8")
        called.append((url, dest))

    monkeypatch.setattr(opendata, "download_file", _fake_download)

    outputs = download_opendata_page(page, base_dir=tmp_path)

    assert len(outputs) == len(page.resources)
    assert all(path.exists() for path in outputs)
    assert {dest.parent for _, dest in called} == {
        tmp_path / page.storage_dirname,
    }

    expected_filenames = {resource.filename for resource in page.resources}
    downloaded_filenames = {dest.name for _, dest in called}
    assert downloaded_filenames == expected_filenames
