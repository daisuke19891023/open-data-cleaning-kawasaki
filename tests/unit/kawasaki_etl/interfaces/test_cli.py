"""Tests for CLI interface implementation."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import typer
from typer.testing import CliRunner

from kawasaki_etl.interfaces.base import BaseInterface
from kawasaki_etl.interfaces.cli import CLIInterface

runner = CliRunner()


class TestCLIInterface:
    """Test CLI interface functionality."""

    def test_cli_interface_inherits_base(self) -> None:
        """Test that CLIInterface inherits from BaseInterface."""
        assert issubclass(CLIInterface, BaseInterface)

    def test_cli_interface_has_name(self) -> None:
        """Test that CLIInterface has correct name."""
        cli = CLIInterface()
        assert cli.name == "CLI"

    def test_cli_interface_has_typer_app(self) -> None:
        """Test that CLIInterface has Typer app."""
        cli = CLIInterface()
        assert hasattr(cli, "app")
        assert isinstance(cli.app, typer.Typer)

    def test_cli_welcome_command(self) -> None:
        """Test CLI welcome command functionality."""
        cli = CLIInterface()

        # Mock the console output
        with patch("kawasaki_etl.interfaces.cli.console") as mock_console:
            cli.welcome()

            # Check that welcome message was printed (should be called twice)
            assert mock_console.print.call_count == 2
            # First call is the welcome message
            first_call = mock_console.print.call_args_list[0][0]
            assert "Welcome to Kawasaki ETL!" in str(first_call)
            # Second call is the hint
            second_call = mock_console.print.call_args_list[1][0]
            assert "Type --help for more information" in str(second_call)

    def test_cli_run_method(self) -> None:
        """Test CLI run method executes typer app."""
        cli = CLIInterface()

        # Mock the typer app
        cli.app = MagicMock()

        cli.run()

        cli.app.assert_called_once()

    def test_list_datasets_command_outputs_ids(self, tmp_path: Path) -> None:
        """list-datasets should show IDs from the config file."""
        datasets_path = tmp_path / "datasets.yml"
        datasets_path.write_text(
            """
            datasets:
              wifi_counts:
                category: connectivity
                url: https://example.com/wifi.csv
                type: csv
            """,
            encoding="utf-8",
        )

        cli = CLIInterface(datasets_config_path=datasets_path)
        result = runner.invoke(cli.app, ["debug", "list-datasets"])

        assert result.exit_code == 0
        assert "wifi_counts" in result.stdout

    def test_list_datasets_command_handles_invalid_config(self, tmp_path: Path) -> None:
        """Invalid configs should surface clear error messages."""
        datasets_path = tmp_path / "datasets.yml"
        datasets_path.write_text(
            """
            datasets:
              broken:
                category: connectivity
            """,
            encoding="utf-8",
        )

        cli = CLIInterface(datasets_config_path=datasets_path)
        result = runner.invoke(cli.app, ["debug", "list-datasets"])

        assert result.exit_code == 1
        assert "設定読み込みエラー" in result.output
