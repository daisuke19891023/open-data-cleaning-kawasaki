from __future__ import annotations

from urllib.parse import urljoin

from kawasaki_etl.models import OpenDataPage, OpenDataResource

# 防災・防犯カテゴリの代表的なオープンデータページ定義

WATER_SUPPLY_BASE_URL = "https://www.city.kawasaki.jp/800/page/0000085691.html"
WATER_SUPPLY_PAGE = OpenDataPage(
    identifier="emergency_water_points_r7_04",
    page_url=f"{WATER_SUPPLY_BASE_URL}#opendata_dataset_3",
    description="応急給水拠点一覧(令和7年4月1日時点)",
    resources=(
        OpenDataResource(
            title="応急給水拠点一覧",
            url=urljoin(
                WATER_SUPPLY_BASE_URL,
                "../cmsfiles/contents/0000085/85691/241007_2Gcd_File060327.gcd_20250327102044.csv",
            ),
            file_format="csv",
            updated_at="2025-04-01",
            description="市内応急給水拠点の一覧データ",
        ),
    ),
)

EVACUATION_BASE_URL = "https://www.city.kawasaki.jp/601/page/0000036154.html"
EVACUATION_PAGE = OpenDataPage(
    identifier="designated_evacuation_sites_r3_08",
    page_url=f"{EVACUATION_BASE_URL}#opendata_dataset_5",
    description="指定避難所一覧(資料)",
    resources=(
        OpenDataResource(
            title="指定避難所一覧",
            url=urljoin(
                EVACUATION_BASE_URL,
                "../cmsfiles/contents/0000036/36154/hinan210823.xlsx",
            ),
            file_format="xlsx",
            updated_at="2021-08-23",
            description="市内の指定避難所リスト",
        ),
    ),
)

HAZARD_BASE_URL = "https://www.city.kawasaki.jp/800/page/0000133400.html"
HAZARD_PAGE = OpenDataPage(
    identifier="internal_flood_hazard_map",
    page_url=f"{HAZARD_BASE_URL}#opendata_dataset_3",
    description="内水ハザードマップ(浸水想定区域)データ",
    resources=(
        OpenDataResource(
            title="内水ハザードマップ(浸水想定区域)データ",
            url=urljoin(
                HAZARD_BASE_URL,
                "../cmsfiles/contents/0000133/133400/naisuihazadodata.zip",
            ),
            file_format="zip",
            updated_at="2025-03-27",
            description="内水ハザードマップのデータ一式",
        ),
    ),
)

FIRE_BASE_URL = "https://www.city.kawasaki.jp/170/page/0000058746.html"
FIRE_STATION_PAGE = OpenDataPage(
    identifier="fire_station_list_h27_10",
    page_url=f"{FIRE_BASE_URL}#opendata_dataset_3",
    description="消防署・出張所一覧(2015年)",
    resources=(
        OpenDataResource(
            title="消防署・出張所一覧",
            url=urljoin(
                FIRE_BASE_URL,
                "../cmsfiles/contents/0000058/58746/firestat20151001.csv",
            ),
            file_format="csv",
            updated_at="2015-10-01",
            description="消防署および出張所の所在地一覧",
        ),
    ),
)

FIRE_EQUIPMENT_PAGE = OpenDataPage(
    identifier="fire_brigade_storage_h27_10",
    page_url=f"{FIRE_BASE_URL}#opendata_dataset_4",
    description="消防団(器具置場)一覧(2015年)",
    resources=(
        OpenDataResource(
            title="消防団(器具置場)一覧",
            url=urljoin(
                FIRE_BASE_URL,
                "../cmsfiles/contents/0000058/58746/firecomp20151001.csv",
            ),
            file_format="csv",
            updated_at="2015-10-01",
            description="消防団器具置場の一覧",
        ),
    ),
)

FIRE_HYDRANT_PAGE = OpenDataPage(
    identifier="public_fire_hydrants_h27_10",
    page_url=f"{FIRE_BASE_URL}#opendata_dataset_5",
    description="消火栓(公設)一覧(2015年)",
    resources=(
        OpenDataResource(
            title="消火栓(公設)一覧",
            url=urljoin(
                FIRE_BASE_URL,
                "../cmsfiles/contents/0000058/58746/firehyd20151001.csv",
            ),
            file_format="csv",
            updated_at="2015-10-01",
            description="公設消火栓の一覧",
        ),
    ),
)

FIRE_CISTERN_PAGE = OpenDataPage(
    identifier="public_fire_cisterns_h27_10",
    page_url=f"{FIRE_BASE_URL}#opendata_dataset_6",
    description="防火水槽(公設)一覧(2015年)",
    resources=(
        OpenDataResource(
            title="防火水槽(公設)一覧",
            url=urljoin(
                FIRE_BASE_URL,
                "../cmsfiles/contents/0000058/58746/firetank20151001.csv",
            ),
            file_format="csv",
            updated_at="2015-10-01",
            description="防火水槽の一覧",
        ),
    ),
)

DISASTER_PREVENTION_PAGES: tuple[OpenDataPage, ...] = (
    WATER_SUPPLY_PAGE,
    EVACUATION_PAGE,
    HAZARD_PAGE,
    FIRE_STATION_PAGE,
    FIRE_EQUIPMENT_PAGE,
    FIRE_HYDRANT_PAGE,
    FIRE_CISTERN_PAGE,
)
