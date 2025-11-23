from __future__ import annotations

# ruff: noqa: RUF001

import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx

from kawasaki_etl.models import OpenDataPage, OpenDataResource


BASE_CATEGORY_URL = (
    "https://www.city.kawasaki.jp/main/opendata/opendata_category_9.html"
)

LONG_TERM_BASE_URL = "https://www.city.kawasaki.jp/170/page/0000010875.html"
LONG_TERM_PAGE = OpenDataPage(
    identifier="population_longterm_overview",
    page_url=f"{LONG_TERM_BASE_URL}#opendata_dataset_2025",
    description="世帯数・人口の年別/月別推移(長期時系列)",
    resources=(
        OpenDataResource(
            title="世帯数、男女別人口、面積の推移（年別　csv）",
            url=urljoin(
                LONG_TERM_BASE_URL, "../cmsfiles/contents/0000010/10875/jinko.csv",
            ),
            file_format="csv",
            updated_at="2025-04-01",
            description="年別の世帯数・男女別人口・面積推移",
        ),
        OpenDataResource(
            title="月別、世帯数人口の推移（全市、区別　csv）",
            url=urljoin(
                LONG_TERM_BASE_URL,
                "../cmsfiles/contents/0000010/10875/jinkolong.csv",
            ),
            file_format="csv",
            updated_at="2025-04-01",
            description="月別の世帯数・人口推移（全市・区別）",
        ),
    ),
)

POPULATION_2025_04_BASE_URL = "https://www.city.kawasaki.jp/170/page/0000175749.html"
POPULATION_2025_04_PAGE = OpenDataPage(
    identifier="population_snapshot_2025_04",
    page_url=f"{POPULATION_2025_04_BASE_URL}#opendata_dataset_6",
    description="川崎市の世帯数・人口（令和7年4月1日現在）",
    resources=(
        OpenDataResource(
            title="川崎市の世帯数・人口（令和7年4月1日現在）",
            url=urljoin(
                POPULATION_2025_04_BASE_URL,
                "../cmsfiles/contents/0000175/175749/2504(no723).xls",
            ),
            file_format="xls",
            updated_at="2025-04-01",
            description="令和7年4月1日時点の世帯数・人口統計",
        ),
    ),
)

POPULATION_2025_05_BASE_URL = "https://www.city.kawasaki.jp/170/page/0000176618.html"
POPULATION_2025_05_PAGE = OpenDataPage(
    identifier="population_snapshot_2025_05",
    page_url=f"{POPULATION_2025_05_BASE_URL}#opendata_dataset_6",
    description="川崎市の世帯数・人口（令和7年5月1日現在）",
    resources=(
        OpenDataResource(
            title="川崎市の世帯数・人口（令和7年5月1日現在）",
            url=urljoin(
                POPULATION_2025_05_BASE_URL,
                "../cmsfiles/contents/0000176/176618/2505(no724).xls",
            ),
            file_format="xls",
            updated_at="2025-05-01",
            description="令和7年5月1日時点の世帯数・人口統計",
        ),
    ),
)

POPULATION_2025_06_BASE_URL = "https://www.city.kawasaki.jp/170/page/0000177392.html"
POPULATION_2025_06_PAGE = OpenDataPage(
    identifier="population_snapshot_2025_06",
    page_url=f"{POPULATION_2025_06_BASE_URL}#opendata_dataset_6",
    description="川崎市の世帯数・人口（令和7年6月1日現在）",
    resources=(
        OpenDataResource(
            title="川崎市の世帯数・人口（令和7年6月1日現在）",
            url=urljoin(
                POPULATION_2025_06_BASE_URL,
                "../cmsfiles/contents/0000177/177392/2506(no725).xls",
            ),
            file_format="xls",
            updated_at="2025-06-01",
            description="令和7年6月1日時点の世帯数・人口統計",
        ),
    ),
)

