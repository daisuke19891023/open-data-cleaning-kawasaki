from __future__ import annotations

from urllib.parse import urljoin

from kawasaki_etl.models import OpenDataPage, OpenDataResource

BASE_PAGE_URL = "https://www.city.kawasaki.jp/450/page/0000030624.html"

CHILDCARE_ACCEPTANCE_PAGE = OpenDataPage(
    identifier="childcare_acceptance_r8_04",
    page_url=f"{BASE_PAGE_URL}#opendata_dataset_7",
    description="認可保育所等の受入可能数(最新掲載分)",
    resources=(
        OpenDataResource(
            title="川崎区 受入可能数",  # 11月21日時点
            url=urljoin(
                BASE_PAGE_URL,
                "../cmsfiles/contents/0000030/30624/R8_4_1kawaski07.pdf",
            ),
            file_format="pdf",
            updated_at="2024-11-21",
        ),
        OpenDataResource(
            title="幸区 受入可能数",  # 11月21日時点
            url=urljoin(
                BASE_PAGE_URL,
                "../cmsfiles/contents/0000030/30624/R8_4_1saiwai08.pdf",
            ),
            file_format="pdf",
            updated_at="2024-11-21",
        ),
        OpenDataResource(
            title="中原区 受入可能数",  # 10月31日時点
            url=urljoin(
                BASE_PAGE_URL,
                "../cmsfiles/contents/0000030/30624/R8_4_1nakahara07.pdf",
            ),
            file_format="pdf",
            updated_at="2024-10-31",
        ),
        OpenDataResource(
            title="高津区 受入可能数",  # 11月21日時点
            url=urljoin(
                BASE_PAGE_URL,
                "../cmsfiles/contents/0000030/30624/R8_4_1takatu09.pdf",
            ),
            file_format="pdf",
            updated_at="2024-11-21",
        ),
        OpenDataResource(
            title="宮前区 受入可能数",  # 11月21日時点
            url=urljoin(
                BASE_PAGE_URL,
                "../cmsfiles/contents/0000030/30624/R8_4_1miyamae09.pdf",
            ),
            file_format="pdf",
            updated_at="2024-11-21",
        ),
        OpenDataResource(
            title="多摩区 受入可能数",  # 11月7日時点
            url=urljoin(
                BASE_PAGE_URL,
                "../cmsfiles/contents/0000030/30624/R8_4_1tama05.pdf",
            ),
            file_format="pdf",
            updated_at="2024-11-07",
        ),
        OpenDataResource(
            title="麻生区 受入可能数",  # 11月14日時点
            url=urljoin(
                BASE_PAGE_URL,
                "../cmsfiles/contents/0000030/30624/R8_4_1asao07.pdf",
            ),
            file_format="pdf",
            updated_at="2024-11-14",
        ),
    ),
)

CHILDCARE_ADJUSTMENT_PAGE = OpenDataPage(
    identifier="childcare_adjustment_result_r7_11",
    page_url=f"{BASE_PAGE_URL}#opendata_dataset_10",
    description="認可保育所等の利用調整結果(最新掲載分)",
    resources=(
        OpenDataResource(
            title="川崎区 利用調整結果",
            url=urljoin(
                BASE_PAGE_URL,
                "../cmsfiles/contents/0000030/30624/kekkaR7.11kawasaki01.pdf",
            ),
            file_format="pdf",
            updated_at="2024-11-01",
        ),
        OpenDataResource(
            title="幸区 利用調整結果",
            url=urljoin(
                BASE_PAGE_URL,
                "../cmsfiles/contents/0000030/30624/kekkaR7.11saiwai01.pdf",
            ),
            file_format="pdf",
            updated_at="2024-11-01",
        ),
        OpenDataResource(
            title="中原区 利用調整結果",
            url=urljoin(
                BASE_PAGE_URL,
                "../cmsfiles/contents/0000030/30624/kekkaR7.11nakahara01.pdf",
            ),
            file_format="pdf",
            updated_at="2024-11-01",
        ),
        OpenDataResource(
            title="高津区 利用調整結果",
            url=urljoin(
                BASE_PAGE_URL,
                "../cmsfiles/contents/0000030/30624/kekkaR7.11takatu01.pdf",
            ),
            file_format="pdf",
            updated_at="2024-11-01",
        ),
        OpenDataResource(
            title="宮前区 利用調整結果",
            url=urljoin(
                BASE_PAGE_URL,
                "../cmsfiles/contents/0000030/30624/kekkaR7.11miyamae01.pdf",
            ),
            file_format="pdf",
            updated_at="2024-11-01",
        ),
        OpenDataResource(
            title="多摩区 利用調整結果",
            url=urljoin(
                BASE_PAGE_URL,
                "../cmsfiles/contents/0000030/30624/kekkaR7.11tama01.pdf",
            ),
            file_format="pdf",
            updated_at="2024-11-01",
        ),
        OpenDataResource(
            title="麻生区 利用調整結果",
            url=urljoin(
                BASE_PAGE_URL,
                "../cmsfiles/contents/0000030/30624/kekkaR7.11asao01.pdf",
            ),
            file_format="pdf",
            updated_at="2024-11-01",
        ),
    ),
)

CHILDCARE_PAGES: tuple[OpenDataPage, ...] = (
    CHILDCARE_ACCEPTANCE_PAGE,
    CHILDCARE_ADJUSTMENT_PAGE,
)

CHILDCARE_PAGES_BY_ID: dict[str, OpenDataPage] = {
    page.identifier: page for page in CHILDCARE_PAGES
}
