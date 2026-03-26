from sqlalchemy import text
from sqlalchemy.orm import Session

from src.exceptions import (
    ColumnAlreadyExistsError,
    ColumnNotFoundError,
    TableNotFoundError,
)
from src.models import ColumnModel


class ColumnDAL:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add_column(self, table_name: str, column: ColumnModel) -> None:
        self._ensure_table_exists(table_name)
        if column.name in self._get_column_names(table_name):
            raise ColumnAlreadyExistsError(table_name, column.name)
        self._session.execute(
            text(
                f"ALTER TABLE {table_name} "
                f"ADD COLUMN {column.name} {column.type.value}"
            )
        )

    def drop_column(self, table_name: str, column_name: str) -> None:
        self._ensure_table_exists(table_name)
        if column_name not in self._get_column_names(table_name):
            raise ColumnNotFoundError(table_name, column_name)
        self._session.execute(
            text(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")
        )

    def column_exists(self, table_name: str, column_name: str) -> bool:
        self._ensure_table_exists(table_name)
        return column_name in self._get_column_names(table_name)

    def get_columns(self, table_name: str) -> list[str]:
        self._ensure_table_exists(table_name)
        return self._get_column_names(table_name)

    def _get_column_names(self, table_name: str) -> list[str]:
        result = self._session.execute(
            text(f"PRAGMA table_info({table_name})")
        )
        return [row[1] for row in result.fetchall()]

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
