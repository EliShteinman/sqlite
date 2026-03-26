from sqlalchemy.orm import Session

from src.connection_resolver import SQLiteConnectionResolver
from src.dal.column_dal import ColumnDAL
from src.dal.database_dal import DatabaseDAL
from src.dal.table_dal import TableDAL
from src.services.column_service import ColumnService
from src.services.database_service import DatabaseService
from src.services.query_service import QueryService
from src.services.table_service import TableService
from src.transaction_context import TransactionContext


def create_connection_resolver() -> SQLiteConnectionResolver:
    return SQLiteConnectionResolver()


def create_transaction_context(session: Session) -> TransactionContext:
    return TransactionContext(session)


def create_table_service(ctx: TransactionContext) -> TableService:
    return TableService(ctx)


def create_column_service(ctx: TransactionContext) -> ColumnService:
    return ColumnService(ctx)


def create_query_service(ctx: TransactionContext) -> QueryService:
    return QueryService(ctx)


def create_database_service(ctx: TransactionContext) -> DatabaseService:
    return DatabaseService(ctx)
