from app.providers.moex.futures import load_moex_futures_tickers

async def get_active_futures():
    df = await load_moex_futures_tickers()
    # apply domain rules here
    return df