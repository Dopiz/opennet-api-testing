from __future__ import annotations

import logging
from typing import Optional

import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)


class PsqlModule:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        user: str = "postgres",
        password: Optional[str] = None,
        database: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self._conn = None
        self._cur = None
        self._connect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _connect(self):
        self._conn = psycopg2.connect(
            database=self.database,
            user=self.user,
            password=self.password,
            host=self.host,
            port=int(self.port),
        )
        self._conn.autocommit = True
        self._cur = self._conn.cursor()

    def _ensure_connection(self):
        """Re-establish connection after InterfaceError."""
        try:
            self._conn.isolation_level
        except (psycopg2.InterfaceError, AttributeError):
            logger.warning("Connection lost, reconnecting...")
            self._connect()

    def _execute_with_retry(self, fn, *args, **kwargs):
        """Execute a DB operation, auto-reconnect once on InterfaceError."""
        try:
            return fn(*args, **kwargs)
        except psycopg2.InterfaceError:
            self._connect()
            return fn(*args, **kwargs)

    def read_data(self, sql: str, args: dict = None, fetchall: bool = True):
        self._execute_with_retry(self._cur.execute, sql, args)
        columns = self._cur.description
        if fetchall:
            rows = self._cur.fetchall()
            if not rows:
                return []
            return [{columns[i].name: val for i, val in enumerate(row)} for row in rows]
        row = self._cur.fetchone()
        if not row:
            return None
        return {columns[i].name: val for i, val in enumerate(row)}

    def write_data(self, sql: str, args=None, bulk: bool = False):
        try:
            if bulk:
                return self._execute_with_retry(execute_values, self._cur, sql, args)
            return self._execute_with_retry(self._cur.execute, sql, args)
        except Exception:
            self._conn.rollback()
            raise

    # -- SQL builders -------------------------------------------------------

    @staticmethod
    def select(
        table: str,
        fields: list = None,
        conditions: dict = None,
        cond_logic: str = "AND",
        order_by: list[tuple[str, str]] = None,
    ) -> str:
        cols = "*" if not fields else ", ".join(f'"{f}"' for f in fields)
        sql = f'SELECT {cols} FROM "{table}" '
        if conditions:
            sql += "WHERE " + PsqlModule._build_where(conditions, cond_logic)
        if order_by:
            clause = ", ".join(f'"{col}" {direction}' for col, direction in order_by)
            sql += f"ORDER BY {clause} "
        return sql

    @staticmethod
    def update(
        table: str,
        fields: list,
        conditions: dict = None,
        cond_logic: str = "AND",
    ) -> str:
        set_clause = ", ".join(f'"{f}" = %({f})s' for f in fields)
        sql = f'UPDATE "{table}" SET {set_clause} '
        if conditions:
            sql += "WHERE " + PsqlModule._build_where(conditions, cond_logic)
        return sql

    @staticmethod
    def _build_where(conditions: dict, logic: str = "AND") -> str:
        parts = []
        for col, value in conditions.items():
            if isinstance(value, list):
                parts.append(f'"{col}" = ANY(%({col})s)')
            else:
                parts.append(f'"{col}" = %({col})s')
        return f" {logic} ".join(parts) + " "

    def close(self):
        if self._conn and not self._conn.closed:
            self._conn.close()