FOREIGN_NATIONALITIES_BASE_URL = "https://www.city.kawasaki.jp/250/page/0000177712.html"
FOREIGN_NATIONALITIES_PAGE = OpenDataPage(
    identifier="foreign_nationalities_2025",
    page_url=f"{FOREIGN_NATIONALITIES_BASE_URL}#opendata_dataset_1",
    description="外国人国籍地域別統計（令和7(2025)年度）",
    resources=(
        OpenDataResource(
            title="外国人国籍地域別統計（2025年4月）",
            url=urljoin(
                FOREIGN_NATIONALITIES_BASE_URL,
                "../cmsfiles/contents/0000177/177712/202504.csv",
            ),
            file_format="csv",
            updated_at="2025-04-01",
        ),
        OpenDataResource(
            title="外国人国籍地域別統計（2025年5月）",
            url=urljoin(
                FOREIGN_NATIONALITIES_BASE_URL,
                "../cmsfiles/contents/0000177/177712/202505.csv",
            ),
            file_format="csv",
            updated_at="2025-05-01",
        ),
        OpenDataResource(
            title="外国人国籍地域別統計（2025年6月）",
            url=urljoin(
                FOREIGN_NATIONALITIES_BASE_URL,
                "../cmsfiles/contents/0000177/177712/202506.csv",
            ),
            file_format="csv",
            updated_at="2025-06-01",
        ),
        OpenDataResource(
            title="外国人国籍地域別統計（2025年7月）",
            url=urljoin(
                FOREIGN_NATIONALITIES_BASE_URL,
                "../cmsfiles/contents/0000177/177712/202507.csv",
            ),
            file_format="csv",
            updated_at="2025-07-01",
        ),
        OpenDataResource(
            title="外国人国籍地域別統計（2025年8月）",
            url=urljoin(
                FOREIGN_NATIONALITIES_BASE_URL,
                "../cmsfiles/contents/0000177/177712/202508.csv",
            ),
            file_format="csv",
            updated_at="2025-08-01",
        ),
        OpenDataResource(
            title="外国人国籍地域別統計（2025年9月）",
            url=urljoin(
                FOREIGN_NATIONALITIES_BASE_URL,
                "../cmsfiles/contents/0000177/177712/202509.csv",
            ),
            file_format="csv",
            updated_at="2025-09-01",
        ),
        OpenDataResource(
            title="外国人国籍地域別統計（2025年10月）",
            url=urljoin(
                FOREIGN_NATIONALITIES_BASE_URL,
                "../cmsfiles/contents/0000177/177712/202510.csv",
            ),
            file_format="csv",
            updated_at="2025-10-01",
        ),
        OpenDataResource(
            title="公開データ利用規約（外国人国籍地域別統計）",
            url=urljoin(
                FOREIGN_NATIONALITIES_BASE_URL,
                "../cmsfiles/contents/0000177/177712/kawasakiod_rules.pdf",
            ),
            file_format="pdf",
            updated_at="2025-04-01",
            description="外国人国籍地域別統計の利用規約",
        ),
    ),
)

POPULATION_2025_07_BASE_URL = "https://www.city.kawasaki.jp/170/page/0000178232.html"
POPULATION_2025_07_PAGE = OpenDataPage(
    identifier="population_snapshot_2025_07",
    page_url=f"{POPULATION_2025_07_BASE_URL}#opendata_dataset_6",
    description="川崎市の世帯数・人口（令和7年7月1日現在）",
    resources=(
        OpenDataResource(
            title="川崎市の世帯数・人口（令和7年7月1日現在）",
            url=urljoin(
                POPULATION_2025_07_BASE_URL,
                "../cmsfiles/contents/0000178/178232/2507(no726).xls",
            ),
            file_format="xls",
            updated_at="2025-07-01",
            description="令和7年7月1日時点の世帯数・人口統計",
        ),
    ),
)

TOWN_POPULATION_2025_07_BASE_URL = (
    "https://www.city.kawasaki.jp/170/page/0000178367.html"
)
TOWN_POPULATION_2025_07_PAGE = OpenDataPage(
    identifier="town_population_2025_07",
    page_url=f"{TOWN_POPULATION_2025_07_BASE_URL}#opendata_dataset_2",
    description="町丁別世帯数・人口（令和7年7月末日現在）",
    resources=(
        OpenDataResource(
            title="町丁別世帯数・人口（令和7年7月末日現在）",
            url=urljoin(
                TOWN_POPULATION_2025_07_BASE_URL,
                "../cmsfiles/contents/0000178/178367/tyoutyou202507.xls",
            ),
            file_format="xls",
            updated_at="2025-07-31",
            description="町丁別の世帯数・人口（7月末）",
        ),
    ),
)

