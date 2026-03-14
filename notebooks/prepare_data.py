import pandas as pd

# 读取 Binance 原始日线数据（无表头）
file_path = "data/raw/BTCUSDT-1d-2025-01.csv"
df = pd.read_csv(file_path, header=None)

# 给原始数据加列名
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

# 转成时间
df["datetime"] = pd.to_datetime(df["open_time"], unit="us")
# 只保留我们第一阶段需要的 6 列
df_clean = df[["datetime", "open", "high", "low", "close", "volume"]].copy()

# 排序
df_clean = df_clean.sort_values("datetime").reset_index(drop=True)

# 保存成标准格式
output_path = "data/processed/BTCUSDT_1d_sample.csv"
df_clean.to_csv(output_path, index=False)

print("清洗后的前 5 行：")
print(df_clean.head())
print()
print("数据条数：", len(df_clean))
print("起始时间：", df_clean["datetime"].min())
print("结束时间：", df_clean["datetime"].max())
print("已保存到：", output_path)
