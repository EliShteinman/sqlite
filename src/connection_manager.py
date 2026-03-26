from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


class ConnectionManager:
    @staticmethod
    @contextmanager
    def get_session(connection_string: str) -> Iterator[Session]:
        engine = create_engine(connection_string)
        ConnectionManager._register_sqlite_transaction_events(engine)
        session_factory = sessionmaker(bind=engine)
        session = session_factory()
        try:
            yield session
        finally:
            session.close()
            engine.dispose()

    @staticmethod
    def _register_sqlite_transaction_events(engine: Engine) -> None:
        @event.listens_for(engine, "connect")
        def disable_pysqlite_autocommit(dbapi_conn, connection_record):  # type: ignore[no-untyped-def]
            dbapi_conn.isolation_level = None

        @event.listens_for(engine, "begin")
        def emit_begin(conn):  # type: ignore[no-untyped-def]
            conn.exec_driver_sql("BEGIN")
