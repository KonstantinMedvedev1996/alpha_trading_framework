from pydantic import BaseModel, Field, model_validator
from datetime import datetime

from app.models.enum_helpers import TimeframeEnum


class CandleCreateSchema(BaseModel):
    security_id: int
    timeframe: TimeframeEnum
    datetime: datetime

    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_ohlc(self):
        if not (self.low <= self.open <= self.high):
            raise ValueError("Open must be between low and high")

        if not (self.low <= self.close <= self.high):
            raise ValueError("Close must be between low and high")

        return self