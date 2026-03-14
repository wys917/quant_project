import json
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from engine.metrics import calculate_metrics, calculate_trade_stats

STRATEGY_NAME = "ma_crossover_v3"
SYMBOL = "BTCUSDT"
DATA_FILE = ROOT_DIR / "data/processed/BTCUSDT_1d_full.csv"
RESULTS_DIR = ROOT_DIR / "data/processed/results"


def build_round_trips(trades_df, fee_rate):
    round_trips = []
    current_buy = None

    for _, trade in trades_df.iterrows():
        if trade["action"] == "BUY":
            current_buy = trade
        elif trade["action"] == "SELL" and current_buy is not None:
            holding_days = int((trade["datetime"] - current_buy["datetime"]).days)
            pnl_pct = (trade["price"] - current_buy["price"]) / current_buy["price"] - 2 * fee_rate
            round_trips.append(
                {
                    "buy_date": current_buy["datetime"],
                    "buy_price": current_buy["price"],
                    "sell_date": trade["datetime"],
                    "sell_price": trade["price"],
                    "pnl_pct": pnl_pct,
                    "holding_days": holding_days,
                }
            )
            current_buy = None

    return pd.DataFrame(
        round_trips,
        columns=["buy_date", "buy_price", "sell_date", "sell_price", "pnl_pct", "holding_days"],
    )


def save_results(df, trades_df, round_trips_df, metrics, trade_stats):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    metrics_payload = {
        "strategy_name": STRATEGY_NAME,
        "symbol": SYMBOL,
        "start_date": str(df["datetime"].min()),
        "end_date": str(df["datetime"].max()),
        "total_return": metrics["total_return"],
        "annual_return": metrics["annual_return"],
        "volatility": metrics["volatility"],
        "sharpe": metrics["sharpe"],
        "max_drawdown": metrics["max_drawdown"],
        "win_rate": trade_stats["win_rate"],
        "avg_win": trade_stats["avg_win"],
        "avg_loss": trade_stats["avg_loss"],
        "profit_loss_ratio": trade_stats["profit_loss_ratio"],
        "total_trades": trade_stats["total_trades"],
    }

    equity_curve_df = df[["datetime", "equity", "equity_curve", "market_curve", "position", "close"]].copy()

    with open(RESULTS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2, ensure_ascii=False)

    trades_df.to_csv(RESULTS_DIR / "trades.csv", index=False)
    round_trips_df.to_csv(RESULTS_DIR / "round_trips.csv", index=False)
    equity_curve_df.to_csv(RESULTS_DIR / "equity_curve.csv", index=False)

    summary_lines = [
        f"Strategy: {STRATEGY_NAME}",
        f"Symbol: {SYMBOL}",
        f"Backtest Range: {df['datetime'].min()} to {df['datetime'].max()}",
        f"Total Return: {metrics['total_return']:.2%}",
        f"Annual Return: {metrics['annual_return']:.2%}",
        f"Volatility: {metrics['volatility']:.2%}",
        f"Sharpe Ratio: {metrics['sharpe']:.2f}",
        f"Max Drawdown: {metrics['max_drawdown']:.2%}",
        f"Win Rate: {trade_stats['win_rate']:.2%}",
        f"Average Win: {trade_stats['avg_win']:.2%}",
        f"Average Loss: {trade_stats['avg_loss']:.2%}",
        f"Profit/Loss Ratio: {trade_stats['profit_loss_ratio']:.2f}",
        f"Total Trades: {trade_stats['total_trades']}",
    ]
    (RESULTS_DIR / "summary.txt").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    # 兼容此前的输出文件，保留给已有脚本和查看方式使用
    df.to_csv(ROOT_DIR / "data/processed/backtest_v3_result.csv", index=False)
    trades_df.to_csv(ROOT_DIR / "data/processed/trades_v3.csv", index=False)
    round_trips_df.to_csv(ROOT_DIR / "data/processed/round_trips_v3.csv", index=False)


def maybe_show_plots():
    if "agg" not in matplotlib.get_backend().lower():
        plt.show()
    else:
        plt.close("all")


