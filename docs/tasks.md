# 川崎市オープンデータ ETL 基盤: タスクリスト

この文書では、受け入れ条件 (Acceptance Criteria) と Definition of Done (DoD) を付与した改修タスクを一覧化します。優先度に応じて上から順に着手することを想定しています。

## グローバル DoD（共通）
- `nox -s lint typing test` が成功すること。
- 新規コードは型ヒント付きで Ruff のフォーマット/リントに違反しないこと。
- 新規ロジックには最低 1 つ以上のテストを追加すること。
- README または docs に使用方法/仕様を追記し、新しい環境変数は `.env.example` に反映すること。
- エラー時はロガー経由で分かりやすいメッセージを出し、スタックトレースが生で露出しないこと。

## タスク一覧
### T1. プロジェクト目的の明確化 & 基本ディレクトリ追加
- **概要**: リポジトリを「川崎市オープンデータの ETL & 解析基盤」と位置付け、`configs/` と `data/` ディレクトリを整備し、`.gitignore` を更新する。
- **Acceptance Criteria**
  - README を読めばデータ配置が把握でき、`data/` 配下が Git で無視される。
  - `configs/datasets.yml` にサンプルエントリがあり構造が分かる。
- **DoD**: グローバル DoD を満たし、README に目的と構造が反映されていること。
- **Status: DONE**
  - README 冒頭に川崎市オープンデータ ETL の目的とデータフローを追記し、`configs/`/`data/` の構造を明示。
  - `configs/datasets.yml`/`configs/db.yml` を追加し、`data/` 配下に raw/normalized/meta をプリセット化。
  - `.gitignore` で `data/` を無視しつつ `.gitkeep` を除外対象外にし、クローン直後からパスが把握可能にした。

### T2. DatasetConfig モデルと設定ローダーの実装
- **概要**: `configs/datasets.yml` を読み込んで内部モデルに変換する仕組み (`core/models.py`) を実装する。
- **Acceptance Criteria**
  - `python -m kawasaki_etl.main debug list-datasets` で ID 一覧が表示される。
  - 不正ケースでは CLI 上に分かりやすいエラーが出る。
- **DoD**: グローバル DoD。`tests/unit/core/test_models_or_config_loader.py` に YAML モックを使ったテストがあること。
- **Status: DONE**
  - `DatasetConfig`/`load_dataset_configs`/`get_dataset_config` を追加し、YAML 構造エラーや ID 不在時の例外を明示化。
  - Typer CLI に `debug list-datasets` を追加し、設定一覧表示と読み込み失敗時の分かりやすいメッセージを実装。
  - `tests/unit/kawasaki_etl/core/test_models_or_config_loader.py` と CLI 向けテストで正常/異常系をカバー。

### T3. ダウンロード & パス管理（core.io）の実装
- **概要**: `data/raw/{category}/{dataset_id}/` へのダウンロードと冪等性を担保する共通関数 `download_if_needed()` を実装する。
- **Acceptance Criteria**
  - `etl download <dataset_id>` で `data/raw/...` に保存される。
  - 2 回目は「既に存在するためスキップ」ログが出て再ダウンロードされない。
- **DoD**: グローバル DoD。失敗時は適切に例外処理＋ログ出力されること。
- **Status: DONE**
  - `core.io` にダウンロード処理を集約し、HTTP タイムアウトや書き込み失敗をハンドリング。
  - Typer CLI に `etl download <dataset_id>` を追加し、`data/raw/<category>/<dataset_id>/` へ保存する共通動作を提供。
  - 冪等性確認のユニットテストと CLI 経由のダウンロードテストを追加。

### T4. CSV/Excel/ZIP 正規化（core.normalize）の実装
- **概要**: 文字コード検出や CSV/Excel/ZIP 内 CSV の正規化を行い、UTF-8 に変換する共通関数を提供する。
- **Acceptance Criteria**
  - Shift-JIS/CP932 の CSV を正規化すると UTF-8 で読めるファイルが `data/normalized/...` に生成される。
  - 想定外の文字コードでは試したエンコーディングとパスを含むエラーを返す。
- **DoD**: グローバル DoD。`tests/unit/core/test_normalize.py` に正常/異常系テストがあること。

