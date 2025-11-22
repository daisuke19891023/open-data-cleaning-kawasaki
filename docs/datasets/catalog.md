# データセットカタログ管理ガイド

本ドキュメントでは、川崎市オープンデータカタログのカテゴリリンクや各データセットの URL を一元管理し、`configs/` とローダーの整備状況に応じて消込できるようにする運用ルールをまとめます。ユーザーから共有されたレポート内のリンク・メモを下表へ転記してください。

## 管理の考え方
- **カテゴリリンク**: オープンデータカタログ内の各カテゴリページへのリンクを一覧化します。レポートに掲載された URL を転記し、後続のデータセット表から参照できるようにします。
- **データセット表**: レポートで列挙されたデータセットをカテゴリごとに記録し、取り込み準備状況（未着手/確認中/取り込み準備OK/運用中）をステータス列で管理します。
- **消込ルール**: 以下の条件を満たしたらステータスを「取り込み準備OK」または「運用中」に更新します。
  - `configs/datasets.yml` に `dataset_id` と URL/パーサーが登録済み。
  - 対応するローダー・パイプラインが `src/kawasaki_etl/pipelines/` などに存在し、`python -m kawasaki_etl.main debug list-datasets` に表示される。

## カテゴリリンクの控え
レポートに記載されているカテゴリごとのカタログ URL をここに転記します。防災・防犯や医療・介護・福祉など、追加カテゴリがあれば行を増やしてください。

| カテゴリ | カタログ URL | 備考 |
| --- | --- | --- |
| 医療・介護・福祉 | https://www.city.kawasaki.jp/main/opendata/opendata_category_1.html | 代表的なデータセットの URL を下記で管理 |
| 防災・防犯 | https://www.city.kawasaki.jp/main/opendata/opendata_category_2.html | 下記テーブルに全データセットを列挙 |
| 観光・イベント | https://www.city.kawasaki.jp/main/opendata/opendata_category_4.html |  |
| 住まい・生活・引越し | https://www.city.kawasaki.jp/main/opendata/opendata_category_6.html |  |
| 子育て・教育 | https://www.city.kawasaki.jp/main/opendata/opendata_category_7.html |  |
| 公共施設・都市計画 | https://www.city.kawasaki.jp/main/opendata/opendata_category_8.html |  |
| 人口・世帯 | https://www.city.kawasaki.jp/main/opendata/opendata_category_9.html |  |
| 環境・エネルギー | https://www.city.kawasaki.jp/main/opendata/opendata_category_10.html |  |
| 情報通信・先端技術 | https://www.city.kawasaki.jp/main/opendata/opendata_category_11.html |  |
| 産業 | https://www.city.kawasaki.jp/main/opendata/opendata_category_13.html |  |
| 地図・地理空間 | https://www.city.kawasaki.jp/main/opendata/opendata_category_18.html |  |
| その他 | https://www.city.kawasaki.jp/main/opendata/opendata_category_19.html |  |

## データセット管理テーブル
レポートで整理されたデータセットをカテゴリ別に追記してください。ステータスは `未着手` / `確認中` / `取り込み準備OK` / `運用中` などで運用します。`dataset_id` が付与できるものは `configs/datasets.yml` と一致させると消込が容易になります。

