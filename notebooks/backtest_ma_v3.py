import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from engine.metrics import calculate_metrics, calculate_trade_stats
import pandas as pd
import matplotlib.pyplot as plt

# === 1. 读取数据 ===
df = pd.read_csv("data/processed/BTCUSDT_1d_full.csv")
df["datetime"] = pd.to_datetime(df["datetime"])
df = df.sort_values("datetime").reset_index(drop=True)

# === 2. 计算均线 ===
df["ma5"] = df["close"].rolling(5).mean()
df["ma20"] = df["close"].rolling(20).mean()

# === 3. 生成信号（当天收盘后看到） ===
df["signal"] = 0
df.loc[df["ma5"] > df["ma20"], "signal"] = 1

# === 4. 找到信号变化点 ===
# signal: 0 -> 1 表示出现买入信号
# signal: 1 -> 0 表示出现卖出信号
df["signal_change"] = df["signal"].diff().fillna(0)

# === 5. 回测参数 ===
initial_cash = 100000.0
cash = initial_cash
btc = 0.0
fee_rate = 0.001  # 0.1%

equity_list = []
position_list = []
trade_records = []

# === 6. 逐行回测 ===
for i in range(len(df)):
    row = df.iloc[i]
    current_date = row["datetime"]
    current_open = row["open"]
    current_close = row["close"]

    # 默认今天先不交易
    action = "HOLD"

    # 注意：
    # 今天是否交易，取决于“昨天收盘后”产生的信号变化
    # 所以要看 i-1 那一行的 signal_change
    if i > 0:
        prev_signal_change = df.iloc[i - 1]["signal_change"]

        # 昨天收盘后出买入信号，今天开盘买
        if prev_signal_change == 1 and cash > 0:
            buy_price = current_open
            fee = cash * fee_rate
            investable_cash = cash - fee
            btc = investable_cash / buy_price
            cash = 0.0
            action = "BUY"

            trade_records.append({
                "datetime": current_date,
                "action": "BUY",
                "price": buy_price,
                "fee": fee,
                "btc": btc,
                "cash_after": cash
            })

        # 昨天收盘后出卖出信号，今天开盘卖
        elif prev_signal_change == -1 and btc > 0:
            sell_price = current_open
            gross_amount = btc * sell_price
            fee = gross_amount * fee_rate
            cash = gross_amount - fee
            btc = 0.0
            action = "SELL"

            trade_records.append({
                "datetime": current_date,
                "action": "SELL",
                "price": sell_price,
                "fee": fee,
                "btc": btc,
                "cash_after": cash
            })

    # 计算今天收盘后的总资产
    equity = cash + btc * current_close

    equity_list.append(equity)
    position_list.append(1 if btc > 0 else 0)

# === 7. 保存回测结果 ===
df["position"] = position_list
df["equity"] = equity_list
df["equity_curve"] = df["equity"] / initial_cash

# 市场基准：买入并持有
df["market_return"] = df["close"].pct_change().fillna(0)
df["market_curve"] = (1 + df["market_return"]).cumprod()

# === 8. 生成交易记录表 ===
trades_df = pd.DataFrame(trade_records)

# 配对买卖，生成每笔完整交易
round_trips = []
current_buy = None

for _, trade in trades_df.iterrows():
    if trade["action"] == "BUY":
        current_buy = trade
    elif trade["action"] == "SELL" and current_buy is not None:
        pnl_pct = (trade["price"] - current_buy["price"]) / current_buy["price"] - 2 * fee_rate
        round_trips.append({
            "buy_date": current_buy["datetime"],
            "buy_price": current_buy["price"],
            "sell_date": trade["datetime"],
            "sell_price": trade["price"],
            "pnl_pct": pnl_pct
        })
        current_buy = None

round_trips_df = pd.DataFrame(round_trips)

# === 9. 输出结果 ===
print("=== 信号变化 ===")
print(df[["datetime", "close", "ma5", "ma20", "signal", "signal_change"]].tail(15))
print()

print("=== 交易记录 ===")
if len(trades_df) > 0:
    print(trades_df)
else:
    print("暂无交易记录")
print()

print("=== 完整买卖配对 ===")
if len(round_trips_df) > 0:
    print(round_trips_df)
else:
    print("暂无完整买卖配对（可能只有买入，还没卖出）")
print()

total_return = df["equity_curve"].iloc[-1] - 1
print(f"策略总收益: {total_return:.2%}")

# newwwwwwwwwwwwwww
# === 计算回测指标 ===
metrics = calculate_metrics(df)

print("\n=== 回测指标 ===")

print(f"Total Return: {metrics['total_return']:.2%}")
print(f"Annual Return: {metrics['annual_return']:.2%}")
print(f"Volatility: {metrics['volatility']:.2%}")
print(f"Sharpe Ratio: {metrics['sharpe']:.2f}")
print(f"Max Drawdown: {metrics['max_drawdown']:.2%}")
# === 交易统计 ===
trades_df = pd.DataFrame(trade_records)
trade_stats = calculate_trade_stats(round_trips_df)

print("\n=== 交易统计 ===")
print(f"Win Rate: {trade_stats['win_rate']:.2%}")
print(f"Average Win: {trade_stats['avg_win']:.2%}")
print(f"Average Loss: {trade_stats['avg_loss']:.2%}")
print(f"Profit/Loss Ratio: {trade_stats['profit_loss_ratio']:.2f}")
# === 10. 保存文件 ===
df.to_csv("data/processed/backtest_v3_result.csv", index=False)
trades_df.to_csv("data/processed/trades_v3.csv", index=False)
round_trips_df.to_csv("data/processed/round_trips_v3.csv", index=False)

# === 11. 画价格图 + 买卖点 ===
plt.figure(figsize=(12, 6))
plt.plot(df["datetime"], df["close"], label="Close")
plt.plot(df["datetime"], df["ma5"], label="MA5")
plt.plot(df["datetime"], df["ma20"], label="MA20")

if len(trades_df) > 0:
    buy_points = trades_df[trades_df["action"] == "BUY"]
    sell_points = trades_df[trades_df["action"] == "SELL"]

    if len(buy_points) > 0:
        plt.scatter(buy_points["datetime"], buy_points["price"], marker="^", s=120, label="Buy")
    if len(sell_points) > 0:
        plt.scatter(sell_points["datetime"], sell_points["price"], marker="v", s=120, label="Sell")

plt.title("MA Strategy with Next Open Execution")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# === 12. 画净值曲线 ===
plt.figure(figsize=(12, 6))
plt.plot(df["datetime"], df["equity_curve"], label="Strategy Equity")
plt.plot(df["datetime"], df["market_curve"], label="Buy and Hold")
plt.title("Backtest V3 - Next Open Execution")
plt.xlabel("Date")
plt.ylabel("Net Value")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
