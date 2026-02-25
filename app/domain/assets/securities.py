from sqlalchemy import select
import pandas as pd

from app.db.sessions import AsyncSessionLocal
from app.models.enum_helpers import PlatformEnum, SecurityTypeEnum, SecurityStatusEnum,FutureTypeEnum
from app.models.security import Security
from app.core.mappers.securities import security_to_dict, securities_to_df
from app.core.exceptions.securities import SecurityNotFoundError

from app.core.commands.securities import get_or_create_security_id, get_securities_async

class SecurityAlreadyExistsError(Exception):
    pass

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

async def get_securities_df(
    platform: PlatformEnum,
    security_type: SecurityTypeEnum,
    status: SecurityStatusEnum,
) -> pd.DataFrame:
    securities = await get_securities_async(platform, security_type, status)
    return securities_to_df(securities)

async def create_security(
    name: str,
    platform: PlatformEnum = PlatformEnum.MOEX,
    status: SecurityStatusEnum = SecurityStatusEnum.ACTIVE,
    type: SecurityTypeEnum = SecurityTypeEnum.FUTURE,
    term: FutureTypeEnum = FutureTypeEnum.SHORT_TERM,
) -> int:
    """
    Async wrapper that forwards all parameters
    to get_or_create_security_id.
    """
    
    security =  await get_or_create_security_id(
        name=name,
        platform=platform,
        status=status,
        type=type,
        term=term,
    )
    
    if isinstance(security, int): 
        raise SecurityAlreadyExistsError(
                f"Security '{name}' already exists"
            )
    
    return security_to_dict(security)


    
    