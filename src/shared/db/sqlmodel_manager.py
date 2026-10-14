import logging
from contextlib import contextmanager
from typing import Any
from sqlmodel import Session, text

from .base import BaseDBManager
from .appLogger import appLogger

logger = appLogger(
    "sqlmodel_manager",
    log_file="src/logs/sqlmodel_manager.log",
    level=logging.INFO,
    enable_console=True,
).get_logger()


class SQLModelDBManager(BaseDBManager):
    """DB manager implementation using SQLModel/SQLAlchemy engine."""

    def __init__(self, engine):
        self._engine = engine

    def execute_query(self, query: str, **kwargs) -> bool:
        stmt = text(query)
        try:
            with Session(self._engine) as session:
                if kwargs:
                    session.exec(stmt, params=kwargs)
                else:
                    session.exec(stmt)
                session.commit()
            return True
        except Exception:
            logger.exception("execute_query failed: %s | kwargs=%s", query, kwargs)
            raise

    def execute_fetch(self, query: str, **kwargs) -> Any:
        stmt = text(query)
        try:
            with Session(self._engine) as session:
                result = (
                    session.exec(stmt, params=kwargs) if kwargs else session.exec(stmt)
                )
                try:
                    return result.mappings().all()
                except Exception:
                    try:
                        return result.fetchall()
                    except Exception:
                        return list(result)
        except Exception:
            logger.exception("execute_fetch failed: %s | kwargs=%s", query, kwargs)
            raise

    @contextmanager
    def transaction(self):
        with Session(self._engine) as session:
            try:
                yield session
                session.commit()
            except Exception:
                logger.exception("transaction failed")
                session.rollback()
                raise
