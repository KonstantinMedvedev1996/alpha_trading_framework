

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import settings





engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=True,
    # pool_size=5,
    # max_overflow=10,
)

async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=True,
    # pool_size=5,
    # max_overflow=10,
)  

# session_factory  = sessionmaker(bind=engine)

async_session_factory = async_sessionmaker(bind=async_engine)


# SessionLocal = sessionmaker(
#     bind=engine,
#     autoflush=False,
#     autocommit=False,
# )

# @contextmanager
# def get_session():
#     session = SessionLocal()
#     try:
#         yield session
#         session.commit()
#     except Exception:
#         session.rollback()
#         raise
#     finally:
#         session.close()