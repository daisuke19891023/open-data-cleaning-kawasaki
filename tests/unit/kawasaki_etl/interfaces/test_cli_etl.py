from __future__ import annotations

from typing import TYPE_CHECKING, Self

from typer.testing import CliRunner

import kawasaki_etl.core.io as io_module
from kawasaki_etl.interfaces.cli import CLIInterface

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path
    import pytest


class _DummyStream:
    def __init__(self, body: bytes, status_code: int = 200) -> None:
        self.body = body
        self.status_code = status_code

    def iter_bytes(self, chunk_size: int) -> Iterator[bytes]:
        _ = chunk_size
        yield self.body

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False


class _DummyClient:
    def __init__(self, body: bytes) -> None:
        self.body = body

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        return False

    def stream(self, method: str, url: str) -> _DummyStream:
        _ = (method, url)
        return _DummyStream(self.body)


def _patch_http_client(monkeypatch: pytest.MonkeyPatch, body: bytes) -> None:
    def dummy_factory(*_args: object, **_kwargs: object) -> _DummyClient:
        return _DummyClient(body)

    monkeypatch.setattr(io_module.httpx, "Client", dummy_factory)


def _write_dataset_config(config_path: Path, url: str) -> None:
    """テスト用の datasets.yml を生成する."""
    config_path.write_text(
        f"""
        sample:
          category: test
          url: {url}
          type: csv
        """,
        encoding="utf-8",
    )


def test_cli_download_command(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """`etl download` コマンドでファイルが保存されることを確認."""
    runner = CliRunner()
    datasets_yaml = tmp_path / "datasets.yml"
    download_url = "https://example.com/data.csv"
    _write_dataset_config(datasets_yaml, download_url)

    _patch_http_client(monkeypatch, body=b"payload")

    cli = CLIInterface(datasets_config_path=datasets_yaml)
    raw_dir = tmp_path / "raw"
    monkeypatch.setattr(io_module, "RAW_DATA_DIR", raw_dir)

    result = runner.invoke(cli.app, ["etl", "download", "sample"])

    assert result.exit_code == 0
    dest_file = raw_dir / "test" / "sample" / "data.csv"
    assert dest_file.exists()
    assert dest_file.read_bytes() == b"payload"
    assert "ダウンロード先" in result.stdout


def test_etl_list_command(tmp_path: Path) -> None:
    """Etl list で datasets.yml の ID が表示されること."""
    runner = CliRunner()
    datasets_path = tmp_path / "datasets.yml"
    datasets_path.write_text(
        """
        datasets:
          wifi_sample:
            category: wifi
            url: https://example.com/wifi.csv
            type: csv
        """,
        encoding="utf-8",
    )

    cli = CLIInterface(datasets_config_path=datasets_path)
    result = runner.invoke(cli.app, ["etl", "list"])

    assert result.exit_code == 0
    assert "wifi_sample" in result.stdout


def test_etl_run_invokes_wifi_pipeline(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """Etl run で Wi-Fi パイプラインが実行されること."""
    runner = CliRunner()
    datasets_path = tmp_path / "datasets.yml"
    datasets_path.write_text(
        """
        datasets:
          wifi_sample:
            category: wifi
            url: https://example.com/wifi.csv
            type: csv
            table: wifi_access_counts
        """,
        encoding="utf-8",
    )

    called: list[tuple[str, object | None]] = []

    def fake_run_wifi(dataset: object, engine: object | None = None) -> None:
        called.append((dataset.dataset_id, engine))

    cli = CLIInterface(datasets_config_path=datasets_path)
    monkeypatch.setattr(cli, "_get_engine", lambda _alias: "engine")
    monkeypatch.setattr("kawasaki_etl.interfaces.cli.run_wifi_count", fake_run_wifi)

    result = runner.invoke(cli.app, ["etl", "run", "wifi_sample"])

    assert result.exit_code == 0
    assert called == [("wifi_sample", "engine")]


def test_etl_run_all_invokes_all(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """Etl run-all で全データセットが処理されること."""
    runner = CliRunner()
    datasets_path = tmp_path / "datasets.yml"
    datasets_path.write_text(
        """
        datasets:
          wifi_a:
            category: wifi
            url: https://example.com/a.csv
            type: csv
          wifi_b:
            category: wifi
            url: https://example.com/b.csv
            type: csv
        """,
        encoding="utf-8",
    )

    called: list[str] = []

    def fake_run_wifi(dataset: object, engine: object | None = None) -> None:
        _ = engine
        called.append(dataset.dataset_id)

    cli = CLIInterface(datasets_config_path=datasets_path)
    monkeypatch.setattr(cli, "_get_engine", lambda _alias: "engine")
    monkeypatch.setattr("kawasaki_etl.interfaces.cli.run_wifi_count", fake_run_wifi)

    result = runner.invoke(cli.app, ["etl", "run-all"])

    assert result.exit_code == 0
    assert called == ["wifi_a", "wifi_b"]
