from __future__ import annotations

import pandas as pd
import pytest
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from kawasaki_etl.core.db import DBConnectionError, get_engine, upsert_dataframe


def test_get_engine_prefers_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Env の DSN を使って Engine を生成できること."""
    monkeypatch.setenv("DB_DSN", "sqlite+pysqlite:///:memory:")
    engine = get_engine()

    with engine.connect() as conn:
        assert conn.execute(text("select 1")).scalar() == 1


def test_get_engine_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """接続失敗時にわかりやすい例外が出ること."""
    class DummyError(SQLAlchemyError): ...

    def fake_create_engine(*_args: object, **_kwargs: object) -> None:
        raise DummyError("boom")

    monkeypatch.setattr("kawasaki_etl.core.db.create_engine", fake_create_engine)
    monkeypatch.setenv("DB_DSN", "sqlite+pysqlite:///:memory:")

    with pytest.raises(DBConnectionError) as excinfo:
        get_engine()

    assert "DB connection failed" in str(excinfo.value)


def test_upsert_dataframe_updates_existing() -> None:
    """UPSERT により既存行が更新されること."""
    engine = create_engine("sqlite+pysqlite:///:memory:")
    metadata = MetaData()
    Table(
        "wifi_access_counts",
        metadata,
        Column("dataset_id", String, nullable=False),
        Column("date", String, nullable=False),
        Column("spot_id", String, nullable=False),
        Column("connection_count", Integer, nullable=False),
        Column("snapshot_date", String),
        sqlite_autoincrement=False,
    )
    metadata.create_all(engine)
    index_sql = (
        "CREATE UNIQUE INDEX idx_wifi_pk "
        "ON wifi_access_counts(date, spot_id)"
    )
    with engine.begin() as conn:
        conn.execute(text(index_sql))

    initial = pd.DataFrame(
        [
            {
                "dataset_id": "wifi",
                "date": "2020-01-01",
                "spot_id": "A",
                "connection_count": 10,
            },
            {
                "dataset_id": "wifi",
                "date": "2020-01-02",
                "spot_id": "A",
                "connection_count": 5,
            },
        ],
    )

    upsert_dataframe(initial, "wifi_access_counts", ["date", "spot_id"], engine)

    updated = pd.DataFrame(
        [
            {
                "dataset_id": "wifi",
                "date": "2020-01-01",
                "spot_id": "A",
                "connection_count": 50,
            },
        ],
    )
    upsert_dataframe(updated, "wifi_access_counts", ["date", "spot_id"], engine)

    with engine.connect() as conn:
        rows = list(
            conn.execute(
                text("select date, spot_id, connection_count from wifi_access_counts"),
            ),
        )

    assert sorted(rows) == [
        ("2020-01-01", "A", 50),
        ("2020-01-02", "A", 5),
    ]
