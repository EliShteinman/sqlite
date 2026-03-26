import sqlite3

from src.exceptions import InvalidSQLError
from src.transaction_context import TransactionContext


class QueryService:
    def __init__(self, ctx: TransactionContext) -> None:
        self._ctx = ctx

    def execute(self, sql: str) -> list[dict]:
        self._validate_syntax(sql)
        return self._ctx.database_dal.execute_query(sql)

    @staticmethod
    def _validate_syntax(sql: str) -> None:
        if not sql or not sql.strip():
            raise InvalidSQLError(sql, "empty query")
        try:
            sqlite3.complete_statement(sql if sql.rstrip().endswith(";") else sql + ";")
        except Exception:
            raise InvalidSQLError(sql, "incomplete or malformed statement")
