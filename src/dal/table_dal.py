from sqlalchemy import text
from sqlalchemy.orm import Session

from src.exceptions import TableAlreadyExistsError, TableNotFoundError
from src.models import ColumnModel


class TableDAL:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_table(self, table_name: str, columns: list[ColumnModel]) -> None:
        if self.table_exists(table_name):
            raise TableAlreadyExistsError(table_name)
        columns_sql = ", ".join(
            f"{col.name} {col.type.value}" for col in columns
        )
        self._session.execute(text(f"CREATE TABLE {table_name} ({columns_sql})"))

    def drop_table(self, table_name: str) -> None:
        if not self.table_exists(table_name):
            raise TableNotFoundError(table_name)
        self._session.execute(text(f"DROP TABLE {table_name}"))

    def table_exists(self, table_name: str) -> bool:
        result = self._session.execute(
            text(
                "SELECT count(*) FROM sqlite_master "
                "WHERE type='table' AND name=:name"
            ),
            {"name": table_name},
        )
        return bool(result.scalar())

    def get_all_tables(self) -> list[str]:
        result = self._session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        )
        return [row[0] for row in result.fetchall()]
