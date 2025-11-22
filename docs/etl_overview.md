# ETL Overview

川崎市オープンデータを処理するための ETL ライフサイクルと設定方法をまとめています。README と合わせて読めば、どこに設定を書き、どの CLI を叩けばよいかを把握できます。

## ライフサイクル

```
configs/datasets.yml → download → normalize → load/meta → DB/data/
```

1. **Download**: datasets.yml に記載された URL からファイルを取得し、`data/raw/<category>/<dataset_id>/` に保存します。
2. **Normalize**: 文字コードや列名を統一した CSV を `data/normalized/...` に生成します。ZIP や Excel も内部の CSV/シートを抽出して UTF-8 に揃えます。
3. **Load & Meta**: 正規化済みファイルを DataFrame として DB に UPSERT し、処理履歴を `data/meta/...` に保存します。ハッシュが同じ場合はスキップされ、冪等性が担保されます。

## データセット定義（configs/datasets.yml）

- 必須: `category`, `url`, `type`
- 任意: `parser`, `table`, `key_fields`, `snapshot_date`, `extra`
- 形式: YAML のトップレベルまたは `datasets:` セクションに ID をキーとして記述

```yaml
wifi_2020_count:
  category: wifi          # data/ 配下のカテゴリ名、およびパイプライン判定に利用
  url: https://example.kawasaki.jp/wifi/2020.csv
  type: csv               # csv | excel | zip など
  parser: wifi_usage_parser
  table: wifi_access_counts
  key_fields:
    - date
    - spot_id
  snapshot_date: 2020-12-31
  extra:
    encoding: cp932
```

- `category` はディレクトリ分けとパイプライン選択に使います（Wi-Fi 系は `wifi`、観光 PDF は `tourism`）。
- `parser` で使用するパーサー/パイプラインを選択します。Wi-Fi は `wifi_usage_parser`、観光入込客数は `tourism_irikomi_pdf` を利用します。
- `key_fields` は UPSERT 時の主キー列です。空リストでも構いません。
- `extra` に文字コードやシート名など任意のパラメータを渡せます（各パイプラインが解釈）。

## CLI の使い方

```bash
# 定義済みデータセットの一覧
uv run python -m kawasaki_etl.main etl list

# raw のみダウンロード
uv run python -m kawasaki_etl.main etl download <dataset_id>

# download → normalize → load/meta を実行
uv run python -m kawasaki_etl.main etl run <dataset_id>

# すべてのデータセットをまとめて処理
uv run python -m kawasaki_etl.main etl run-all
```

デフォルトでは `.env` を読み込みます。別の環境ファイルを使う場合は `--dotenv staging.env` のように指定してください。

## DB 設定

- 既定では `.env` の `DATABASE_URL`（または `DB_*` 系変数）を参照します。
- `configs/db.yml` の `default` エントリでも設定できます。詳細は `src/kawasaki_etl/utils/settings.py` と `.env.example` を参照してください。

## 新しいデータセットを追加する手順

1. `configs/datasets.yml` にエントリを追加する。
2. 既存パーサーで処理できる場合はそのまま `etl run <id>` を実行。新しい形式の場合は `src/kawasaki_etl/pipelines/` にパーサーを追加し、`CLIInterface._run_pipeline`（`interfaces/cli.py`）でカテゴリ/パーサーに紐付ける。
3. 必要に応じてテーブルスキーマを用意し、`table` と `key_fields` を設定する。

## 関連ドキュメント

- メタ情報の形式: [docs/meta_store.md](meta_store.md)
- PDF 抽出ガイド: [docs/guides/pdf_extraction.md](guides/pdf_extraction.md)
- テスト・開発フロー: [docs/development/testing.md](development/testing.md)
