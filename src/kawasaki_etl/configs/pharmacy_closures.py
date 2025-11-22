from __future__ import annotations

from urllib.parse import urljoin

from kawasaki_etl.models import OpenDataPage, OpenDataResource

BASE_PAGE_URL = "https://www.city.kawasaki.jp/350/page/0000094095.html"
DATASET_ANCHOR_URL = f"{BASE_PAGE_URL}#opendata_dataset_6"

PHARMACY_CLOSURES_PAGE = OpenDataPage(
    identifier="pharmacy_closures_r7_10",
    page_url=DATASET_ANCHOR_URL,
    description="前月に廃止を届け出た薬局、店舗販売業、卸売販売業に関する情報",
    resources=(
        OpenDataResource(
            title="廃止を届け出た薬局一覧(令和7年10月)",
            url=urljoin(
                BASE_PAGE_URL,
                "../cmsfiles/contents/0000094/94095/haishiyakkyoku10.csv",
            ),
            file_format="csv",
            updated_at="2025-10-31",
            description="前月廃止を届け出た薬局の営業所一覧",
        ),
        OpenDataResource(
            title="廃止を届け出た店舗販売業の営業所一覧(令和7年10月)",
            url=urljoin(
                BASE_PAGE_URL,
                "../cmsfiles/contents/0000094/94095/haishitenpo10.csv",
            ),
            file_format="csv",
            updated_at="2025-10-31",
            description="前月に廃止を届け出た店舗販売業の営業所一覧",
        ),
        OpenDataResource(
            title="廃止を届け出た卸売販売業の営業所一覧(令和7年10月)",
            url=urljoin(
                BASE_PAGE_URL,
                "../cmsfiles/contents/0000094/94095/haishioroshi10.csv",
            ),
            file_format="csv",
            updated_at="2025-10-31",
            description="前月に廃止を届け出た卸売販売業の営業所一覧",
        ),
    ),
)
