from contextlib import contextmanager
from typing import Any
from sqlmodel import Session, text

from .base import BaseDBManager


class SQLModelDBManager(BaseDBManager):
    """DB manager implementation using SQLModel/SQLAlchemy engine."""

    def __init__(self, engine):
        self._engine = engine
        # self._engine.extend_existing = True  # Allow extending existing tables

    def execute_query(self, query: str, **kwargs) -> bool:
        stmt = text(query)
        with Session(self._engine) as session:
            if kwargs:
                session.exec(stmt, params=kwargs)
            else:
                session.exec(stmt)
            session.commit()
        return True

    def execute_fetch(self, query: str, **kwargs) -> Any:
        stmt = text(query)
        with Session(self._engine) as session:
            result = session.exec(stmt, params=kwargs) if kwargs else session.exec(stmt)
            try:
                return result.mappings().all()
            except Exception:
                try:
                    return result.fetchall()
                except Exception:
                    return list(result)

    @contextmanager
    def transaction(self):
        with Session(self._engine) as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