### T5. メタ情報管理（core.meta_store）の実装
- **概要**: `data/meta/` に JSON でダウンロード/処理履歴を記録し、冪等性を担保する仕組みを提供する。
- **Acceptance Criteria**
  - 同じファイルに対する 2 回目の `etl run` で「既に処理済み」と判定され二重 INSERT が起きない。
  - ファイルを更新すると新しい SHA256 で再処理される。
- **DoD**: グローバル DoD。メタファイル形式が README または docs に記載されていること。
- **Status: DONE**
  - core.meta_store を追加し、SHA256 計算・処理済み判定・メタファイル書き込みを実装。
  - docs/meta_store.md と README に JSON 形式と保存パスを記載。
  - テスト（`tests/unit/kawasaki_etl/core/test_meta_store.py`）でパス生成・ハッシュ算出・冪等判定を検証。

### T6. DB 接続 & UPSERT ロジック（core.db）の実装
- **概要**: PostgreSQL(+PostGIS) 向け接続と DataFrame の UPSERT を実装し、`.env` または `configs/db.yml` から接続情報を取得する。
- **Acceptance Criteria**
  - テスト用テーブルで主キー重複時に重複登録されず更新される。
  - 接続失敗時に明確なエラーメッセージが表示される。
- **DoD**: グローバル DoD。少なくとも 1 つのパイプラインで `upsert_dataframe` が使用されていること。

### T7. CLI への ETL コマンド追加（interfaces.cli の拡張）
- **概要**: Typer CLI に `etl list`, `etl run <dataset_id>`, `etl run-all` を追加し、既存 CLI に統合する。
- **Acceptance Criteria**
  - `uv run python -m kawasaki_etl.main --help` に ETL コマンドが表示される。
  - `uv run python -m kawasaki_etl.main etl list` で datasets.yml の ID が出力される。
- **DoD**: グローバル DoD。CLI コマンドの簡易テストが追加されていること。

### T8. 最初の CSV パイプライン（Wi-Fi 接続数）の実装
- **概要**: Wi-Fi 接続数 CSV を対象に download → normalize → DB upsert を実装する。
- **Acceptance Criteria**
  - `uv run python -m kawasaki_etl.main etl run wifi_2020_count` で raw 保存・正規化・DB 反映が行われる。
  - 2 回連続実行してもレコードが二重に増えない。
- **DoD**: グローバル DoD。Wi-Fi CSV のカラム構成とマッピングが README または docs に記載されていること。

### T9. PDF パイプラインのスケルトン実装（観光入込客数）
- **概要**: PDF → DataFrame のスケルトンを用意し、観光入込客数向けのパイプラインを追加する（初期はモック可）。
- **Acceptance Criteria**
  - `etl run tourism_r05_irikomi` が実行でき、PDF ダウンロードと正規化（モック含む）が動作する。
  - 未実装部分がある場合は CLI 上で「未実装」と分かるメッセージが出る。
- **DoD**: グローバル DoD。PDF 抽出の仕様と今後の拡張方針が docs に記載されていること。
- **Status: DONE**
  - 観光入込客数向けの `tourism_r05_irikomi` を datasets.yml に追加し、ETL CLI から実行可能にした。
  - `pdf_utils.extract_tables_from_tourism_irikomi` と観光パイプラインを実装し、未実装メッセージ付きのモック DataFrame を保存する挙動を用意。
  - PDF 抽出の方針・モック手順を docs/guides/pdf_extraction.md に整理し、MkDocs ナビに追加。

### T10. リポジトリレベルのドキュメント整備
- **概要**: README と docs を更新し、ETL フレームワークとしての使い方・構造を整理する。
- **Acceptance Criteria**
  - README だけでリポジトリの目的や CLI 実行手順が理解できる。
  - `uv run mkdocs build` が成功する。
- **DoD**: グローバル DoD。README と docs の内容が実際の構造や CLI と矛盾していないこと。

## 進め方の提案
- 最初のスプリントで **T1〜T4 + T7** を完了して「ETL 基盤の骨格」を作る。
- その後 **T8** で 1 本の CSV パイプラインを end-to-end で通し、冪等性や DB 連携を検証する。
- **T9** 以降で PDF 系パイプラインを横展開し、datasets.yml / db.yml の拡張とともにドキュメントを充実させる。