AGE_POPULATION_2025_07_BASE_URL = (
    "https://www.city.kawasaki.jp/170/page/0000178368.html"
)
AGE_POPULATION_2025_07_PAGE = OpenDataPage(
    identifier="age_population_2025_07",
    page_url=f"{AGE_POPULATION_2025_07_BASE_URL}#opendata_dataset_2",
    description="全市・区別・管区別・町丁別年齢別人口（令和7年6月末日現在）",
    resources=(
        OpenDataResource(
            title="年齢別人口（エクセル・全市/区別/管区別/町丁別）",
            url=urljoin(
                AGE_POPULATION_2025_07_BASE_URL,
                "../cmsfiles/contents/0000178/178368/tyounen202507all.xls",
            ),
            file_format="xls",
            updated_at="2025-06-30",
        ),
        OpenDataResource(
            title="年齢別人口（オープンデータCSV）",
            url=urljoin(
                AGE_POPULATION_2025_07_BASE_URL,
                "../cmsfiles/contents/0000178/178368/opendata202507.csv",
            ),
            file_format="csv",
            updated_at="2025-06-30",
        ),
    ),
)

POPULATION_2025_08_BASE_URL = "https://www.city.kawasaki.jp/170/page/0000178933.html"
POPULATION_2025_08_PAGE = OpenDataPage(
    identifier="population_snapshot_2025_08",
    page_url=f"{POPULATION_2025_08_BASE_URL}#opendata_dataset_6",
    description="川崎市の世帯数・人口（令和7年8月1日現在）",
    resources=(
        OpenDataResource(
            title="川崎市の世帯数・人口（令和7年8月1日現在）",
            url=urljoin(
                POPULATION_2025_08_BASE_URL,
                "../cmsfiles/contents/0000178/178933/2508(no727).xls",
            ),
            file_format="xls",
            updated_at="2025-08-01",
            description="令和7年8月1日時点の世帯数・人口統計",
        ),
    ),
)

POPULATION_2025_09_BASE_URL = "https://www.city.kawasaki.jp/170/page/0000180024.html"
POPULATION_2025_09_PAGE = OpenDataPage(
    identifier="population_snapshot_2025_09",
    page_url=f"{POPULATION_2025_09_BASE_URL}#opendata_dataset_6",
    description="川崎市の世帯数・人口（令和7年9月1日現在）",
    resources=(
        OpenDataResource(
            title="川崎市の世帯数・人口（令和7年9月1日現在）",
            url=urljoin(
                POPULATION_2025_09_BASE_URL,
                "../cmsfiles/contents/0000180/180024/2509(no728).xls",
            ),
            file_format="xls",
            updated_at="2025-09-01",
            description="令和7年9月1日時点の世帯数・人口統計",
        ),
    ),
)

POPULATION_2025_10_BASE_URL = "https://www.city.kawasaki.jp/170/page/0000180576.html"
POPULATION_2025_10_PAGE = OpenDataPage(
    identifier="population_snapshot_2025_10",
    page_url=f"{POPULATION_2025_10_BASE_URL}#opendata_dataset_7",
    description="川崎市の世帯数・人口（令和7年10月1日現在）",
    resources=(
        OpenDataResource(
            title="川崎市の世帯数・人口（令和7年10月1日現在）(Excel)",
            url=urljoin(
                POPULATION_2025_10_BASE_URL,
                "../cmsfiles/contents/0000180/180576/2510(no729).xlsx",
            ),
            file_format="xlsx",
            updated_at="2025-10-01",
        ),
        OpenDataResource(
            title="川崎市の世帯数・人口（令和7年10月1日現在）(PDF)",
            url=urljoin(
                POPULATION_2025_10_BASE_URL,
                "../cmsfiles/contents/0000180/180576/2510(no729).pdf",
            ),
            file_format="pdf",
            updated_at="2025-10-01",
        ),
    ),
)

