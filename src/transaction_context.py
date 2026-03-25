from types import TracebackType

from sqlalchemy.orm import Session

from src.dal.column_dal import ColumnDAL
from src.dal.database_dal import DatabaseDAL
from src.dal.table_dal import TableDAL


class TransactionContext:
    def __init__(self, session: Session) -> None:
        self._session = session
        self.table_dal = TableDAL(session)
        self.column_dal = ColumnDAL(session)
        self.database_dal = DatabaseDAL(session)

    def __enter__(self) -> "TransactionContext":
        self._session.begin()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self._session.rollback()
        else:
            self._session.commit()
