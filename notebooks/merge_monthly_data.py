import pandas as pd
from pathlib import Path

input_dir = Path("data/raw/monthly")
output_file = Path("data/processed/BTCUSDT_1d_full.csv")

all_files = sorted(input_dir.glob("BTCUSDT-1d-*.csv"))

dfs = []

for file in all_files:
    df = pd.read_csv(file, header=None)

    df.columns = [
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
        "ignore"
    ]

    # 自动判断时间单位：13位毫秒，16位微秒
    sample_ts = str(int(df.loc[0, "open_time"]))
    if len(sample_ts) >= 16:
        unit = "us"
    else:
        unit = "ms"

    df["datetime"] = pd.to_datetime(df["open_time"], unit=unit)

    df = df[["datetime", "open", "high", "low", "close", "volume"]].copy()
    dfs.append(df)

merged = pd.concat(dfs, ignore_index=True)
merged = merged.sort_values("datetime").drop_duplicates(subset=["datetime"]).reset_index(drop=True)

merged.to_csv(output_file, index=False)

print("文件数：", len(all_files))
print("总行数：", len(merged))
print("开始时间：", merged["datetime"].min())
print("结束时间：", merged["datetime"].max())
print("保存到：", output_file)
print()
print(merged.head())
print()
print(merged.tail())
