# Kawasaki ETL

川崎市オープンデータを「ダウンロード → 正規化 → データベース連携」まで一気通貫で扱うための ETL フレームワークです。`configs/datasets.yml` にデータセット定義を書くだけで Typer ベースの CLI からパイプラインを実行でき、Wi-Fi 接続数や観光入込客数などのデータ取得・蓄積を自動化します。

## 何ができるか（最短 3 ステップ）

1. 依存関係を用意

    ```bash
    uv sync
    cp .env.example .env
    ```

2. データセット一覧を確認

    ```bash
    uv run python -m kawasaki_etl.main etl list
    ```

3. Wi-Fi 接続数パイプラインを実行

    ```bash
    uv run python -m kawasaki_etl.main etl run wifi_2020_count
    ```

## ETL アーキテクチャ概要

```mermaid
flowchart TD
    A[configs/datasets.yml
    dataset_id, URL, parser, category] --> B[Download
    data/raw/<category>/<dataset_id>/]
    B --> C[Normalize
    data/normalized/<category>/<dataset_id>/]
    C --> D[Load/Analyze
    DB (configs/db.yml)
    meta => data/meta/]
```

- `configs/datasets.yml` にパイプラインの入力（URL・形式・パーサー名など）を記述します。
- `data/` 配下に raw/normalized/meta を自動生成し、ファイルのハッシュで再処理要否を判定します（Git では無視）。
- CLI から `etl download`/`etl run`/`etl run-all` を叩くと、定義に基づき各ステップを順次実行します。

### Wi-Fi 接続数パイプライン

`wifi_2020_count` など Wi-Fi 系データセットは以下のカラムに正規化され、DB の `wifi_access_counts` テーブルへ UPSERT されます。

- `dataset_id`: datasets.yml の ID（例: `wifi_2020_count`）
- `date`: 接続日（YYYY-MM-DD）
- `spot_id`: スポット識別子（CSV の「スポットID」などをマッピング）
- `spot_name`: スポット名称
- `connection_count`: 当日の接続回数（数値化・欠損は 0 扱い）
- `snapshot_date`: データ提供側が示すスナップショット日（存在する場合）

主キーは `date` と `spot_id` の組み合わせで、2 回同じ CSV を流してもレコードは重複せず更新されます。

## 主な特徴

-   **ETL 向け CLI を標準搭載**: Typer 製の `etl download`/`etl run`/`etl run-all` が利用可能
-   **設定駆動型**: YAML (`configs/datasets.yml`, `configs/db.yml`) のみでデータセットと DB を差し替え可能
-   **メタ情報による冪等性**: `data/meta/` に処理履歴を残し、同じファイルはスキップ
-   **型安全で近代的な Python**: Python 3.13、Ruff、Pyright、uv で統一

## データディレクトリ構造

```
data/                           # Git で無視される動的データ
├── raw/<category>/<dataset_id>/        # ダウンロードした生ファイル
├── normalized/<category>/<dataset_id>/ # 文字コードや列名を正規化した CSV
└── meta/<category>/<dataset_id>/       # 処理済みハッシュやタイムスタンプの JSON
```

`data/` はクローン直後からディレクトリのみが存在し、ファイルは ETL 実行時に生成されます。メタファイルのフォーマット詳細は [docs/meta_store.md](docs/meta_store.md) を参照してください。

## プロジェクト構成

```
kawasaki_etl/
├── configs/                     # Git 管理される設定
│   ├── datasets.yml             # データセット定義（必須項目は docs/etl_overview.md を参照）
│   └── db.yml                   # DB 接続情報テンプレート（ENV で上書き可能）
├── src/kawasaki_etl/
│   ├── main.py                  # エントリーポイント（--dotenv 対応）
│   ├── interfaces/              # CLI/REST API 実装
│   │   └── cli.py               # Typer 製 CLI。`etl` サブコマンドを提供
│   ├── core/                    # 設定・IO・正規化・メタ情報
│   └── pipelines/               # Wi-Fi などのデータセット固有パイプライン
├── tests/                       # Unit/API/E2E テスト
├── docs/                        # MkDocs ベースのドキュメント
├── data/                        # raw/normalized/meta（Git ignore）
├── mkdocs.yml                   # ドキュメントサイト設定
├── pyproject.toml               # 依存・ツール設定
└── README.md
```