| カテゴリ | データセット名/説明 | データセット URL | 形式 | dataset_id | ステータス | メモ |
| --- | --- | --- | --- | --- | --- | --- |
| 防災・防犯 | （例: 避難所一覧） | （レポートの URL を転記） | CSV 等 | （未設定なら空欄） | 未着手 |  |
| 防災・防犯 | 【2022年度】応急給水拠点一覧（令和7年4月1日時点） | https://www.city.kawasaki.jp/800/page/0000085691.html#opendata_dataset_3 | CSV | emergency_water_points_r7_04 | 取り込み準備OK | `configs.disaster_prevention.WATER_SUPPLY_PAGE` を download_opendata_page で取得可能 |
| 防災・防犯 | 【2021年度】資料 | https://www.city.kawasaki.jp/601/page/0000036154.html#opendata_dataset_5 | XLSX | designated_evacuation_sites_r3_08 | 取り込み準備OK | `configs.disaster_prevention.EVACUATION_PAGE` を download_opendata_page で取得可能 |
| 防災・防犯 | 【2021年度】内水ハザードマップ（浸水想定区域）データ | https://www.city.kawasaki.jp/800/page/0000133400.html#opendata_dataset_3 | ZIP | internal_flood_hazard_map | 取り込み準備OK | `configs.disaster_prevention.HAZARD_PAGE` を download_opendata_page で取得可能 |
| 防災・防犯 | 【2015年度】消防署・出張所一覧 | https://www.city.kawasaki.jp/170/page/0000058746.html#opendata_dataset_3 | CSV | fire_station_list_h27_10 | 取り込み準備OK | `configs.disaster_prevention.FIRE_STATION_PAGE` を download_opendata_page で取得可能 |
| 防災・防犯 | 【2015年度】消防団（器具置場）一覧 | https://www.city.kawasaki.jp/170/page/0000058746.html#opendata_dataset_4 | CSV | fire_brigade_storage_h27_10 | 取り込み準備OK | `configs.disaster_prevention.FIRE_EQUIPMENT_PAGE` を download_opendata_page で取得可能 |
| 防災・防犯 | 【2015年度】消火栓（公設）一覧 | https://www.city.kawasaki.jp/170/page/0000058746.html#opendata_dataset_5 | CSV | public_fire_hydrants_h27_10 | 取り込み準備OK | `configs.disaster_prevention.FIRE_HYDRANT_PAGE` を download_opendata_page で取得可能 |
| 防災・防犯 | 【2015年度】防火水槽（公設）一覧 | https://www.city.kawasaki.jp/170/page/0000058746.html#opendata_dataset_6 | CSV | public_fire_cisterns_h27_10 | 取り込み準備OK | `configs.disaster_prevention.FIRE_CISTERN_PAGE` を download_opendata_page で取得可能 |
| 医療・介護・福祉 | （例: 医療機関一覧） | （レポートの URL を転記） | CSV/Excel 等 | （未設定なら空欄） | 未着手 | 代表的なものを抜粋 |
| … | … | … | … | … | … | … |

## 消込済み（設定・ローダーあり）
既に `configs/` とローダーで取り込み準備ができているものを記録します。レポートで挙がっているデータセットと突合し、二重登録を避けてください。

| dataset_id | カテゴリ | データセット URL | パーサー/パイプライン | ステータス | 備考 |
| --- | --- | --- | --- | --- | --- |
| wifi_2020_count | wifi | https://ckan.smartcity.kawasaki.jp/dataset/2f0b8ebc-d1a1-4b96-957c-969d5c6929b8/resource/6c4efb03-2d0b-43e8-92f4-e6e56cff4f1a/download/0005704001_000559556.csv | wifi_usage_parser / pipelines.opendata | 取り込み準備OK | Wi-Fi 接続数 CSV。`etl run wifi_2020_count` で実行可能 |
| tourism_r05_irikomi | tourism | https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf | tourism_irikomi_pdf / pipelines.tourism | 取り込み準備OK | 観光入込客数 PDF（モック）。`etl run tourism_r05_irikomi` で実行可能 |

## 運用メモ
- カタログ側で URL が更新された場合は、上表と `configs/datasets.yml` の両方を更新し、ステータスを「確認中」に戻すと差分を追いやすくなります。
- 取り込み済みデータの保存先は `data/raw/<category>/<dataset_id>/` および `data/normalized/<category>/<dataset_id>/` です。`data/meta/` にはハッシュ付きの処理履歴が残るため、更新検知にも利用できます。
- テーブルのフォーマットを変更する場合は mkdocs ナビゲーション更新も忘れずに行ってください。
