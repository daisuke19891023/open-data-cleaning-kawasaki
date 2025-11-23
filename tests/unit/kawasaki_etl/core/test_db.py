from __future__ import annotations

import pandas as pd
import pytest
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from kawasaki_etl.core import db
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

    captured: dict[str, object] = {}

    def fake_error(msg: str, **kwargs: object) -> None:
        captured["msg"] = msg
        captured.update(kwargs)

    monkeypatch.setattr(
        "kawasaki_etl.core.db.create_engine", fake_create_engine,
    )  # pyright: ignore[reportCallIssue]
    monkeypatch.setenv("DB_DSN", "sqlite+pysqlite:///:memory:")
    monkeypatch.setattr(db.logger, "error", fake_error)

    with pytest.raises(DBConnectionError) as excinfo:
        get_engine()

    assert "DB connection failed" in str(excinfo.value)
    assert captured["msg"] == "DB connection failed"
    assert captured["dsn"] == "sqlite+pysqlite:///:memory:"


def test_get_engine_failure_masks_password(monkeypatch: pytest.MonkeyPatch) -> None:
    """ログにパスワードが出力されないようにマスクされること."""

    class DummyError(SQLAlchemyError): ...

    def fake_create_engine(*_args: object, **_kwargs: object) -> None:
        raise DummyError("boom")

    captured: dict[str, object] = {}

    def fake_error(msg: str, **kwargs: object) -> None:
        captured["msg"] = msg
        captured.update(kwargs)

    dsn = "postgresql+psycopg://user:secret@localhost:5432/example"

    monkeypatch.setattr(
        "kawasaki_etl.core.db.create_engine", fake_create_engine,
    )  # pyright: ignore[reportCallIssue]
    monkeypatch.setenv("DB_DSN", dsn)
    monkeypatch.setattr(db.logger, "error", fake_error)

    with pytest.raises(DBConnectionError):
        get_engine()

    safe_dsn = captured.get("dsn")
    assert isinstance(safe_dsn, str)
    assert "user" not in safe_dsn
    assert "secret" not in safe_dsn
    assert safe_dsn.startswith("postgresql+psycopg://***:***@")


def test_mask_sensitive_dsn_masks_user_and_password() -> None:
    """DSN 文字列のユーザー名とパスワードが置換されること."""
    dsn = "postgresql+psycopg://user:password@db.example.com:5432/sample?options=-c%20statement_timeout%3D5000"
    masked = db._mask_sensitive_dsn(  # pyright: ignore[reportPrivateUsage]  # noqa: SLF001
        dsn,
    )

    assert "user" not in masked
    assert "password" not in masked
    assert masked.startswith("postgresql+psycopg://***:***@db.example.com:5432/sample")


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
