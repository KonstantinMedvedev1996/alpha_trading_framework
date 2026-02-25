from sqlalchemy import text
import pandas as pd

from app.db.base import Base
from app.models import security, historicalcandle
from app.db.db import engine, async_engine
from app.db.sessions import AsyncSessionLocal



# def create_tables():
#     engine.echo = True
#     # Base.metadata.drop_all(bind=engine)
#     Base.metadata.create_all(bind=engine)
#     engine.echo = True

async def create_tables() -> None:
    """
    Create all tables using async engine.
    """

    async_engine.echo = True

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_engine.echo = False

async def drop_tables() -> None:
    """
    Drop all tables using async engine.
    """

    async_engine.echo = True

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    async_engine.echo = False

# def drop_tables():
#     engine.echo = True
#     Base.metadata.drop_all(bind=engine)
#     # Base.metadata.create_all(bind=engine)
#     engine.echo = True

async def get_tables_df() -> pd.DataFrame:
    """
    Returns DataFrame of tables (PostgreSQL)."""

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
        )

        tables = result.scalars().all()

    return pd.DataFrame(tables, columns=["table_name"])

async def get_current_database() -> str:
    """
    Returns name of currently connected PostgreSQL database.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT current_database();")
        )
        return result.scalar_one()

async def get_all_databases_df() -> pd.DataFrame:
    """
    Returns all databases in PostgreSQL server.
    """

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT datname
                FROM pg_database
                WHERE datistemplate = false
                ORDER BY datname;
            """)
        )

        databases = result.scalars().all()

    return pd.DataFrame(databases, columns=["database_name"])

async def get_database_count() -> int:
    """
    Returns number of user databases.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT COUNT(*)
                FROM pg_database
                WHERE datistemplate = false;
            """)
        )

        return result.scalar_one()

async def get_databases_with_size_mb() -> pd.DataFrame:
    """
    Returns all user databases with their size in MB.
    """

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT
                    datname AS database_name,
                    ROUND(pg_database_size(datname) / 1024.0 / 1024.0, 2) AS size_mb
                FROM pg_database
                WHERE datistemplate = false
                ORDER BY size_mb DESC;
            """)
        )

        rows = result.fetchall()

    return pd.DataFrame(rows, columns=["database_name", "size_mb"])

async def drop_tables_by_name(
    table_names: list[str],
    cascade: bool = True,
) -> None:
    """
    Drops selected tables from PostgreSQL database.

    Parameters
    ----------
    table_names : list[str]
        List of table names to drop.
    cascade : bool
        Whether to use CASCADE (default True).
    """

    if not table_names:
        return

    async with AsyncSessionLocal() as session:
        for table in table_names:

            # basic protection against injection
            if not table.isidentifier():
                raise ValueError(f"Invalid table name: {table}")

            query = f'DROP TABLE IF EXISTS "{table}"'
            if cascade:
                query += " CASCADE"

            await session.execute(text(query))

        await session.commit()

