import asyncio
from datetime import UTC, datetime

import pandas as pd
import pytz
from sqlalchemy import select

from dateutil.relativedelta import relativedelta

from app.core.commands.securities import get_or_create_security_id
from app.db.sessions import AsyncSessionLocal
from app.domain.constants.assets import ASSETS_TO_PREFIX
from app.domain.constants.futures import MMVB_FUTURES_MONTH_CODES
from app.models.enum_helpers import PlatformEnum, TimeframeEnum
from app.models.historicalcandle import HistoricalCandle
from app.core.commands.candels import insert_candles_from_df

def get_prefix(asset: str, prefix_map: dict[str, str] = ASSETS_TO_PREFIX) -> str:
    return prefix_map.get(asset)

def generate_futures_contracts(
    base: str,
    start_month: str,
    end_month: str | None = None
) -> list[str]:
    """
    base        : e.g. 'BR'
    start_month: 'YYYY-MM'
    end_month  : 'YYYY-MM' (optional, defaults to current month)

    returns list like ['BRZ3', 'BRF4', ...]
    """

    start = datetime.strptime(start_month, "%Y-%m")

    if end_month:
        end = datetime.strptime(end_month, "%Y-%m")
    else:
        now = datetime.now(UTC)
        end = datetime(now.year, now.month, 1, tzinfo=UTC)  

    contracts = []
    current = start

    while current <= end:
        month_code = MMVB_FUTURES_MONTH_CODES[current.month]
        year_digit = str(current.year)[-1]
        contracts.append(f"{base}{month_code}{year_digit}")
        current += relativedelta(months=1)

    return contracts


async def get_symbol_info_field_async(
    ap_provider,
    exchange: str,
    symbol: str,
    field: str,
):
    """
    Async wrapper around sync provider.
    Runs blocking I/O in thread pool.
    """
    try:
        si = await asyncio.to_thread(
            ap_provider.get_symbol_info,
            exchange,
            symbol,
        )

        if not si:
            return None

        return si.get(field)

    except Exception:
        return None

async def build_contract_limits_df(
    instrument: str,
    ap_provider,
    exchange: str = "MOEX",
    start_month: str = "2022-03",
    end_month: str = "2026-03",
):
    """
    Generate a dataframe with begin/end date limits for futures contracts.

    Parameters
    ----------
    instrument : str
        Instrument name (e.g. 'VTBR')
    ap_provider :
        Provider object used by get_symbol_info_field
    exchange : str
        Exchange name (default: 'MOEX')
    start_month : str
        Start month in YYYY-MM format
    end_month : str
        End month in YYYY-MM format

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: symbol, cancellation, begin, end
    """

    # 1. Generate contracts
    contracts = generate_futures_contracts(
        base=get_prefix(instrument),
        start_month=start_month,
        end_month=end_month
    )

    # 2️⃣ Fetch cancellation dates concurrently
    tasks = [
        get_symbol_info_field_async(
            ap_provider,
            exchange,
            symbol,
            "cancellation",
        )
        for symbol in contracts
    ]

    values = await asyncio.gather(*tasks)

    rows = [
        {"symbol": symbol, "cancellation": value}
        for symbol, value in zip(contracts, values)
    ]

    df_contracts = pd.DataFrame(rows)

    # 3. Clean & sort
    df_clean = (
        df_contracts
        .dropna(subset=["cancellation"])
        .assign(cancellation=lambda x: pd.to_datetime(x["cancellation"]))
        .sort_values("cancellation", ascending=False)
        .reset_index(drop=True)
    )

    if df_clean.empty or len(df_clean) < 2:
        return pd.DataFrame(columns=["symbol", "cancellation", "begin", "end"])

    df = df_clean.copy()

    # 4. Calculate begin / end limits
    df["begin"] = df["cancellation"].shift(-1) - pd.Timedelta(days=2)
    df["end"] = df["cancellation"] - pd.Timedelta(days=2)

    # ensure first row end is correct
    df.loc[0, "end"] = df.loc[0, "cancellation"] - pd.Timedelta(days=2)

    # 5. Drop incomplete rows
    df = df.dropna(subset=["begin", "end"]).reset_index(drop=True)

    return df