TOWN_POPULATION_2025_09_BASE_URL = (
    "https://www.city.kawasaki.jp/170/page/0000181216.html"
)
TOWN_POPULATION_2025_09_PAGE = OpenDataPage(
    identifier="town_population_2025_09",
    page_url=f"{TOWN_POPULATION_2025_09_BASE_URL}#opendata_dataset_3",
    description="町丁別世帯数・人口（令和7年9月末日現在）",
    resources=(
        OpenDataResource(
            title="町丁別世帯数・人口（冊子PDF）",
            url=urljoin(
                TOWN_POPULATION_2025_09_BASE_URL,
                "../cmsfiles/contents/0000181/181216/sassi202510.pdf",
            ),
            file_format="pdf",
            updated_at="2025-09-30",
        ),
        OpenDataResource(
            title="町丁別世帯数・人口（エクセルデータ）",
            url=urljoin(
                TOWN_POPULATION_2025_09_BASE_URL,
                "../cmsfiles/contents/0000181/181216/tyotyo202510.xls",
            ),
            file_format="xls",
            updated_at="2025-09-30",
        ),
    ),
)

AGE_POPULATION_2025_09_BASE_URL = (
    "https://www.city.kawasaki.jp/170/page/0000181218.html"
)
AGE_POPULATION_2025_09_PAGE = OpenDataPage(
    identifier="age_population_2025_09",
    page_url=f"{AGE_POPULATION_2025_09_BASE_URL}#opendata_dataset_2",
    description="全市・区別・管区別・町丁別年齢別人口（令和7年9月末日現在）",
    resources=(
        OpenDataResource(
            title="年齢別人口（エクセル・全市/区別/管区別/町丁別）",
            url=urljoin(
                AGE_POPULATION_2025_09_BASE_URL,
                "../cmsfiles/contents/0000181/181218/tyonen202510all.xls",
            ),
            file_format="xls",
            updated_at="2025-09-30",
        ),
        OpenDataResource(
            title="年齢別人口（オープンデータCSV）",
            url=urljoin(
                AGE_POPULATION_2025_09_BASE_URL,
                "../cmsfiles/contents/0000181/181218/opendata202510.csv",
            ),
            file_format="csv",
            updated_at="2025-09-30",
        ),
        OpenDataResource(
            title="長寿人口(令和5年度12月時点参考)",
            url=urljoin(
                AGE_POPULATION_2025_09_BASE_URL,
                "../cmsfiles/contents/0000181/181218/chouchou(r0512).xls",
            ),
            file_format="xls",
            updated_at="2023-12-31",
            description="補足の長寿人口データ(令和5年度)",
        ),
    ),
)

POPULATION_2025_11_BASE_URL = "https://www.city.kawasaki.jp/170/page/0000181789.html"
POPULATION_2025_11_PAGE = OpenDataPage(
    identifier="population_snapshot_2025_11",
    page_url=f"{POPULATION_2025_11_BASE_URL}#opendata_dataset_7",
    description="川崎市の世帯数・人口（令和7年11月1日現在）",
    resources=(
        OpenDataResource(
            title="川崎市の世帯数・人口（令和7年11月1日現在）(Excel)",
            url=urljoin(
                POPULATION_2025_11_BASE_URL,
                "../cmsfiles/contents/0000181/181789/2511(no730).xlsx",
            ),
            file_format="xlsx",
            updated_at="2025-11-01",
        ),
        OpenDataResource(
            title="川崎市の世帯数・人口（令和7年11月1日現在）(PDF)",
            url=urljoin(
                POPULATION_2025_11_BASE_URL,
                "../cmsfiles/contents/0000181/181789/2511(no730).pdf",
            ),
            file_format="pdf",
            updated_at="2025-11-01",
        ),
    ),
)

