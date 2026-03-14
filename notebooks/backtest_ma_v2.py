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

# === 4. 实际持仓（昨天信号，今天执行） ===
df["position"] = df["signal"].shift(1).fillna(0)

# === 5. 市场收益 ===
df["market_return"] = df["close"].pct_change().fillna(0)

# === 6. 找出交易点 ===
# position变化：0->1 是买入，1->0 是卖出
df["trade"] = df["position"].diff().fillna(0)

# === 7. 加手续费 ===
fee_rate = 0.001  # 单边手续费 0.1%

# 正常持仓收益
df["strategy_return"] = df["position"] * df["market_return"]

# 如果当天发生交易，扣手续费
# 买入 trade = 1，卖出 trade = -1，都扣一次手续费
df.loc[df["trade"] != 0, "strategy_return"] = df.loc[df["trade"] != 0, "strategy_return"] - fee_rate

df["strategy_return"] = df["strategy_return"].fillna(0)

# === 8. 净值曲线 ===
df["equity_curve"] = (1 + df["strategy_return"]).cumprod()
df["market_curve"] = (1 + df["market_return"]).cumprod()

# === 9. 生成买卖点表 ===
buy_points = df[df["trade"] == 1].copy()
sell_points = df[df["trade"] == -1].copy()

print("=== 买点 ===")
print(buy_points[["close", "ma5", "ma20", "signal", "position"]])
print()

print("=== 卖点 ===")
print(sell_points[["close", "ma5", "ma20", "signal", "position"]])
print()

print("=== 最后15行结果 ===")
print(df[["close", "signal", "position", "trade", "market_return", "strategy_return", "equity_curve"]].tail(15))
print()

total_return = df["equity_curve"].iloc[-1] - 1
print(f"策略总收益(含手续费): {total_return:.2%}")

# === 10. 导出交易记录 ===
trades = df[df["trade"] != 0][["close", "trade"]].copy()
trades["action"] = trades["trade"].map({1.0: "BUY", -1.0: "SELL"})
trades.to_csv("data/processed/trades_sample.csv")

# === 11. 画图：价格 + 均线 + 买卖点 ===
plt.figure(figsize=(12, 6))
plt.plot(df.index, df["close"], label="Close")
plt.plot(df.index, df["ma5"], label="MA5")
plt.plot(df.index, df["ma20"], label="MA20")

plt.scatter(buy_points.index, buy_points["close"], marker="^", s=100, label="Buy")
plt.scatter(sell_points.index, sell_points["close"], marker="v", s=100, label="Sell")

plt.title("MA Strategy with Buy/Sell Points")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# === 12. 画净值曲线 ===
plt.figure(figsize=(12, 6))
plt.plot(df.index, df["equity_curve"], label="Strategy Equity")
plt.plot(df.index, df["market_curve"], label="Buy and Hold")

plt.title("MA Strategy Backtest with Fee")
plt.xlabel("Date")
plt.ylabel("Net Value")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
