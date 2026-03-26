from src.models import DatabaseModel
from src.transaction_context import TransactionContext


class DatabaseService:
    def __init__(self, ctx: TransactionContext) -> None:
        self._ctx = ctx

    def database_exists(self) -> bool:
        return self._ctx.database_dal.database_exists()

    def get_current_schema(self) -> DatabaseModel:
        return self._ctx.database_dal.get_current_schema()

    def get_size_mb(self) -> float:
        return self._ctx.database_dal.get_size_mb()
