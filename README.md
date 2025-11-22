# Kawasaki ETL

川崎市オープンデータの収集・正規化・格納を行う ETL & 解析基盤です。`configs/datasets.yml` にデータセット定義を記述すると、CLI からダウンロード/正規化/DB 連携のパイプラインを順次拡張できる構成になっています。

## データフロー概要

```
configs/datasets.yml
        |
        v
[Download]    -> data/raw/<category>/<dataset_id>/
        |
        v
[Normalize]   -> data/normalized/<category>/<dataset_id>/
        |
        v
[Load/Analyze] -> DB (configs/db.yml) + data/meta/ で処理履歴管理
```

データ配置はリポジトリ内の `data/` ディレクトリに整理済みで、クローン直後からパスが分かります（Git では無視されるため生データは追跡されません）。

## Features

-   **Multiple Interface Types**: Support for CLI and REST API interfaces
-   **Flexible Configuration**: Environment-based configuration with `.env` file support
-   **Structured Logging**: Advanced logging with OpenTelemetry integration
-   **Modern Python**: Built with Python 3.13+ and modern tooling
-   **Comprehensive Testing**: Unit, API, and E2E test coverage
-   **Type Safety**: Full type hints with strict Pyright checking
-   **Code Quality**: Automated linting and formatting with Ruff
-   **Dependency Management**: Managed with uv for fast, reliable builds

## Project Structure

```
kawasaki_etl/
├── configs/                  # YAML-based configs (Git で管理)
│   ├── datasets.yml          # データセット定義
│   └── db.yml                # DB 接続テンプレート
├── data/                     # 取得データ・正規化データ・メタ情報（Git ignore）
│   ├── raw/
│   ├── normalized/
│   └── meta/
├── src/kawasaki_etl/         # Main application code
│   ├── __init__.py             # Package initialization
│   ├── app.py                  # Application entry point
│   ├── base.py                 # Base component class
│   ├── main.py                 # CLI entry point with --dotenv support
│   ├── types.py                # Type definitions
│   ├── core/                   # ETL core (config loader, etc.)
│   │   ├── __init__.py
│   │   └── models.py
│   ├── interfaces/             # Interface implementations
│   │   ├── __init__.py
│   │   ├── base.py            # Base interface class
│   │   ├── cli.py             # CLI interface using Typer
│   │   ├── factory.py         # Interface factory pattern
│   │   └── restapi.py         # REST API interface using FastAPI
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   ├── api.py             # API response models
│   │   └── io.py              # I/O models (e.g., WelcomeMessage)
│   └── utils/                  # Utility modules
│       ├── __init__.py
│       ├── file_handler.py     # File handling utilities
│       ├── logger.py           # Structured logging setup
│       ├── otel_exporter.py    # (removed) OpenTelemetry exporter (removed for stability)
│       └── settings.py         # Application settings
├── tests/                       # Test suite
│   ├── unit/                   # Unit tests
│   ├── api/                    # API tests
│   └── e2e/                    # End-to-end tests
├── docs/                        # Documentation
├── constraints/                 # Dependency constraints
├── .env                        # Environment configuration (not in git)
├── .env.example                # Example environment configuration
├── pyproject.toml              # Project configuration
├── noxfile.py                  # Task automation
├── CLAUDE.md                   # AI assistant instructions
└── README.md                   # This file
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

### Running the Application

```bash
# Run with default settings (uses .env file)
uv run python -m kawasaki_etl.main

# Run with custom environment file
uv run python -m kawasaki_etl.main --dotenv prod.env

# Show help
uv run python -m kawasaki_etl.main --help
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

取得したデータは `data/raw/<category>/<dataset_id>/`, 正規化後は `data/normalized/...`, メタ情報は `data/meta/` に配置します。`data/` 配下は `.gitignore` により追跡対象外です。

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
