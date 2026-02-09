from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Numeric, BigInteger, DateTime, ForeignKey, UniqueConstraint

from app.models.enum_helpers import TimeframeEnum

from app.db.base import Base
from app.models.security import Security


class HistoricalCandle(Base):
    __tablename__ = "historical_candles"
    __table_args__ = (
        UniqueConstraint(
            "security_id", "timeframe", "datetime",
            name="uq_security_tf_time",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    


    security_id: Mapped[int] = mapped_column(
        ForeignKey("securities.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    timeframe: Mapped[TimeframeEnum] = mapped_column(
        SAEnum(TimeframeEnum, name="timeframe_enum", native_enum=False),
        nullable=False,
        index=True,
    )

    datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    open: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    high: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    low: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    close: Mapped[float] = mapped_column(Numeric(18, 6), nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    
    security: Mapped[Security] = relationship(
        back_populates="historical_data"
    )