import logging  # Выводим лог на консоль и в файл
logger = logging.getLogger('AlorPy.Bars')  # Будем вести лог. Определяем здесь, т.к. возможен внешний вызов ф-ии
dt_format = '%d.%m.%Y %H:%M'  # Формат представления даты и времени в файле истории. По умолчанию русский формат

def get_candles_from_provider(ap_provider, class_code, security_code, tf, seconds_from=0) -> pd.DataFrame:
    """Получение бар из провайдера

    :param AlorPy ap_provider: Провайдер Alor
    :param str class_code: Код режима торгов
    :param str security_code: Код тикера
    :param str tf: Временной интервал https://ru.wikipedia.org/wiki/Таймфрейм
    :param int seconds_from: Дата и время открытия первого бара в кол-ве секунд, прошедших с 01.01.1970 00:00 UTC
    """
    
    time_frame, _ = ap_provider.timeframe_to_alor_timeframe(tf)  # Временной интервал Alor
    alor_board = ap_provider.board_to_alor_board(class_code)  # Код режима торгов Алора
    exchange = ap_provider.get_exchange(alor_board, security_code)  # Биржа
    if not exchange:
        exchange = "MOEX"  # fallback for futures
    print("Exchange:", exchange)
    if not exchange:  # Если биржа не была найдена
        logger.error(f'Биржа для тикера {class_code}.{security_code} не найдена')
        return pd.DataFrame()  # то выходим, дальше не продолжаем
    logger.info(f'Получение истории {class_code}.{security_code} {tf} из Alor')
    history = ap_provider.get_history(exchange, security_code, time_frame, seconds_from)  # Запрос истории рынка
    if not history:  # Если бары не получены
        logger.error('Ошибка при получении истории: История не получена')
        return pd.DataFrame()  # то выходим, дальше не продолжаем
    if 'history' not in history:  # Если бар нет в словаре
        logger.error(f'Ошибка при получении истории: {history}')
        return pd.DataFrame()  # то выходим, дальше не продолжаем
    new_bars = history['history']  # Получаем все бары из Alor
    if len(new_bars) == 0:  # Если новых бар нет
        logger.info('Новых записей нет')
        return pd.DataFrame()  # то выходим, дальше не продолжаем
    pd_bars = pd.json_normalize(new_bars)  # Переводим список бар в pandas DataFrame
    pd_bars['datetime'] = pd.to_datetime(pd_bars['time'], unit='s')  # Дата и время в UTC для дневных бар и выше
    if type(time_frame) is not str:  # Для внутридневных бар (time_frame число)
        pd_bars['datetime'] = pd_bars['datetime'].dt.tz_localize('UTC').dt.tz_convert(ap_provider.tz_msk).dt.tz_localize(None)  # Переводим в рыночное время МСК
    pd_bars.index = pd_bars['datetime']  # В индекс ставим дату/время
    pd_bars = pd_bars[['datetime', 'open', 'high', 'low', 'close', 'volume']]  # Отбираем нужные колонки. Дата и время нужна, чтобы не удалять одинаковые OHLCV на разное время
    lot_size = ap_provider.lots_to_size(exchange, security_code, 1)  # Кол-во акций в штуках в одном лоте
    pd_bars['volume'] = pd_bars['volume'].astype('int64') * lot_size  # Объемы в штуках могут быть только целыми
    si = ap_provider.get_symbol_info(exchange, security_code)  # Спецификация тикера
    if not si['decimals']:  # Если кол-во десятичных знаков = 0, то цены - целые значения
        pd_bars['open'] = pd_bars['open'].astype('int64')
        pd_bars['high'] = pd_bars['high'].astype('int64')
        pd_bars['low'] = pd_bars['low'].astype('int64')
        pd_bars['close'] = pd_bars['close'].astype('int64')
    logger.info(f'Первый бар    : {pd_bars.index[0]:{dt_format}}')
    logger.info(f'Последний бар : {pd_bars.index[-1]:{dt_format}}')
    logger.info(f'Кол-во бар    : {len(pd_bars)}')
    return pd_bars

