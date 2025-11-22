# 川崎市オープンデータ ETL 基盤: 設計

この文書では、ETL 基盤のアーキテクチャ設計とコンポーネント設計方針を示します。既存の clean-python-interfaces テンプレートに ETL ドメインを追加する際のガイドとして利用します。

## アーキテクチャ概要
- **レイヤ構造**
  - `core`: ETL 共通部品（設定ロード、IO、正規化、DB、メタ管理、PDF ヘルパ）
  - `pipelines`: データセットカテゴリ別の ETL 実装（例: Wi-Fi, 観光, 保育）
  - `interfaces`: Typer CLI / FastAPI REST からパイプラインを呼び出す入口
- **設定**
  - `configs/datasets.yml`: データセットごとの定義（ID, URL, 種別, テーブル, キー列, parser 等）
  - `configs/db.yml`: DB 接続 alias と URL/schema の対応を保持
  - `.env.example`: DB_DSN などの環境変数テンプレート
- **データ配置**
  - `data/raw/`: ダウンロードした生ファイル
  - `data/normalized/`: UTF-8 CSV など正規化済みデータ
  - `data/meta/`: 処理済みファイルのメタ情報 (JSON)

## コンポーネント設計
### core.models
- `DatasetConfig` dataclass を定義。
- 属性例: `dataset_id`, `category`, `url`, `type`, `parser`, `table`, `key_fields`, `snapshot_date`, `extra`。
- YAML ローダー (`load_dataset_configs`, `get_dataset_config`) を同ファイルまたは `config_loader` として提供。

### core.io
- `get_raw_path(dataset: DatasetConfig) -> Path`
- `download_file(url: str, dest_path: Path) -> None`
- `download_if_needed(dataset: DatasetConfig) -> Path`
- 既存のダウンロードロジックを整理し、サイズ/タイムスタンプまたはハッシュで冪等性を担保。

### core.normalize
- `detect_encoding_and_read_csv(path: Path) -> pd.DataFrame`
- `normalize_csv(path: Path, dest: Path) -> pd.DataFrame`
- `normalize_excel(path: Path, dest_dir: Path) -> dict[str, Path]`
- `normalize_zip_of_csv(zip_path: Path, dest_dir: Path) -> list[Path]`
- 列名正規化ヘルパ（全角→半角、前後空白除去など）を含める。

### core.pdf_utils
- PDF 抽出の共通関数群。
- 例: `extract_tables_from_tourism_irikomi(pdf_path: Path) -> pd.DataFrame`（初期はモックでも可）。

### core.db
- `get_engine(alias: str = "default")` で SQLAlchemy Engine を返す。
- `upsert_dataframe(df, table_name, key_fields, engine)` で PostgreSQL ON CONFLICT を用いた UPSERT を実装。
- 接続失敗やクエリ失敗時はロガー経由で明確なエラーを返す。

### core.meta_store
- `get_meta_path(dataset: DatasetConfig, raw_path: Path) -> Path`
- `mark_loaded(dataset, raw_path, sha256, processed_at)`
- `is_already_loaded(dataset, raw_path, sha256) -> bool`
- ダウンロード/処理の冪等性をメタファイルで担保。

### pipelines
- カテゴリ別に `pipelines/<category>.py` を用意し、`run_<dataset>` 関数を実装。
- 例: `run_wifi_count`, `run_tourism_irikomi`。
- 内部で `download_if_needed` → `normalize_*` → `upsert_dataframe` → `meta_store` を組み合わせる。

### interfaces
- Typer ベース CLI (`interfaces/cli.py`) に `etl list`, `etl run <dataset_id>`, `etl run-all` を追加。
- FastAPI ベース REST API (`interfaces/restapi.py`) には将来的に `/etl/*` を追加できるフックを残す。

## エラー処理とログ
- 例外はロガー経由で通知し、CLI から見て分かりやすいメッセージを返す。
- ダウンロード失敗、YAML 形式不正、DB 接続失敗などケース別にハンドリングする。

## テスト方針
- 新規ロジックには最低 1 つのテストを追加（特に core と CLI/pipelines）。
- 例: `tests/unit/core/test_models_or_config_loader.py` に YAML 読み込みテスト、`tests/unit/core/test_normalize.py` に正常/異常系テスト。

## 将来の拡張
- PDF 解析に camelot/tabula などを導入する際は `pdf_utils` で統一的に扱う。
- datasets.yml に複数 DB alias や追加カテゴリを増やせるよう拡張。
- mkdocs に ETL 概要・データセット追加手順・パイプライン一覧を追加し、ドキュメント中心の運用を目指す。
