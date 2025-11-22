# 川崎市オープンデータ ETL 基盤: 仕様

この文書では、川崎市オープンデータを対象とした ETL 基盤の仕様を整理します。開発の目的、対象ディレクトリ、主要なコンポーネント、および全体の要求事項をまとめています。

## プロジェクトの目的
- 川崎市が公開する各種オープンデータを安定的かつ再現可能に収集・加工・格納すること。
- CLI/REST API を備えた既存のアプリ骨格に ETL ドメインを組み込み、横展開しやすいパイプライン群を提供すること。

## 期待するディレクトリ構成（追加部分）
```
open-data-cleaning-kawasaki/
├── configs/
│   ├── datasets.yml        # データセット定義（ID / URL / 種別 / テーブル名 など）
│   └── db.yml              # DB 接続定義（alias → URL / schema）
├── data/                   # Git 管理外
│   ├── raw/                # ダウンロードした生ファイル
│   ├── normalized/         # UTF-8 CSV など整形済み中間成果物
│   └── meta/               # メタ情報（ハッシュ、処理済みフラグなど）
└── src/kawasaki_etl/
    ├── core/               # ETL 共通部品
    │   ├── models.py       # DatasetConfig 等の dataclass
    │   ├── io.py           # download, パス生成, ZIP 展開
    │   ├── normalize.py    # CSV/Excel/ZIP 正規化
    │   ├── pdf_utils.py    # PDF 抽出の共通関数
    │   ├── db.py           # DB 接続 & UPSERT
    │   └── meta_store.py   # 処理済みファイルのメタ管理
    ├── pipelines/          # データセットカテゴリ別 ETL
    │   ├── wifi.py         # Wi-Fi 接続数 CSV パイプライン
    │   ├── tourism.py      # 観光入込客数 PDF パイプライン
    │   ├── childcare.py    # 保育系 PDF パイプライン
    │   └── ...
    └── interfaces/
        ├── cli.py          # 既存 CLI に etl コマンド群を追加
        └── restapi.py      # 必要に応じて /etl/* API を追加
```

## ETL フローの概要
1. `configs/datasets.yml` にデータセット（ID、URL、種別、テーブル名、キー列など）を定義。
2. CLI から `uv run python -m kawasaki_etl.main etl run <dataset_id>` を実行。
3. `core.io` が `data/raw/` にファイルをダウンロード。
4. `core.normalize` / `core.pdf_utils` が `data/normalized/` に標準化済みの DataFrame を出力。
5. `core.db` が PostgreSQL(+PostGIS) に UPSERT（冪等）。
6. `meta_store` が処理済みファイルを記録し、次回処理をスキップ可能にする。

## グローバル Definition of Done（DoD）
1. **ビルド/テスト**: `uv sync` 済み環境で `nox -s lint typing test` が成功すること。
2. **型 & スタイル**: 新規コードは型ヒント付きで Ruff のフォーマット/リントに違反しないこと。
3. **テスト**: 新規ロジック（特に core/pipelines/cli）は最低 1 つ以上のテストを追加すること。
4. **ドキュメント**: README または docs に使用方法/仕様を追記し、新しい環境変数は `.env.example` にも反映すること。
5. **ログ & エラー処理**: エラーはロガー経由で分かりやすく記録され、スタックトレースが生で露出しないこと。

## 受け入れ基準の全体像
- datasets.yml から CLI 経由で ID 一覧や個別実行が確認できる。
- data ディレクトリにダウンロード/正規化/メタが保存され、再実行時は冪等にスキップされる。
- UPSERT により DB に重複が生じず、接続失敗時は明確なエラーを返す。
- README / docs がディレクトリ構造と CLI/API の振る舞いを説明している。

## 想定するインターフェース
- **CLI**: `etl list`, `etl run <dataset_id>`, `etl run-all` をサポートし、補助的に `debug list-datasets` などのデバッグコマンドを提供。
- **REST API**: 将来的に `/etl/*` エンドポイントを追加可能な設計とする。

## 想定データセットの例
- Wi-Fi 接続数 CSV（`wifi_2020_count` など）
- 観光入込客数 PDF（`tourism_r05_irikomi` など）
- 保育関連 PDF（`childcare_*`）

## 今後の拡張方針
- まず CSV ベースのパイプラインで end-to-end を通し、PDF 系を段階的に実装。
- datasets.yml / db.yml に alias を増やし、複数 DB やカテゴリ追加を容易にする。
- mkdocs で ETL 概要やデータセット追加手順を整備し、開発者オンボーディングを簡素化する。
