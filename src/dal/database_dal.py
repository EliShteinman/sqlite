import os

from sqlalchemy import text
from sqlalchemy.engine import Result
from sqlalchemy.exc import ResourceClosedError
from sqlalchemy.orm import Session

from src.config import BYTES_PER_MB, SQLITE_URL_PREFIX
from src.enums import ColumnType
from src.models import ColumnModel, DatabaseModel, TableModel


class DatabaseDAL:
    def __init__(self, session: Session) -> None:
        self._session = session

    def execute_query(self, sql: str) -> list[dict]:
        result: Result = self._session.execute(text(sql))
        try:
            return [dict(row) for row in result.mappings().all()]
        except ResourceClosedError:
            return []

    def get_size_mb(self) -> float:
        db_path = self._resolve_db_path()
        size_bytes = os.path.getsize(db_path)
        return size_bytes / BYTES_PER_MB

    def get_current_schema(self) -> DatabaseModel:
        table_names = self._get_table_names()
        tables = [self._read_table_schema(name) for name in table_names]
        return DatabaseModel(max_size_mb=round(self.get_size_mb()), tables=tables)

    def _get_table_names(self) -> list[str]:
        rows = self._session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        ).fetchall()
        return [row[0] for row in rows]

    def _read_table_schema(self, table_name: str) -> TableModel:
        pragma_rows = self._session.execute(
            text(f"PRAGMA table_info({table_name})")
        ).fetchall()
        columns = [
            ColumnModel(name=row[1], type=ColumnType(row[2]))
            for row in pragma_rows
        ]
        return TableModel(name=table_name, columns=columns)

    def _resolve_db_path(self) -> str:
        url = str(self._session.bind.url)
        return url.removeprefix(SQLITE_URL_PREFIX)
