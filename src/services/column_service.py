from src.models import ColumnModel
from src.transaction_context import TransactionContext


class ColumnService:
    def __init__(self, ctx: TransactionContext) -> None:
        self._ctx = ctx

    def add_column(self, column: ColumnModel) -> None:
        self._ctx.column_dal.add_column(column)

    def drop_column(self, column: ColumnModel) -> None:
        self._ctx.column_dal.drop_column(column)

    def column_exists(self, column: ColumnModel) -> bool:
        return self._ctx.column_dal.column_exists(column)

    def get_columns(self, table_name: str) -> list[ColumnModel]:
        return self._ctx.column_dal.get_columns(table_name)

    def get_column_names(self, table_name: str) -> list[str]:
        return self._ctx.column_dal.get_column_names(table_name)
