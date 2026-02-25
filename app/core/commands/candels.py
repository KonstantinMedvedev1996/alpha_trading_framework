from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

import pandas as pd

from app.db.sessions import AsyncSessionLocal

from app.models.enum_helpers import TimeframeEnum
from app.models.historicalcandle import HistoricalCandle
from app.schemas.candel import CandleCreateSchema

CHUNK_SIZE = 2000  # safe for 8 columns (4000 * 8 = 32000 < 32767)


async def insert_candles_from_df(
    df: pd.DataFrame,
    security_id: int,
    timeframe: TimeframeEnum,
) -> int:

    if df.empty:
        return 0

    records = [
        {
            "security_id": security_id,
            "timeframe": timeframe,
            "datetime": row.datetime,
            "open": row.open,
            "high": row.high,
            "low": row.low,
            "close": row.close,
            "volume": int(row.volume),
        }
        for row in df.itertuples(index=False)
    ]

    inserted = 0

    async with AsyncSessionLocal() as session:
        for i in range(0, len(records), CHUNK_SIZE):
            chunk = records[i:i + CHUNK_SIZE]

            stmt = (
                insert(HistoricalCandle)
                .values(chunk)
                .on_conflict_do_nothing(
                    index_elements=[
                        "security_id",
                        "timeframe",
                        "datetime",
                    ]
                )
            )

            result = await session.execute(stmt)

            # rowcount works correctly with DO NOTHING
            inserted += result.rowcount or 0

        await session.commit()

    return inserted