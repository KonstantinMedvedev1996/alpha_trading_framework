import asyncio
import pandas as pd
from moexalgo import Market
from requests import RequestException


def _load_moex_futures_sync() -> pd.DataFrame:
    fo = Market("FO")
    return fo.tickers()


async def load_moex_futures_tickers() -> pd.DataFrame:
    try:
        df = await asyncio.to_thread(_load_moex_futures_sync)

    except RequestException as e:
        raise ConnectionError(
            "Failed to connect to MOEX ISS API"
        ) from e

    except Exception as e:
        raise RuntimeError(
            "Unexpected error while loading MOEX futures tickers"
        ) from e

    if not isinstance(df, pd.DataFrame) or df.empty:
        raise RuntimeError("MOEX returned empty or invalid data")

    if "lasttradedate" in df.columns:
        df["lasttradedate"] = pd.to_datetime(
            df["lasttradedate"],
            errors="coerce"
        )

    return df