POPULATION_2025_PAGES: tuple[OpenDataPage, ...] = (
    LONG_TERM_PAGE,
    POPULATION_2025_04_PAGE,
    POPULATION_2025_05_PAGE,
    POPULATION_2025_06_PAGE,
    FOREIGN_NATIONALITIES_PAGE,
    POPULATION_2025_07_PAGE,
    TOWN_POPULATION_2025_07_PAGE,
    AGE_POPULATION_2025_07_PAGE,
    POPULATION_2025_08_PAGE,
    POPULATION_2025_09_PAGE,
    POPULATION_2025_10_PAGE,
    TOWN_POPULATION_2025_09_PAGE,
    AGE_POPULATION_2025_09_PAGE,
    POPULATION_2025_11_PAGE,
)


__all__ = [
    "BASE_CATEGORY_URL",
    "POPULATION_2025_PAGES",
    "get_population_pages_for_year",
]


CMSFILES_LINK_RE = re.compile(r'href="([^"]*cmsfiles[^"]+)"[^>]*>(.*?)</a>', re.DOTALL)
YEAR_MONTH_DIGITS = 6
MONTHS_PER_YEAR = 12


def _make_identifier(year: int, page_url: str) -> str:
    stem = Path(urlparse(page_url).path).stem
    return f"population_{year}_{stem}"


def _extract_year_section_links(html: str, year: int) -> list[tuple[str, str]]:
    year_block = re.search(
        rf"<h2>{year}年度</h2>\s*<ul class=\"publicity_list\">(.*?)</ul>",
        html,
        re.DOTALL,
    )
    if not year_block:
        return []

    links: list[tuple[str, str]] = []
    for href, title in re.findall(
        r'href="([^"]+)"[^>]*>([^<]+)</a>', year_block.group(1),
    ):
        links.append((href, title.strip()))
    return links


def _infer_updated_at(resource_url: str, fallback_year: int) -> str:
    filename = Path(urlparse(resource_url).path).name
    year_month_match = re.search(r"(\d{6}|\d{4})", filename)
    if not year_month_match:
        return f"{fallback_year}-01-01"

    raw = year_month_match.group(1)
    if len(raw) == YEAR_MONTH_DIGITS:
        year = int(raw[:4])
        month = int(raw[4:6])
    else:
        year = 2000 + int(raw[:2])
        month = int(raw[2:])

    if not 1 <= month <= MONTHS_PER_YEAR:
        return f"{fallback_year}-01-01"
    return f"{year:04d}-{month:02d}-01"


def _extract_resources(
    page_html: str, page_url: str, fallback_year: int,
) -> tuple[OpenDataResource, ...]:
    resources: list[OpenDataResource] = []
    for href, title_html in CMSFILES_LINK_RE.findall(page_html):
        title = re.sub(r"<[^>]+>", "", title_html).strip()
        resource_url = urljoin(page_url, href)
        resources.append(
            OpenDataResource(
                title=title,
                url=resource_url,
                file_format=Path(urlparse(resource_url).path).suffix.lstrip(".").lower(),
                updated_at=_infer_updated_at(resource_url, fallback_year),
            ),
        )
    return tuple(resources)


def _resolve_population_pages_for_year(
    year: int, client: httpx.Client,
) -> tuple[OpenDataPage, ...]:
    category_response = client.get(BASE_CATEGORY_URL)
    category_response.raise_for_status()
    category_html = category_response.text
    links = _extract_year_section_links(category_html, year)

    pages: list[OpenDataPage] = []
    for href, title in links:
        page_url = urljoin(BASE_CATEGORY_URL, href)
        page_response = client.get(page_url)
        page_response.raise_for_status()
        page_html = page_response.text
        resources = _extract_resources(page_html, page_url, fallback_year=year)
        if not resources:
            continue
        pages.append(
            OpenDataPage(
                identifier=_make_identifier(year, page_url),
                page_url=page_url,
                description=title,
                resources=resources,
            ),
        )

    return tuple(pages)


def get_population_pages_for_year(
    year: int, client: httpx.Client | None = None,
) -> tuple[OpenDataPage, ...]:
    """人口・世帯カテゴリの指定年度セクションを動的にパースして OpenDataPage を返す."""

    def _resolve(http_client: httpx.Client) -> tuple[OpenDataPage, ...]:
        return _resolve_population_pages_for_year(year, http_client)

    if client is not None:
        return _resolve(client)

    with httpx.Client(follow_redirects=True) as http_client:
        return _resolve(http_client)
