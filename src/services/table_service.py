from src.models import ColumnModel
from src.transaction_context import TransactionContext


class TableService:
    def __init__(self, ctx: TransactionContext) -> None:
        self._ctx = ctx

    def create_table(self, table_name: str, columns: list[ColumnModel]) -> None:
        self._ctx.table_dal.create_table(table_name, columns)

    def drop_table(self, table_name: str) -> None:
        self._ctx.table_dal.drop_table(table_name)

    def table_exists(self, table_name: str) -> bool:
        return self._ctx.table_dal.table_exists(table_name)

    def get_all_tables(self) -> list[str]:
        return self._ctx.table_dal.get_all_tables()
