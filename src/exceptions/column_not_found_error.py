class ColumnNotFoundError(Exception):
    def __init__(self, table_name: str, column_name: str) -> None:
        super().__init__(
            f"Column '{column_name}' not found in table '{table_name}'"
        )
        self.table_name = table_name
        self.column_name = column_name