## Quick Start

### Prerequisites

-   Python 3.13 or higher
-   uv (Python package manager)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd kawasaki_etl

# Create virtual environment and install dependencies
uv sync

# Copy environment configuration
cp .env.example .env

# Edit .env with your configuration
```

### Running the Application (CLI)

```bash
# CLI 全体のヘルプを表示
uv run python -m kawasaki_etl.main --help

# 登録済みデータセットの一覧を表示
uv run python -m kawasaki_etl.main etl list

# raw データだけダウンロード
uv run python -m kawasaki_etl.main etl download wifi_2020_count

# ETL を一括実行（download → normalize → load/meta）
uv run python -m kawasaki_etl.main etl run wifi_2020_count

# すべてのデータセットを順番に処理
uv run python -m kawasaki_etl.main etl run-all

# .env 以外の設定を使う場合
uv run python -m kawasaki_etl.main --dotenv prod.env etl list
```

## Configuration

### Dataset definitions (configs/datasets.yml)

`configs/datasets.yml` ではデータセットごとにカテゴリー、URL、形式、処理用パーサー名などを宣言します。サンプル:

```yaml
wifi_2020_count:
  category: connectivity
  url: https://opendata.example.kawasaki.jp/wifi/count_2020.csv
  type: csv
  parser: wifi_usage_parser
  table: wifi_connection_counts
  key_fields:
    - date
    - spot_id
  snapshot_date: 2020-12-31
  extra:
    encoding: utf-8
```

取得したデータは `data/raw/<category>/<dataset_id>/`, 正規化後は `data/normalized/...`, メタ情報は `data/meta/` に配置します。`data/` 配下は `.gitignore` により追跡対象外です。メタファイルの JSON 形式と保存パスの詳細は [docs/meta_store.md](docs/meta_store.md) を参照してください。

### Environment Variables

Configuration is managed through environment variables. See `.env.example` for all available options:

| Variable         | Description                                  | Default | Options                                         |
| ---------------- | -------------------------------------------- | ------- | ----------------------------------------------- |
| `INTERFACE_TYPE` | Interface to use                             | `cli`   | `cli`, `restapi`                                |
| `LOG_LEVEL`      | Logging level                                | `INFO`  | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `LOG_FORMAT`     | Log output format                            | `json`  | `json`, `console`, `plain`                      |
| `LOG_FILE_PATH`  | Log file path                                | None    | Any valid file path                             |
| `OTEL_*`         | [Deprecated] OpenTelemetry exporter settings | -       | Removed                                         |

### Using Custom Environment Files

You can specify custom environment files using the `--dotenv` option:

```bash
# Development environment
uv run python -m kawasaki_etl.main --dotenv dev.env

# Production environment
uv run python -m kawasaki_etl.main --dotenv prod.env

# Testing environment
uv run python -m kawasaki_etl.main --dotenv test.env
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
uv sync --extra dev

# Install pre-commit hooks
uv run pre-commit install
```

### Development Commands

| Command              | Description         |
| -------------------- | ------------------- |
| `nox -s lint`        | Run code linting    |
| `nox -s format_code` | Format code         |
| `nox -s typing`      | Run type checking   |
| `nox -s test`        | Run all tests       |
| `nox -s security`    | Run security checks |
| `nox -s docs`        | Build documentation |
| `nox -s ci`          | Run all CI checks   |

### Testing

```bash
# Run all tests
nox -s test

# Run specific test file
uv run pytest tests/unit/kawasaki_etl/test_app.py

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

### Code Quality

The project maintains high code quality standards:

