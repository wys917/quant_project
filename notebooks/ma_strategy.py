import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
df = pd.read_csv("data/processed/BTCUSDT_1d_full.csv")

df["datetime"] = pd.to_datetime(df["datetime"])

# 设置索引
df = df.set_index("datetime")

# 计算均线
df["ma5"] = df["close"].rolling(5).mean()
df["ma20"] = df["close"].rolling(20).mean()

# 生成交易信号
df["signal"] = 0

df.loc[df["ma5"] > df["ma20"], "signal"] = 1

print(df.head(25))

# 画图
plt.figure(figsize=(12,6))

plt.plot(df.index, df["close"], label="Close")
plt.plot(df.index, df["ma5"], label="MA5")
plt.plot(df.index, df["ma20"], label="MA20")

plt.title("BTCUSDT Moving Average Strategy")
plt.legend()
plt.grid(True)

plt.show()
