import os
import asyncio
import pandas as pd
from moexalgo import Market
from requests import RequestException
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta
import pandas as pd

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


async def save_moex_futures_tickers_pickle_safe(
    base_name: str = "moex_futures_tickers"
) -> Path:
    """
    Async version:
    - Awaits ticker loading
    - Saves into data/moex_future/
    - Creates folder if missing
    - Uses atomic write
    """

    # ✅ Proper async call
    try:
        df = await load_moex_futures_tickers()
    except Exception as e:
        raise RuntimeError("Failed to load MOEX futures tickers") from e

    if not isinstance(df, pd.DataFrame):
        raise ValueError("load_moex_futures_tickers() did not return DataFrame")

    if df.empty:
        raise ValueError("MOEX futures tickers DataFrame is empty")

    # ---------------------------------------------------
    # 📁 Build path relative to project root
    # Assumes structure:
    # project/
    # ├── app/
    # └── data/
    #     └── moex_future/
    # ---------------------------------------------------

    PROJECT_ROOT = Path(__file__).resolve().parents[3]  
    # adjust if needed depending where this file lives

    target_dir = PROJECT_ROOT / "Data" / "moex_current_futures"
    target_dir.mkdir(parents=True, exist_ok=True)

    date_suffix = datetime.now(timezone.utc).strftime("%Y%m%d")
    path = target_dir / f"{base_name}_{date_suffix}.pkl"

    # ---------------------------------------------------
    # ✅ Atomic write (thread-safe)
    # ---------------------------------------------------

    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=target_dir,
        prefix=path.stem,
        suffix=".tmp"
    )
    os.close(tmp_fd)

    try:
        # writing pickle is blocking → offload to thread
        await asyncio.to_thread(df.to_pickle, tmp_path)
        Path(tmp_path).replace(path)
    except Exception:
        if Path(tmp_path).exists():
            Path(tmp_path).unlink()
        raise

    return path

async def load_moex_futures_tickers_pickle(
    base_name: str = "moex_futures_tickers",
    days_back: int = 0
) -> pd.DataFrame:
    """
    Async loader:
    - Searches in data/moex_current_futures
    - Looks back up to `days_back`
    - Loads most recent available pickle
    - Offloads blocking I/O to thread
    """

    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    target_dir = PROJECT_ROOT / "Data" / "moex_current_futures"

    if not target_dir.exists():
        raise FileNotFoundError(f"Directory does not exist: {target_dir}")

    today = datetime.now(timezone.utc).date()

    for i in range(days_back + 1):
        date_suffix = (today - timedelta(days=i)).strftime("%Y%m%d")
        candidate = target_dir / f"{base_name}_{date_suffix}.pkl"

        if candidate.exists():
            try:
                df = await asyncio.to_thread(pd.read_pickle, candidate)

                if not isinstance(df, pd.DataFrame) or df.empty:
                    raise ValueError(
                        f"File exists but DataFrame invalid/empty: {candidate}"
                    )

                return df

            except Exception as e:
                raise RuntimeError(
                    f"Failed to load pickle: {candidate}"
                ) from e

    raise FileNotFoundError(
        f"No MOEX futures tickers pickle found "
        f"in last {days_back} days inside {target_dir}"
    )

async def moex_futures_garbage_collector(
    base_name: str = "moex_futures_tickers"
) -> int:
    """
    Deletes all MOEX futures pickles in data/moex_current_futures
    that are not from the current day.

    Returns:
        int: number of files deleted
    """

    PROJECT_ROOT = Path(__file__).resolve().parents[3]
    target_dir = PROJECT_ROOT / "Data" / "moex_current_futures"

    if not target_dir.exists():
        return 0  # nothing to delete

    today_suffix = datetime.now(timezone.utc).strftime("%Y%m%d")
    deleted_count = 0

    for file in target_dir.glob(f"{base_name}_*.pkl"):
        if today_suffix not in file.name:
            try:
                # Delete file in thread to avoid blocking
                await asyncio.to_thread(file.unlink)
                deleted_count += 1
            except Exception as e:
                # Log or ignore failed deletions
                print(f"Failed to delete {file}: {e}")

    return deleted_count
