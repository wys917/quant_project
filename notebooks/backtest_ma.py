import pandas as pd
import matplotlib.pyplot as plt

# === 1. 读取数据 ===
df = pd.read_csv("data/processed/BTCUSDT_1d_sample.csv")
df["datetime"] = pd.to_datetime(df["datetime"])
df = df.set_index("datetime")

# === 2. 计算均线 ===
df["ma5"] = df["close"].rolling(5).mean()
df["ma20"] = df["close"].rolling(20).mean()

# === 3. 生成信号 ===
df["signal"] = 0
df.loc[df["ma5"] > df["ma20"], "signal"] = 1

# === 4. 生成持仓 ===
# 用昨天的信号，决定今天是否持仓，避免“今天看完今天收盘才买入”的问题
df["position"] = df["signal"].shift(1)
df["position"] = df["position"].fillna(0)

# === 5. 计算市场每日涨跌幅 ===
df["market_return"] = df["close"].pct_change()

# === 6. 计算策略每日收益 ===
# 如果今天持仓，就吃到今天的涨跌幅；如果空仓，收益就是 0
df["strategy_return"] = df["position"] * df["market_return"]
df["strategy_return"] = df["strategy_return"].fillna(0)

# === 7. 计算净值曲线 ===
# 假设初始资金是 1
df["equity_curve"] = (1 + df["strategy_return"]).cumprod()
df["market_curve"] = (1 + df["market_return"].fillna(0)).cumprod()

# === 8. 打印结果 ===
print(df[["close", "ma5", "ma20", "signal", "position", "market_return", "strategy_return", "equity_curve"]].tail(15))

total_return = df["equity_curve"].iloc[-1] - 1
print()
print(f"策略总收益: {total_return:.2%}")

# === 9. 画图 ===
plt.figure(figsize=(12, 6))
plt.plot(df.index, df["equity_curve"], label="Strategy Equity")
plt.plot(df.index, df["market_curve"], label="Buy and Hold")
plt.title("MA Strategy Backtest")
plt.xlabel("Date")
plt.ylabel("Net Value")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
