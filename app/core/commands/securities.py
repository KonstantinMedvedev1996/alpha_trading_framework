
from sqlalchemy import select
from app.db.sessions import AsyncSessionLocal
from app.models.security import Security
from app.models.enum_helpers import PlatformEnum, SecurityStatusEnum, SecurityTypeEnum, FutureTypeEnum


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