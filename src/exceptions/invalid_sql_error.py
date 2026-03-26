class InvalidSQLError(Exception):
    def __init__(self, sql: str, reason: str) -> None:
        super().__init__(f"Invalid SQL: {reason}")
        self.sql = sql
        self.reason = reason
