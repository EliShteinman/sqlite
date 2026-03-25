import os

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.config import BYTES_PER_MB, SQLITE_URL_PREFIX
from src.enums import ColumnType
from src.models import ColumnModel, DatabaseModel, TableModel


class DatabaseDAL:
    def __init__(self, session: Session) -> None:
        self._session = session

    def execute_query(
        self, sql: str, params: dict | None = None
    ) -> list[dict]:
        result = self._session.execute(text(sql), params or {})
        if result.returns_rows:
            columns = list(result.keys())
            return [dict(zip(columns, row)) for row in result.fetchall()]
        return []

    def get_size_mb(self) -> float:
        db_path = self._resolve_db_path()
        size_bytes = os.path.getsize(db_path)
        return size_bytes / BYTES_PER_MB

    def get_current_schema(self) -> DatabaseModel:
        tables: list[TableModel] = []
        table_rows = self._session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        ).fetchall()

        for table_row in table_rows:
            table_name = table_row[0]
            column_rows = self._session.execute(
                text(f"PRAGMA table_info({table_name})")
            ).fetchall()
            columns = [
                ColumnModel(name=col[1], type=ColumnType(col[2]))
                for col in column_rows
            ]
            tables.append(TableModel(name=table_name, columns=columns))

        size_mb = self.get_size_mb()
        return DatabaseModel(max_size_mb=int(size_mb) + 1, tables=tables)

    def _resolve_db_path(self) -> str:
        url = str(self._session.bind.url)
        return url[len(SQLITE_URL_PREFIX):]
