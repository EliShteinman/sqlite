import os

from sqlalchemy import inspect, text
from sqlalchemy.engine import Inspector, Result
from sqlalchemy.exc import ResourceClosedError
from sqlalchemy.orm import Session

from src.config import BYTES_PER_MB, SQLITE_URL_PREFIX
from src.enums import ColumnType
from src.models import ColumnModel, DatabaseModel, TableModel


class DatabaseDAL:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._inspector: Inspector = inspect(session.bind)

    def database_exists(self) -> bool:
        db_path = self._resolve_db_path()
        return os.path.exists(db_path)

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
        table_names = self._inspector.get_table_names()
        tables = [TableModel(name=name) for name in table_names]
        columns = [
            col
            for name in table_names
            for col in self._read_columns(name)
        ]
        return DatabaseModel(
            max_size_mb=round(self.get_size_mb()),
            tables=tables,
            columns=columns,
        )

    def _read_columns(self, table_name: str) -> list[ColumnModel]:
        return [
            ColumnModel(
                table_name=table_name,
                name=col["name"],
                type=ColumnType(str(col["type"])),
            )
            for col in self._inspector.get_columns(table_name)
        ]

    def _resolve_db_path(self) -> str:
        url = str(self._session.bind.url)
        return url.removeprefix(SQLITE_URL_PREFIX)
