"""Database connection helpers for the production backend.

All psycopg connections should come through this module so pgvector adapters,
row mapping, commit, and rollback behavior stay consistent.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from pgvector.psycopg import register_vector
from psycopg.rows import dict_row

from src.core.config import AppConfig, get_config


def get_connection(config: AppConfig | None = None) -> psycopg.Connection:
    """Open a PostgreSQL connection with dict rows and pgvector support."""
    app_config = config or get_config()
    connection = psycopg.connect(
        **app_config.database.connect_kwargs,
        row_factory=dict_row,
    )
    register_vector(connection)
    return connection


@contextmanager
def transaction(config: AppConfig | None = None) -> Iterator[psycopg.Connection]:
    """Run a unit of work in one transaction and roll back on failure."""
    connection = get_connection(config)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
