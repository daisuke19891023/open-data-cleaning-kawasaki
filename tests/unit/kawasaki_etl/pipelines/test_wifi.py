from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, text

from kawasaki_etl.core.models import DatasetConfig
from kawasaki_etl.pipelines import wifi

if TYPE_CHECKING:
    from pathlib import Path
    from sqlalchemy.engine import Engine


@pytest.fixture
def sqlite_engine() -> Engine:
    """SQLite 上の簡易テーブルを作る."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    metadata = MetaData()
    Table(
        "wifi_access_counts",
        metadata,
        Column("dataset_id", String, nullable=False),
        Column("date", String, nullable=False),
        Column("spot_id", String, nullable=False),
        Column("spot_name", String),
        Column("connection_count", Integer, nullable=False),
        Column("snapshot_date", String),
        sqlite_autoincrement=False,
    )
    metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE UNIQUE INDEX idx_wifi_pk ON wifi_access_counts(date, spot_id)",
            ),
        )
    return engine


def _build_dataset() -> DatasetConfig:
    return DatasetConfig(
        dataset_id="wifi_sample",
        category="wifi",
        url="https://example.com/wifi.csv",
        type="csv",
        parser="wifi_usage_parser",
        table="wifi_access_counts",
        key_fields=["date", "spot_id"],
        snapshot_date="2020-12-31",
        extra={
            "column_mapping": {
                "date": "日付",
                "spot_id": "スポットID",
                "spot_name": "スポット名",
                "connection_count": "接続数",
            },
        },
    )


def test_run_wifi_count_upserts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    sqlite_engine: Engine,
) -> None:
    """同じキーの行が UPSERT されることを確認する."""
    raw_path = tmp_path / "raw.csv"
    raw_path.write_text(
        "日付,スポットID,スポット名,接続数\n2020-01-01,A,駅前,10\n2020-01-02,A,駅前,5\n",
        encoding="utf-8",
    )

    dataset = _build_dataset()

    monkeypatch.setattr(wifi, "NORMALIZED_DATA_DIR", tmp_path / "normalized")

    def _download(_cfg: DatasetConfig) -> Path:
        return raw_path

    def _calculate_hash(_p: Path) -> str:
        return "dummy-hash"

    def _is_loaded(*_args: object, **_kwargs: object) -> bool:
        return False

    def _mark_loaded(*_args: object, **_kwargs: object) -> None:
        return None

    monkeypatch.setattr(wifi, "download_if_needed", _download)
    monkeypatch.setattr(wifi, "calculate_sha256", _calculate_hash)
    monkeypatch.setattr(wifi, "is_already_loaded", _is_loaded)
    monkeypatch.setattr(wifi, "mark_loaded", _mark_loaded)

    wifi.run_wifi_count(dataset, engine=sqlite_engine)

    with sqlite_engine.connect() as conn:
        rows = list(
            conn.execute(
                text("select date, spot_id, connection_count from wifi_access_counts"),
            ),
        )

    assert sorted(rows) == [("2020-01-01", "A", 10), ("2020-01-02", "A", 5)]
    normalized = (
        wifi.NORMALIZED_DATA_DIR / "wifi" / "wifi_sample" / "raw_normalized.csv"
    )
    assert normalized.exists()

    raw_path.write_text(
        "日付,スポットID,スポット名,接続数\n2020-01-01,A,駅前,50\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(wifi, "is_already_loaded", _is_loaded)
    wifi.run_wifi_count(dataset, engine=sqlite_engine)

    with sqlite_engine.connect() as conn:
        rows_after = list(
            conn.execute(
                text("select date, spot_id, connection_count from wifi_access_counts"),
            ),
        )

    assert sorted(rows_after) == [("2020-01-01", "A", 50), ("2020-01-02", "A", 5)]


def test_run_wifi_count_skips_when_already_loaded(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    sqlite_engine: Engine,
) -> None:
    """meta_store が既処理を示す場合は処理しない."""
    raw_path = tmp_path / "raw.csv"
    raw_path.write_text(
        "日付,スポットID,スポット名,接続数\n2020-01-01,A,駅前,10\n",
        encoding="utf-8",
    )

    dataset = _build_dataset()

    monkeypatch.setattr(wifi, "NORMALIZED_DATA_DIR", tmp_path / "normalized")

    def _download(_cfg: DatasetConfig) -> Path:
        return raw_path

    def _calculate_hash(_p: Path) -> str:
        return "dummy-hash"

    marker_called: list[bool] = []

    def _is_loaded(*_args: object, **_kwargs: object) -> bool:
        return True

    def _mark_loaded(*_args: object, **_kwargs: object) -> None:
        marker_called.append(True)

    monkeypatch.setattr(wifi, "download_if_needed", _download)
    monkeypatch.setattr(wifi, "calculate_sha256", _calculate_hash)
    monkeypatch.setattr(wifi, "is_already_loaded", _is_loaded)
    monkeypatch.setattr(wifi, "mark_loaded", _mark_loaded)

    wifi.run_wifi_count(dataset, engine=sqlite_engine)

    with sqlite_engine.connect() as conn:
        rows = list(conn.execute(text("select count(*) from wifi_access_counts")))

    assert rows[0][0] == 0
    assert marker_called == []
