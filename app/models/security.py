from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SAEnum


from app.models.enum_helpers import PlatformEnum, SecurityStatusEnum, SecurityTypeEnum, FutureTypeEnum


from app.db.base import Base




class Security(Base):
    __tablename__ = "securities"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    platform: Mapped[PlatformEnum] = mapped_column(
        SAEnum(PlatformEnum, name="platform_enum", native_enum=False),
        nullable=False,
    )

    status: Mapped[SecurityStatusEnum] = mapped_column(
        SAEnum(SecurityStatusEnum, name="security_status_enum", native_enum=False),
        nullable=False,
        default=SecurityStatusEnum.ACTIVE,
    )
    
    type: Mapped[SecurityTypeEnum] = mapped_column(
        SAEnum(SecurityTypeEnum, name="security_type_enum", native_enum=False),
        nullable=False,
        default=SecurityTypeEnum.FUTURE,
    )
    
    term: Mapped[FutureTypeEnum] = mapped_column(
        SAEnum(FutureTypeEnum, name="future_type_enum", native_enum=False),
        nullable=True,
        default=FutureTypeEnum.SHORT_TERM,
    )

    historical_data: Mapped[list["HistoricalCandle"]] = relationship(
        back_populates="security",
        cascade="all, delete-orphan",
    )