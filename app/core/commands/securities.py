
from sqlalchemy import select
from app.db.sessions import AsyncSessionLocal
from app.models.security import Security
from app.models.enum_helpers import PlatformEnum, SecurityStatusEnum, SecurityTypeEnum, FutureTypeEnum


import pandas as pd

class SecurityNotFoundError(Exception):
    pass


async def get_security_id(
    name: str,
    platform: PlatformEnum = PlatformEnum.MOEX,
    security_type: SecurityTypeEnum = SecurityTypeEnum.FUTURE,
    ) -> int:
    """
    Get Security.id by name.

    Raises:
        SecurityNotFoundError: if the security does not exist.
    """
    async with AsyncSessionLocal() as session:
        stmt = select(Security).where(
            Security.platform == platform,
            Security.type == security_type,
            Security.name == name)
        result = await session.execute(stmt)
        security = result.scalar_one_or_none()

        if not security:
            raise SecurityNotFoundError(f"Security '{name}' not found")

        return security.id

async def get_securities_async(
    platform: PlatformEnum,
    security_type: SecurityTypeEnum,
    status: SecurityStatusEnum,
) -> list[Security]:
    async with AsyncSessionLocal() as session:
        stmt = (
            select(Security)
            .where(Security.platform == platform)
            .where(Security.type == security_type)
            .where(Security.status == status)
        )

        result = await session.execute(stmt)
        return result.scalars().all()


async def get_or_create_security_id(
    name: str,
    platform: PlatformEnum = PlatformEnum.MOEX,
    status: SecurityStatusEnum = SecurityStatusEnum.ACTIVE,
    type: SecurityTypeEnum = SecurityTypeEnum.FUTURE,
    term: FutureTypeEnum = FutureTypeEnum.SHORT_TERM
) -> int:
    """
    Get Security.id by name, or create the Security if it doesn't exist.
    """

    async with AsyncSessionLocal() as session:
        stmt = select(Security).where(Security.name == name)
        result = await session.execute(stmt)
        security = result.scalar_one_or_none()

        if security:
            return security.id

        security = Security(
            name=name,
            platform=platform,
            status=status,
            type=type,
            term=term
        )

        session.add(security)
        await session.flush()   # async flush
        await session.commit() # commit explicitly

        return security.id

def securities_to_df(securities: list[Security]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id": s.id,
                "name": s.name,
                "platform": s.platform,
                "type": s.type,
                "status": s.status,
            }
            for s in securities
        ]
    )

def security_to_dict(security: Security) -> dict:
    return {
        "id": security.id,
        "name": security.name,
        "platform": security.platform,
        "type": security.type,
        "status": security.status,
    }

async def get_securities_df(
    platform: PlatformEnum,
    security_type: SecurityTypeEnum,
    status: SecurityStatusEnum,
) -> pd.DataFrame:
    securities = await get_securities_async(platform, security_type, status)
    return securities_to_df(securities)

async def get_security(
    name: str,
    platform: PlatformEnum = PlatformEnum.MOEX,
    security_type: SecurityTypeEnum = SecurityTypeEnum.FUTURE,
) -> dict:
    async with AsyncSessionLocal() as session:
        stmt = select(Security).where(
            Security.platform == platform,
            Security.type == security_type,
            Security.name == name,
        )

        result = await session.execute(stmt)
        security = result.scalar_one_or_none()

        if not security:
            raise SecurityNotFoundError(f"Security '{name}' not found")

        return security_to_dict(security)