# === 1. 读取数据 ===
df = pd.read_csv(DATA_FILE)
df["datetime"] = pd.to_datetime(df["datetime"])
df = df.sort_values("datetime").reset_index(drop=True)

# === 2. 计算均线 ===
df["ma5"] = df["close"].rolling(5).mean()
df["ma20"] = df["close"].rolling(20).mean()

# === 3. 生成信号（当天收盘后看到） ===
df["signal"] = 0
df.loc[df["ma5"] > df["ma20"], "signal"] = 1

# === 4. 找到信号变化点 ===
df["signal_change"] = df["signal"].diff().fillna(0)

# === 5. 回测参数 ===
initial_cash = 100000.0
cash = initial_cash
btc = 0.0
fee_rate = 0.001

equity_list = []
position_list = []
trade_records = []

# === 6. 逐行回测 ===
for i in range(len(df)):
    row = df.iloc[i]
    current_date = row["datetime"]
    current_open = row["open"]
    current_close = row["close"]

    if i > 0:
        prev_signal_change = df.iloc[i - 1]["signal_change"]

        if prev_signal_change == 1 and cash > 0:
            buy_price = current_open
            fee = cash * fee_rate
            investable_cash = cash - fee
            btc = investable_cash / buy_price
            cash = 0.0

            trade_records.append(
                {
                    "datetime": current_date,
                    "action": "BUY",
                    "price": buy_price,
                    "fee": fee,
                    "btc": btc,
                    "cash_after": cash,
                }
            )
        elif prev_signal_change == -1 and btc > 0:
            sell_price = current_open
            gross_amount = btc * sell_price
            fee = gross_amount * fee_rate
            cash = gross_amount - fee
            btc = 0.0

            trade_records.append(
                {
                    "datetime": current_date,
                    "action": "SELL",
                    "price": sell_price,
                    "fee": fee,
                    "btc": btc,
                    "cash_after": cash,
                }
            )

    equity = cash + btc * current_close
    equity_list.append(equity)
    position_list.append(1 if btc > 0 else 0)

# === 7. 生成净值曲线 ===
df["position"] = position_list
df["equity"] = equity_list
df["equity_curve"] = df["equity"] / initial_cash
df["market_return"] = df["close"].pct_change().fillna(0)
df["market_curve"] = (1 + df["market_return"]).cumprod()

# === 8. 生成交易记录和完整买卖配对 ===
trades_df = pd.DataFrame(
    trade_records,
    columns=["datetime", "action", "price", "fee", "btc", "cash_after"],
)
round_trips_df = build_round_trips(trades_df, fee_rate)

# === 9. 计算指标 ===
metrics = calculate_metrics(df)
trade_stats = calculate_trade_stats(round_trips_df)

# === 10. 打印结果 ===
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

print(f"策略总收益: {metrics['total_return']:.2%}")

print("\n=== 回测指标 ===")
print(f"Total Return: {metrics['total_return']:.2%}")
print(f"Annual Return: {metrics['annual_return']:.2%}")
print(f"Volatility: {metrics['volatility']:.2%}")
print(f"Sharpe Ratio: {metrics['sharpe']:.2f}")
print(f"Max Drawdown: {metrics['max_drawdown']:.2%}")

print("\n=== 交易统计 ===")
print(f"Win Rate: {trade_stats['win_rate']:.2%}")
print(f"Average Win: {trade_stats['avg_win']:.2%}")
print(f"Average Loss: {trade_stats['avg_loss']:.2%}")
print(f"Profit/Loss Ratio: {trade_stats['profit_loss_ratio']:.2f}")
print(f"Total Trades: {trade_stats['total_trades']}")

# === 11. 保存标准化结果 ===
save_results(df, trades_df, round_trips_df, metrics, trade_stats)

# === 12. 画价格图 + 买卖点 ===
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

# === 13. 画净值曲线 ===
plt.figure(figsize=(12, 6))
plt.plot(df["datetime"], df["equity_curve"], label="Strategy Equity")
plt.plot(df["datetime"], df["market_curve"], label="Buy and Hold")
plt.title("Backtest V3 - Next Open Execution")
plt.xlabel("Date")
plt.ylabel("Net Value")
plt.legend()
plt.grid(True)
plt.tight_layout()

maybe_show_plots()
