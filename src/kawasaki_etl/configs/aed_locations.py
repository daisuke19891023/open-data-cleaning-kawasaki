from __future__ import annotations

from urllib.parse import urljoin

from kawasaki_etl.models import OpenDataPage, OpenDataResource

BASE_PAGE_URL = "https://www.city.kawasaki.jp/350/page/0000099784.html"
DATASET_ANCHOR_URL = f"{BASE_PAGE_URL}#opendata_dataset_15"

AED_LOCATIONS_PAGE = OpenDataPage(
    identifier="aed_locations_r7_05",
    page_url=DATASET_ANCHOR_URL,
    description="川崎市内のAED設置箇所一覧（2025年5月1日現在）",
    resources=(
        OpenDataResource(
            title="AED設置箇所一覧（2025年5月1日現在）",
            url=urljoin(
                BASE_PAGE_URL,
                "../cmsfiles/contents/0000099/99784/250501opn.csv",
            ),
            file_format="csv",
            updated_at="2025-05-01",
            description="市内公共施設等に設置されたAEDの位置情報一覧",
        ),
    ),
)
