from __future__ import annotations

from urllib.parse import urljoin

from kawasaki_etl.models import OpenDataPage, OpenDataResource

BASE_PAGE_URL = "https://www.city.kawasaki.jp/350/page/0000094095.html"
DATASET_ANCHOR_URL = f"{BASE_PAGE_URL}#opendata_dataset_3"

PHARMACY_PERMITS_PAGE = OpenDataPage(
    identifier="pharmacy_permits_r7_10",
    page_url=DATASET_ANCHOR_URL,
    description="許可を受けている薬局、店舗販売業、卸売販売業に関する情報",
    resources=(
        OpenDataResource(
            title="薬局の営業所一覧（令和7年10月末時点）",
            url=urljoin(BASE_PAGE_URL, "../cmsfiles/contents/0000094/94095/yakkyoku10.csv"),
            file_format="csv",
            updated_at="2025-10-31",
            description="前月末時点で営業許可を受けている薬局の営業所一覧",
        ),
        OpenDataResource(
            title="店舗販売業の営業所一覧(令和7年10月末時点)",
            url=urljoin(BASE_PAGE_URL, "../cmsfiles/contents/0000094/94095/tenpo10.csv"),
            file_format="csv",
            updated_at="2025-10-31",
            description="前月末時点で営業許可を受けている店舗販売業の営業所一覧",
        ),
        OpenDataResource(
            title="卸売販売業の営業所一覧(令和7年10月末時点)",
            url=urljoin(BASE_PAGE_URL, "../cmsfiles/contents/0000094/94095/oroshi10.csv"),
            file_format="csv",
            updated_at="2025-10-31",
            description="前月末時点で営業許可を受けている卸売販売業の営業所一覧",
        ),
    ),
)
