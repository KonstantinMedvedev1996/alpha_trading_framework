import pandas as pd

from app.providers.moex.futures import load_moex_futures_tickers
from app.providers.moex.futures import load_moex_futures_tickers_pickle
from app.providers.moex.futures import save_moex_futures_tickers_pickle_safe
from app.providers.moex.futures import moex_futures_garbage_collector


async def get_active_futures():
    df = await load_moex_futures_tickers()
    # apply domain rules here
    return df

async def get_active_futures() -> pd.DataFrame:
    """
    Returns active MOEX futures.

    Strategy:
    1. Try loading latest cached pickle
    2. If not found → download & save
    3. Reload from pickle
    4. Apply domain filters
    """

    try:
        print("ready to load pickle")
        df = await load_moex_futures_tickers_pickle()
        print("loaded local pickle")
    except FileNotFoundError:
        # No recent file → download fresh data
        print("can't load local pickle, forwarding to moex API.")
        await moex_futures_garbage_collector()
        print("deleted old pickles")
        await save_moex_futures_tickers_pickle_safe()
        print("saved fresh pickle")
        df = await load_moex_futures_tickers_pickle()
        print("loaded local pickle")



    return df