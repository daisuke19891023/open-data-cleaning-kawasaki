from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping, cast

from pandas import DataFrame
import yaml
from sqlalchemy import MetaData, Table, create_engine, text
from sqlalchemy.dialects.postgresql import Insert as PGInsert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import Insert as SQLiteInsert
from sqlalchemy.exc import SQLAlchemyError

from kawasaki_etl.utils.logger import LoggerProtocol, get_logger

if TYPE_CHECKING:
    from pandas import DataFrame
    from sqlalchemy.engine import Engine

logger: LoggerProtocol = get_logger(__name__)


class DBConfigError(Exception):
    """Raised when DB configuration loading fails."""


class DBConnectionError(Exception):
    """Raised when database connection cannot be established."""


class UpsertError(Exception):
    """Raised when UPSERT processing fails."""


@dataclass
class DBConfig:
    """Database connection configuration."""

    dsn: str | None = None
    host: str | None = None
    port: int | None = None
    user: str | None = None
    password: str | None = None
    database: str | None = None
    options: str | None = None

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> DBConfig:
        """Build a DBConfig from a mapping loaded from YAML."""
        return cls(
            dsn=str(mapping["dsn"]) if mapping.get("dsn") else None,
            host=str(mapping["host"]) if mapping.get("host") else None,
            port=int(mapping["port"]) if mapping.get("port") is not None else None,
            user=str(mapping["user"]) if mapping.get("user") else None,
            password=str(mapping["password"]) if mapping.get("password") else None,
            database=str(mapping["database"]) if mapping.get("database") else None,
            options=str(mapping["options"]) if mapping.get("options") else None,
        )

    def as_dsn(self) -> str:
        """Return a DSN string constructed from configuration."""
        if self.dsn:
            return self.dsn

        required = [self.host, self.port, self.user, self.password, self.database]
        if any(value is None for value in required):
            msg = (
                "Incomplete DB configuration: "
                "host, port, user, password, database are required"
            )
            raise DBConfigError(msg)

        options_suffix = f"?options={self.options}" if self.options else ""
        return (
            "postgresql+psycopg://"
            f"{self.user}:{self.password}@{self.host}:{self.port}/{self.database}{options_suffix}"
        )


def _load_db_config_yaml(config_path: Path) -> dict[str, DBConfig]:
    try:
        raw_content = config_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        msg = f"DB config file not found: {config_path}"
        raise DBConfigError(msg) from None
    except OSError as exc:  # pragma: no cover - unexpected filesystem failure
        msg = f"Failed to read DB config file: {config_path}"
        raise DBConfigError(msg) from exc

    try:
        loaded_raw = yaml.safe_load(raw_content)
    except yaml.YAMLError as exc:
        msg = f"Failed to parse YAML in {config_path}: {exc}"
        raise DBConfigError(msg) from exc

    if loaded_raw is None:
        return {}
    if not isinstance(loaded_raw, dict):
        msg = f"DB config file must contain a mapping at top level: {config_path}"
        raise DBConfigError(msg)

    loaded_map = cast(dict[str, Mapping[str, Any]], loaded_raw)

    configs: dict[str, DBConfig] = {}
    for alias, entry in loaded_map.items():
        configs[str(alias)] = DBConfig.from_mapping(entry)
    return configs


def _resolve_db_config(alias: str, config_path: Path | None = None) -> DBConfig:
    env_dsn = os.getenv("DB_DSN")
    if env_dsn:
        return DBConfig(dsn=env_dsn)

    path = config_path or Path(os.getenv("DB_CONFIG_PATH", "configs/db.yml"))
    configs = _load_db_config_yaml(path)
    try:
        return configs[alias]
    except KeyError as exc:
        msg = f"DB config alias '{alias}' is not defined in {path}"
        raise DBConfigError(msg) from exc


def get_engine(alias: str = "default", *, config_path: Path | None = None) -> Engine:
    """Create a SQLAlchemy engine from environment variables or YAML config."""
    db_config = _resolve_db_config(alias, config_path)
    dsn = db_config.as_dsn()
    try:
        engine = create_engine(dsn, pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.error("DB connection failed", dsn=dsn, error=str(exc))
        msg = f"DB connection failed: {exc}"
        raise DBConnectionError(msg) from exc
    else:
        return engine


def _build_insert_statement(table: Table, engine: Engine) -> PGInsert | SQLiteInsert:
    dialect = engine.dialect.name
    if dialect == "postgresql":
        return pg_insert(table)
    if dialect == "sqlite":
        from sqlalchemy.dialects.sqlite import insert as sqlite_insert

        return sqlite_insert(table)

    msg = f"Unsupported database dialect for upsert: {dialect}"
    raise UpsertError(msg)


def upsert_dataframe(
    df: DataFrame,
    table_name: str,
    key_fields: list[str],
    engine: Engine,
) -> None:
    """Perform an UPSERT of a pandas DataFrame into a database table."""
    if getattr(df, "empty", False):
        logger.info("Skip upsert: DataFrame is empty", table=table_name)
        return

    metadata = MetaData()
    try:
        table = Table(table_name, metadata, autoload_with=engine)
    except SQLAlchemyError as exc:
        msg = f"Failed to reflect table '{table_name}': {exc}"
        raise UpsertError(msg) from exc

    for key in key_fields:
        if key not in table.columns:
            msg = f"Key field '{key}' is not present in table '{table_name}'"
            raise UpsertError(msg)

    records: list[dict[str, Any]] = cast(
        list[dict[str, Any]], df.to_dict(orient="records")  # pyright: ignore[reportUnknownMemberType]
    )
    if not records:
        logger.info("Skip upsert: no records to insert", table=table_name)
        return

    insert_stmt_any = cast(Any, _build_insert_statement(table, engine).values(records))
    update_columns: dict[str, Any] = {}
    for column in table.columns:
        if column.name in key_fields:
            continue
        update_columns[column.name] = insert_stmt_any.excluded[column.name]

    if update_columns:
        stmt = insert_stmt_any.on_conflict_do_update(
            index_elements=key_fields,
            set_=update_columns,
        )
    else:
        stmt = insert_stmt_any.on_conflict_do_nothing(index_elements=key_fields)

    try:
        with engine.begin() as conn:
            conn.execute(stmt)
    except SQLAlchemyError as exc:
        logger.error("UPSERT failed", table=table_name, error=str(exc))
        msg = f"Failed to upsert into '{table_name}': {exc}"
        raise UpsertError(msg) from exc

    logger.info("UPSERT completed", table=table_name, rows=len(records))
