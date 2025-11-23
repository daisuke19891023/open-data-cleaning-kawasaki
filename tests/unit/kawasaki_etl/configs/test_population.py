from pathlib import Path
from typing import cast

import httpx  # noqa: TC002

from kawasaki_etl.configs.population import get_population_pages_for_year

CATEGORY_URL = "https://www.city.kawasaki.jp/main/opendata/opendata_category_9.html"
SNAPSHOT_URL = "https://example.com/population/2023_snapshot.html"
AGE_URL = "https://www.city.kawasaki.jp/population/2023_age.html"
FOREIGN_URL = "https://example.com/population/2022_foreign.html"


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text

    def raise_for_status(self) -> None:  # pragma: no cover - no error path in tests
        return None


class _FakeClient:
    def __init__(self, mapping: dict[str, str]) -> None:
        self.mapping = mapping

    def get(self, url: str) -> _FakeResponse:
        if url not in self.mapping:
            msg = f"URL not stubbed: {url}"
            raise AssertionError(msg)
        return _FakeResponse(self.mapping[url])


def _load_fixture(name: str) -> str:
    base = Path(__file__).resolve().parents[3] / "fixtures" / "population"
    return (base / name).read_text(encoding="utf-8")


def test_get_population_pages_for_year_parses_links() -> None:
    """動的パーサーが年度セクションとリソースを解釈できること."""
    category_html = _load_fixture("category.html")
    snapshot_html = _load_fixture("2023_snapshot.html")
    age_html = _load_fixture("2023_age.html")

    client = cast(
        "httpx.Client",
        _FakeClient(
            {
                CATEGORY_URL: category_html,
                SNAPSHOT_URL: snapshot_html,
                AGE_URL: age_html,
            },
        ),
    )

    pages = get_population_pages_for_year(2023, client=client)

    identifiers = [page.identifier for page in pages]
    assert identifiers == [
        "population_2023_2023_snapshot",
        "population_2023_2023_age",
    ]

    first_page = pages[0]
    assert first_page.page_url == SNAPSHOT_URL
    assert first_page.description.startswith("川崎市の世帯数・人口")
    assert {resource.file_format for resource in first_page.resources} == {"xls", "pdf"}
    assert first_page.resources[0].updated_at == "2023-04-01"

    second_page = pages[1]
    assert second_page.page_url == AGE_URL
    assert len(second_page.resources) == 1
    assert second_page.resources[0].url.endswith("opendata202307.csv")
    assert second_page.resources[0].updated_at == "2023-07-01"


def test_get_population_pages_for_year_skips_other_year() -> None:
    """指定した年度のリンクのみが収集されること."""
    category_html = _load_fixture("category.html")
    foreign_html = _load_fixture("2022_foreign.html")

    client = cast(
        "httpx.Client",
        _FakeClient({CATEGORY_URL: category_html, FOREIGN_URL: foreign_html}),
    )

    pages = get_population_pages_for_year(2022, client=client)

    assert [page.identifier for page in pages] == ["population_2022_2022_foreign"]
    assert len(pages[0].resources) == 2
    assert pages[0].resources[0].updated_at == "2022-04-01"
