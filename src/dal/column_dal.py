from sqlalchemy import text
from sqlalchemy.orm import Session

from src.enums import ColumnType
from src.exceptions import (
    ColumnAlreadyExistsError,
    ColumnNotFoundError,
    TableNotFoundError,
)
from src.models import ColumnModel


class ColumnDAL:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add_column(self, column: ColumnModel) -> None:
        if column.name in self.get_column_names(column.table_name):
            raise ColumnAlreadyExistsError(column.table_name, column.name)
        self._session.execute(
            text(
                f"ALTER TABLE {column.table_name} "
                f"ADD COLUMN {column.name} {column.type.value}"
            )
        )

    def drop_column(self, column: ColumnModel) -> None:
        if column.name not in self.get_column_names(column.table_name):
            raise ColumnNotFoundError(column.table_name, column.name)
        self._session.execute(
            text(f"ALTER TABLE {column.table_name} DROP COLUMN {column.name}")
        )

    def column_exists(self, column: ColumnModel) -> bool:
        return column.name in self.get_column_names(column.table_name)

    def get_columns(self, table_name: str) -> list[ColumnModel]:
        self._ensure_table_exists(table_name)
        return self._read_columns(table_name)

    def get_column_names(self, table_name: str) -> list[str]:
        self._ensure_table_exists(table_name)
        return [col.name for col in self._read_columns(table_name)]

    def _read_columns(self, table_name: str) -> list[ColumnModel]:
        rows = self._session.execute(
            text(f"PRAGMA table_info({table_name})")
        ).fetchall()
        return [
            ColumnModel(table_name=table_name, name=row[1], type=ColumnType(row[2]))
            for row in rows
        ]

    def _ensure_table_exists(self, table_name: str) -> None:
        result = self._session.execute(
            text(
                "SELECT count(*) FROM sqlite_master "
                "WHERE type='table' AND name=:name"
            ),
            {"name": table_name},
        )
        if not result.scalar():
            raise TableNotFoundError(table_name)
