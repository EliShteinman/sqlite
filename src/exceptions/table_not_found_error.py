class TableNotFoundError(Exception):
    def __init__(self, table_name: str) -> None:
        super().__init__(f"Table '{table_name}' not found")
        self.table_name = table_name
