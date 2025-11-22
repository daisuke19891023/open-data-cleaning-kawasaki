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
