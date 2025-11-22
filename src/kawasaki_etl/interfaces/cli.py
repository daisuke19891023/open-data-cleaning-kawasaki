"""CLI interface implementation using Typer."""

from pathlib import Path

import typer
from rich.console import Console

from kawasaki_etl.core import (
    DatasetConfigError,
    DownloadError,
    download_if_needed,
    get_dataset_config,
    load_dataset_configs,
)
from kawasaki_etl.models.io import WelcomeMessage

from .base import BaseInterface

# Configure console for better test compatibility
# Force terminal mode even in non-TTY environments
console = Console(force_terminal=True, force_interactive=False)


class CLIInterface(BaseInterface):
    """Command Line Interface implementation."""

    def __init__(self, datasets_config_path: Path | None = None) -> None:
        """Initialize the CLI interface."""
        super().__init__()  # Call BaseComponent's __init__ for logger initialization
        self.datasets_config_path = datasets_config_path or Path("configs/datasets.yml")
        self.app = typer.Typer(
            name="kawasaki_etl",
            help="Kawasaki ETL CLI",
            add_completion=False,
        )
        self._setup_commands()

    @property
    def name(self) -> str:
        """Get the interface name.

        Returns:
            str: The interface name

        """
        return "CLI"

    def _setup_commands(self) -> None:
        """Set up CLI commands."""
        # Set the default command to welcome
        self.app.command(name="welcome")(self.welcome)

        debug_app = typer.Typer(name="debug", help="デバッグ・検証用のサブコマンド")
        debug_app.command(name="list-datasets")(self.list_datasets)
        self.app.add_typer(debug_app, name="debug")

        etl_app = typer.Typer(name="etl", help="ETL パイプライン関連コマンド")
        etl_app.command(name="download")(self.download_dataset)
        self.app.add_typer(etl_app, name="etl")

        # Add a callback that shows welcome when no command is specified
        self.app.callback(invoke_without_command=True)(self._main_callback)

    def _main_callback(self, ctx: typer.Context) -> None:  # pragma: no cover
        """Run when no subcommand is provided."""
        if ctx.invoked_subcommand is None:
            self.welcome()
            # Ensure we exit cleanly after showing welcome
            raise typer.Exit(0)

    def welcome(self) -> None:
        """Display welcome message."""
        msg = WelcomeMessage()
        # Use console for output (configured for E2E test compatibility)
        console.print(msg.message)
        console.print(msg.hint)
        # Force flush to ensure output is visible
        console.file.flush()

    def list_datasets(self) -> None:
        """List dataset IDs defined in configs/datasets.yml."""
        try:
            configs = load_dataset_configs(self.datasets_config_path)
        except DatasetConfigError as exc:
            self.logger.error("Failed to load dataset configs", error=str(exc))
            typer.secho(
                f"設定読み込みエラー: {exc}",
                err=True,
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1) from exc

        if not configs:
            console.print(
                "データセットが定義されていません。\n"
                "configs/datasets.yml を確認してください。",
            )
            return

        console.print("登録済みデータセット:")
        for dataset_id, dataset_config in sorted(configs.items()):
            console.print(
                f"- {dataset_id} ({dataset_config.category}/{dataset_config.type})",
            )

    def download_dataset(self, dataset_id: str) -> None:
        """Download raw data for the specified dataset."""
        try:
            dataset = get_dataset_config(dataset_id, self.datasets_config_path)
        except DatasetConfigError as exc:
            self.logger.error(
                "Unknown dataset id",
                dataset_id=dataset_id,
                error=str(exc),
            )
            typer.secho(
                f"データセット '{dataset_id}' が見つかりません: {exc}",
                err=True,
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1) from exc

        try:
            dest_path = download_if_needed(dataset)
        except DownloadError as exc:
            self.logger.error(
                "Failed to download dataset",
                dataset_id=dataset_id,
                url=dataset.url,
                error=str(exc),
            )
            typer.secho(
                f"ダウンロードに失敗しました: {exc}",
                err=True,
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1) from exc

        console.print(f"ダウンロード先: {dest_path}")

    def run(self) -> None:
        """Run the CLI interface."""
        # Let Typer handle the command parsing
        self.app()
