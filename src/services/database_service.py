from src.models import DatabaseModel, TableModel
from src.transaction_context import TransactionContext


class DatabaseService:
    def __init__(self, ctx: TransactionContext) -> None:
        self._ctx = ctx

    def create(self, db_model: DatabaseModel) -> None:
        for table in db_model.tables:
            self._ctx.table_dal.create_table(table)

    def update(self, new_schema: DatabaseModel) -> None:
        current_schema = self._ctx.database_dal.get_current_schema()
        current_tables = {t.name: t for t in current_schema.tables}
        new_tables = {t.name: t for t in new_schema.tables}

        self._drop_removed_tables(current_tables, new_tables)
        self._add_new_tables(current_tables, new_tables)
        self._sync_columns(current_tables, new_tables)

    def _drop_removed_tables(
        self,
        current_tables: dict[str, TableModel],
        new_tables: dict[str, TableModel],
    ) -> None:
        for table_name in current_tables:
            if table_name not in new_tables:
                self._ctx.table_dal.drop_table(table_name)

    def _add_new_tables(
        self,
        current_tables: dict[str, TableModel],
        new_tables: dict[str, TableModel],
    ) -> None:
        for table_name, table in new_tables.items():
            if table_name not in current_tables:
                self._ctx.table_dal.create_table(table)

    def _sync_columns(
        self,
        current_tables: dict[str, TableModel],
        new_tables: dict[str, TableModel],
    ) -> None:
        shared_tables = set(current_tables) & set(new_tables)
        for table_name in shared_tables:
            current_columns = {c.name for c in current_tables[table_name].columns}
            new_columns = {c.name: c for c in new_tables[table_name].columns}

            for col_name in current_columns - set(new_columns):
                self._ctx.column_dal.drop_column(table_name, col_name)

            for col_name, column in new_columns.items():
                if col_name not in current_columns:
                    self._ctx.column_dal.add_column(table_name, column)
