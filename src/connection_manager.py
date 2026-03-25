from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


class ConnectionManager:
    @staticmethod
    @contextmanager
    def get_session(connection_string: str) -> Iterator[Session]:
        engine = create_engine(connection_string)
        session_factory = sessionmaker(bind=engine)
        session = session_factory()
        try:
            yield session
        finally:
            session.close()
            engine.dispose()