async def get_candles_from_provider_async(
    ap_provider,
    class_code,
    security_code,
    tf,
    seconds_from=0,
):
    return await asyncio.to_thread(
        get_candles_from_provider,
        ap_provider,
        class_code,
        security_code,
        tf,
        seconds_from,
    )

async def download_continuous_future_glue_no_stop_async(
    df: pd.DataFrame,
    ap_provider,
    class_code: str,
    tf: str,
    max_concurrent: int = 5,  # protect API
) -> pd.DataFrame:

    df = df.reset_index(drop=True)
    collected = []

    semaphore = asyncio.Semaphore(max_concurrent)

    moscow_tz = pytz.timezone("Europe/Moscow")
    current_date = (
        pd.Timestamp.now(tz=moscow_tz)
        .normalize()
        .tz_localize(None)
    )

    async def fetch_one(i: int):
        async with semaphore:
            
            

            symbol = df.loc[i, "symbol"]
            start_date = df.loc[i, "begin"]
            end_date = df.loc[i, "end"]
            
            print("Fetching:", class_code, symbol, tf)

            if pd.isna(start_date):
                start_date = current_date

            if start_date > end_date:
                return None

            try:
                pd_bars = await get_candles_from_provider_async(
                    ap_provider,
                    class_code,
                    symbol,
                    tf,
                )
            except Exception:
                return None

            if pd_bars is None or pd_bars.empty:
                return None

            mask = (
                (pd_bars.index >= start_date)
                & (pd_bars.index <= end_date)
            )

            # pd_bars = pd_bars.loc[mask]
            pd_bars = pd_bars.loc[mask].copy()

            if pd_bars.empty:
                return None

            # pd_bars["symbol"] = symbol
            pd_bars.loc[:, "symbol"] = symbol
            return pd_bars

    # create tasks
    tasks = [
        fetch_one(i)
        for i in reversed(range(len(df)))
    ]

    results = await asyncio.gather(*tasks)

    collected = [r for r in results if r is not None]

    if not collected:
        return pd.DataFrame()

    result = (
        pd.concat(reversed(collected))
        .sort_index()
    )

    result = result[~result.index.duplicated(keep="first")]

    return result



