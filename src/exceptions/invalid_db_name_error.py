class InvalidDBNameError(Exception):
    def __init__(self, db_name: str) -> None:
        super().__init__(f"Invalid database name: '{db_name}'")
        self.db_name = db_name