-   **Type Checking**: Strict Pyright type checking
-   **Linting**: Comprehensive Ruff rules
-   **Formatting**: Automated with Ruff formatter
-   **Testing**: 80% minimum coverage requirement
-   **Security**: Regular security scanning

## Interface Types

### CLI Interface

The default interface provides a command-line interface using Typer:

```bash
# Run CLI interface
INTERFACE_TYPE=cli uv run python -m kawasaki_etl.main
```

Features:

-   Interactive command-line interface
-   Rich terminal output
-   Help documentation
-   Command completion

Common ETL commands:

```bash
# Download raw data for the given dataset ID
uv run python -m kawasaki_etl.main etl download wifi_2020_count

# データは data/raw/<category>/<dataset_id>/ 以下に保存されます
```

### REST API Interface

The REST API interface provides HTTP endpoints using FastAPI:

```bash
# Run REST API interface
INTERFACE_TYPE=restapi uv run python -m kawasaki_etl.main
```

Features:

-   OpenAPI documentation
-   Automatic request validation
-   JSON responses
-   Async support

## Logging

The application uses structured logging with multiple output formats:

### JSON Format (Production)

```json
{
    "timestamp": "2025-07-20T10:30:45.123Z",
    "level": "info",
    "logger": "kawasaki_etl.app",
    "message": "Application started",
    "interface": "cli"
}
```

### Console Format (Development)

```
2025-07-20 10:30:45 [INFO] kawasaki_etl.app: Application started interface=cli
```

### OpenTelemetry Integration

When enabled, logs can be exported to OpenTelemetry collectors:

```bash
# Enable OTLP export
# OpenTelemetry exporter was removed. Trace context may still be included if OTEL is present.
```

## Documentation

ETL の流れや datasets.yml の書き方は [docs/etl_overview.md](docs/etl_overview.md) にまとめています。

### Building Documentation

```bash
# Build with Sphinx (API documentation)
nox -s docs

# Build with MkDocs (user guide)
uv run mkdocs build

# Serve documentation locally
uv run mkdocs serve
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run quality checks (`nox -s ci`)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Guidelines

-   Follow conventional commits
-   Maintain test coverage above 80%
-   Ensure all type checks pass
-   Update documentation as needed
-   Add tests for new features

### Pre-commit Setup

This project uses pre-commit hooks to ensure code quality. The hooks run automatically before each commit.

#### Installation

```bash
# Install pre-commit hooks
uv run pre-commit install
```

#### Manual Run

```bash
# Run on all files
uv run pre-commit run --all-files

# Run on staged files only
uv run pre-commit run
```

#### Hook Configuration

The pre-commit hooks use nox to ensure consistency with the project's configuration:

-   **ruff format**: Formats code according to `pyproject.toml` settings
-   **ruff lint**: Checks and fixes linting issues based on `pyproject.toml` rules
-   **pyright**: Type checks the code using project settings

All hooks respect the configuration in `pyproject.toml`, ensuring no divergence between pre-commit and regular development commands.

### Testing Helpers

This project includes testing helpers to make debugging easier:

#### Pexpect Debug Helper

For E2E tests using pexpect, use the debug helper:

```python
from tests.helpers.pexpect_debug import run_cli_with_debug

# Run with debug output enabled
output, exitstatus = run_cli_with_debug(
    "python -m kawasaki_etl.main --help",
    env=clean_env,
    timeout=10,
    debug=True,  # Enable debug output
)
```

Enable debug mode in CI by setting `PYTEST_DEBUG=1` environment variable.

### GitHub Actions Integration

This project includes a GitHub Actions workflow for Claude Code integration (`.github/workflows/claude.yml`).

**⚠️ Current Status (2025-07-20)**: The `claude-code-action@beta` is experiencing issues where the Claude CLI is not properly installed in the GitHub Actions environment. Until Anthropic fixes this issue, the workflow will not function correctly. You can still use Claude Code manually through the web interface.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

-   Built with modern Python tooling
-   Inspired by clean architecture principles
-   Designed for extensibility and maintainability
