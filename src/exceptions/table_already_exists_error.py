class TableAlreadyExistsError(Exception):
    def __init__(self, table_name: str) -> None:
        super().__init__(f"Table '{table_name}' already exists")
        self.table_name = table_name
