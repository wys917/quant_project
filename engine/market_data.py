import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd

BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"


def load_processed_data(file_path):
    file_path = Path(file_path)
    df = pd.read_csv(file_path)
    df["datetime"] = pd.to_datetime(df["datetime"])
    return df.sort_values("datetime").reset_index(drop=True)


def fetch_binance_klines(symbol="BTCUSDT", interval="1h", limit=200):
    params = urlencode({"symbol": symbol, "interval": interval, "limit": limit})
    url = f"{BINANCE_KLINES_URL}?{params}"

    with urlopen(url, timeout=10) as response:
        rows = json.loads(response.read().decode("utf-8"))

    df = pd.DataFrame(
        rows,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        ],
    )

    df["datetime"] = pd.to_datetime(df["open_time"], unit="ms")
    numeric_cols = ["open", "high", "low", "close", "volume"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df[["datetime", "open", "high", "low", "close", "volume"]].dropna().reset_index(drop=True)
