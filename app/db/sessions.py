from contextlib import contextmanager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.db.db import engine, async_engine
from sqlalchemy.orm import Session, sessionmaker



SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_readonly_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


AsyncSessionLocal = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
)

# async def get_session() -> AsyncSession:
#     async with AsyncSessionLocal() as session:
#         yield session