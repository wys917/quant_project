import pandas as pd
import matplotlib.pyplot as plt

file_path = "data/processed/BTCUSDT_1d_full.csv"

df = pd.read_csv(file_path)

# 转 datetime
df["datetime"] = pd.to_datetime(df["datetime"])

print("=== 基本信息 ===")
print(df.info())
print()

print("=== 前5行 ===")
print(df.head())
print()

print("=== 是否有空值 ===")
print(df.isnull().sum())
print()

print("=== 是否有重复时间 ===")
print(df["datetime"].duplicated().sum())
print()

print("=== 时间范围 ===")
print("开始：", df["datetime"].min())
print("结束：", df["datetime"].max())
print("总行数：", len(df))
print()

# 检查 OHLC 合理性
bad_high = ((df["high"] < df["open"]) | (df["high"] < df["close"])).sum()
bad_low = ((df["low"] > df["open"]) | (df["low"] > df["close"])).sum()

print("=== OHLC 合理性检查 ===")
print("high 异常行数：", bad_high)
print("low 异常行数：", bad_low)
print()

# 画收盘价曲线
plt.figure(figsize=(10, 5))
plt.plot(df["datetime"], df["close"])
plt.title("BTCUSDT Daily Close Price")
plt.xlabel("Date")
plt.ylabel("Close Price")
plt.grid(True)
plt.tight_layout()
plt.show()