class FuturesHistoryDownloader:
    """
    Full + incremental futures history downloader.
    """

    TIMEFRAME_MAP = {
        TimeframeEnum.M1: "M1",
        TimeframeEnum.M5: "M5",
        TimeframeEnum.M15: "M15",
        TimeframeEnum.M30: "M30",
        TimeframeEnum.H1: "M60",
        TimeframeEnum.D1: "D1",
    }

    CLASS_CODE = "SPBFUT"

    def __init__(
        self,
        instrument: str,
        ap_provider,
        security_id: int,
        exchange: str = "MOEX",
        start_month: str = "2022-03",
        end_month: str | None = None,
    ):
        self.instrument = instrument
        self.ap_provider = ap_provider
        self.exchange = exchange
        self.start_month = start_month
        self.end_month = end_month
        self.security_id = security_id

        # self.security_id = get_or_create_security_id(
        #     name=instrument,
        #     platform=PlatformEnum.MOEX,
        # )
    
    
    @classmethod
    async def create(
        cls,
        instrument: str,
        ap_provider,
        exchange: str = "MOEX",
        start_month: str = "2022-03",
        end_month: str | None = None,
    ):
        security_id = await get_or_create_security_id(
            name=instrument,
            platform=PlatformEnum.MOEX,
        )

        return cls(
            instrument=instrument,
            ap_provider=ap_provider,
            security_id=security_id,
            exchange=exchange,
            start_month=start_month,
            end_month=end_month,
        )

    # --------------------------------------------------
    # DB helpers
    # --------------------------------------------------

    
    async def _get_last_stored_datetime(
        self,
        timeframe: TimeframeEnum,
    ) -> datetime | None:

        async with AsyncSessionLocal() as session:
            stmt = (
                select(HistoricalCandle.datetime)
                .where(
                    HistoricalCandle.security_id == self.security_id,
                    HistoricalCandle.timeframe == timeframe,
                )
                .order_by(HistoricalCandle.datetime.desc())
                .limit(1)
            )

            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    def _normalize_candles_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize candle DataFrame to DB-ready format.
        - datetime as a column
        - UTC timezone
        - no symbol column
        - clean index
        """
        df = df.copy()

        # 1️⃣ If datetime is index → move to column
        if isinstance(df.index, pd.DatetimeIndex):
            df["datetime"] = df.index

        # 2️⃣ Ensure datetime column exists
        if "datetime" not in df.columns:
            raise ValueError("DataFrame must contain 'datetime'")

        # 3️⃣ Normalize timezone
        df["datetime"] = pd.to_datetime(df["datetime"], utc=True)

        # 4️⃣ Drop junk columns
        for col in ("symbol",):
            if col in df.columns:
                df.drop(columns=col, inplace=True)

        # 5️⃣ Enforce column order (optional but nice)
        return df[
            ["datetime", "open", "high", "low", "close", "volume"]
        ].reset_index(drop=True)
    



    # --------------------------------------------------
    # Contract limits
    # --------------------------------------------------

    async def _build_limits(
        self,
        start_override: datetime | None = None,
    ) -> pd.DataFrame:
        df = await build_contract_limits_df(
            instrument=self.instrument,
            ap_provider=self.ap_provider,
            exchange=self.exchange,
            start_month=self.start_month,
            end_month=self.end_month
            # or datetime.now(UTC).strftime("%Y-%m"),
        )

        if df.empty:
            raise RuntimeError(
                f"No contract limits for {self.instrument}"
            )

        if start_override is not None:
            df["end"] = df["end"].where(
                df["end"] >= start_override,
                start_override,
            )
            df = df[df["end"] >= start_override]

        return df.reset_index(drop=True)

    # --------------------------------------------------
    # Download
    # --------------------------------------------------


    
    async def _download_continuous(
        self,
        df_limits: pd.DataFrame,
        tf: str,
    ) -> pd.DataFrame:

        df = await download_continuous_future_glue_no_stop_async(
            df=df_limits,
            ap_provider=self.ap_provider,
            class_code=self.CLASS_CODE,
            tf=tf,
        )

        if df.empty:
            return df

        return self._normalize_candles_df(df)

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    async def update_timeframe(
        self,
        timeframe: TimeframeEnum,
        mode: str = "incremental",  # "full" or "incremental"
    ) -> int:
        tf_alor = self.TIMEFRAME_MAP[timeframe]

        last_dt = None
        if mode == "incremental":
            last_dt = await self._get_last_stored_datetime(timeframe)
        
        print("Last dt:", last_dt)

        df_limits = await self._build_limits(start_override=last_dt)
        
        print("Limits rows:", len(df_limits))
        print(df_limits.head())

        df = await self._download_continuous(df_limits, tf_alor)
        
        print("Last stored datetime:", last_dt)
        print("Limits rows:", len(df_limits))
        print("Downloaded rows:", len(df))

        if df.empty:
            return 0

        if last_dt is not None:
            df = df[df["datetime"] > last_dt]

        return await insert_candles_from_df(
            df=df,
            security_id=self.security_id,
            timeframe=timeframe,
        )

    
    async def update_all(
        self,
        mode: str = "incremental",
        timeframes: list[TimeframeEnum] | None = None,
    ) -> dict[TimeframeEnum, int]:

        if timeframes is None:
            timeframes = [
                TimeframeEnum.M1,
                TimeframeEnum.M5,
                TimeframeEnum.M15,
                TimeframeEnum.H1,
                TimeframeEnum.D1,
            ]

        async def run_tf(tf: TimeframeEnum):
            try:
                inserted = await self.update_timeframe(tf, mode=mode)
                print(
                    f"[OK] {self.instrument} {tf.value} "
                    f"({mode}): {inserted}"
                )
                return tf, inserted

            except Exception as e:
                print(f"[FAIL] {self.instrument} {tf.value}: {e}")
                return tf, 0

        tasks = [run_tf(tf) for tf in timeframes]

        results_list = await asyncio.gather(*tasks)

        return dict(results_list)
