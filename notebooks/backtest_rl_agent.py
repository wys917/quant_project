import json
import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from agent.agent_report import generate_report
from engine.market_data import load_processed_data
from engine.metrics import calculate_metrics, calculate_trade_stats
from rl.features import STATE_FEATURE_NAMES, add_rl_features, build_state
from rl.q_learning_agent import ACTION_NAMES, QLearningAgent

STRATEGY_NAME = "rl_q_learning_v1"
MODEL_NAME = "tabular_q_learning"
SYMBOL = "BTCUSDT"
DATA_FILE = ROOT_DIR / "data/processed/BTCUSDT_1d_full.csv"
RESULTS_DIR = ROOT_DIR / "data/processed/results_rl"
REPORT_FILE = ROOT_DIR / "report/strategy_report.md"

INITIAL_CASH = 100000.0
FEE_RATE = 0.001
TRAIN_RATIO = 0.7
EPISODES = 80
RANDOM_SEED = 42


def build_round_trips(trades_df):
    round_trips = []
    current_buy = None

    for _, trade in trades_df.iterrows():
        if trade["action"] == "BUY":
            current_buy = trade
        elif trade["action"] == "SELL" and current_buy is not None:
            holding_days = int((pd.to_datetime(trade["datetime"]) - pd.to_datetime(current_buy["datetime"])).days)
            pnl_pct = (trade["price"] - current_buy["price"]) / current_buy["price"] - 2 * FEE_RATE
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


def run_episode(feature_df, agent, training=True):
    cash = INITIAL_CASH
    btc = 0.0
    prev_equity = INITIAL_CASH

    equity_records = [
        {
            "datetime": feature_df.iloc[0]["datetime"],
            "close": feature_df.iloc[0]["close"],
            "equity": INITIAL_CASH,
            "position": 0,
            "ma5": feature_df.iloc[0]["ma5"],
            "ma20": feature_df.iloc[0]["ma20"],
            "rsi14": feature_df.iloc[0]["rsi14"],
            "macd_hist": feature_df.iloc[0]["macd_hist"],
        }
    ]
    trade_records = []
    decision_records = []
    total_reward = 0.0

    for i in range(len(feature_df) - 1):
        row = feature_df.iloc[i]
        next_row = feature_df.iloc[i + 1]
        position_before = 1 if btc > 0 else 0

        state = build_state(row, position_before)
        q_values = agent.get_q_values(state).copy()
        action = agent.select_action(state, training=training)

        chosen_action_name = ACTION_NAMES[action]
        executed_action_name = "HOLD"
        fee = 0.0
        invalid_penalty = 0.0

        if action == 1:
            if cash > 0:
                buy_price = next_row["open"]
                fee = cash * FEE_RATE
                investable_cash = cash - fee
                btc = investable_cash / buy_price
                cash = 0.0
                executed_action_name = "BUY"

                trade_records.append(
                    {
                        "datetime": next_row["datetime"],
                        "action": "BUY",
                        "price": buy_price,
                        "fee": fee,
                        "btc": btc,
                        "cash_after": cash,
                    }
                )
            else:
                invalid_penalty = -0.05

        elif action == 2:
            if btc > 0:
                sell_price = next_row["open"]
                gross_amount = btc * sell_price
                fee = gross_amount * FEE_RATE
                cash = gross_amount - fee
                btc = 0.0
                executed_action_name = "SELL"

                trade_records.append(
                    {
                        "datetime": next_row["datetime"],
                        "action": "SELL",
                        "price": sell_price,
                        "fee": fee,
                        "btc": btc,
                        "cash_after": cash,
                    }
                )
            else:
                invalid_penalty = -0.05

        next_equity = cash + btc * next_row["close"]
        position_after = 1 if btc > 0 else 0

        if prev_equity > 0:
            reward = ((next_equity - prev_equity) / prev_equity) * 100 + invalid_penalty
        else:
            reward = invalid_penalty

        next_state = build_state(next_row, position_after)
        if training:
            agent.update(state, action, reward, next_state)

        total_reward += reward
        prev_equity = next_equity

        decision_records.append(
            {
                "decision_datetime": row["datetime"],
                "execution_datetime": next_row["datetime"],
                "state": str(state),
                "chosen_action": action,
                "chosen_action_name": chosen_action_name,
                "executed_action_name": executed_action_name,
                "reward": reward,
                "position_before": position_before,
                "position_after": position_after,
                "close": row["close"],
                "next_open": next_row["open"],
                "next_close": next_row["close"],
                "ma_gap": row["ma_gap"],
                "rsi14": row["rsi14"],
                "macd_hist": row["macd_hist"],
                "momentum_5": row["momentum_5"],
                "volume_ratio": row["volume_ratio"],
                "q_hold": float(q_values[0]),
                "q_buy": float(q_values[1]),
                "q_sell": float(q_values[2]),
            }
        )

        equity_records.append(
            {
                "datetime": next_row["datetime"],
                "close": next_row["close"],
                "equity": next_equity,
                "position": position_after,
                "ma5": next_row["ma5"],
                "ma20": next_row["ma20"],
                "rsi14": next_row["rsi14"],
                "macd_hist": next_row["macd_hist"],
            }
        )

    equity_df = pd.DataFrame(equity_records)
    equity_df["datetime"] = pd.to_datetime(equity_df["datetime"])
    equity_df["equity_curve"] = equity_df["equity"] / INITIAL_CASH
    equity_df["market_return"] = equity_df["close"].pct_change().fillna(0)
    equity_df["market_curve"] = (1 + equity_df["market_return"]).cumprod()

    trades_df = pd.DataFrame(
        trade_records,
        columns=["datetime", "action", "price", "fee", "btc", "cash_after"],
    )
    decisions_df = pd.DataFrame(decision_records)

    return equity_df, trades_df, decisions_df, total_reward


def split_train_eval(feature_df):
    split_idx = int(len(feature_df) * TRAIN_RATIO)
    train_df = feature_df.iloc[:split_idx].reset_index(drop=True)
    eval_df = feature_df.iloc[split_idx - 1 :].reset_index(drop=True)
    return train_df, eval_df


def save_rl_results(eval_df, trades_df, round_trips_df, decisions_df, metrics, trade_stats, training_summary, agent):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    metrics_payload = {
        "strategy_name": STRATEGY_NAME,
        "model_name": MODEL_NAME,
        "symbol": SYMBOL,
        "start_date": str(eval_df["datetime"].min()),
        "end_date": str(eval_df["datetime"].max()),
        "data_frequency": "1d",
        "state_features": STATE_FEATURE_NAMES,
        "reward_definition": "next-day portfolio return after next-open execution, scaled by 100",
        "train_start_date": training_summary["train_start_date"],
        "train_end_date": training_summary["train_end_date"],
        "train_rows": training_summary["train_rows"],
        "episodes": training_summary["episodes"],
        "learned_states": training_summary["learned_states"],
        "epsilon_final": training_summary["epsilon_final"],
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

    with open(RESULTS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2, ensure_ascii=False)

    trades_df.to_csv(RESULTS_DIR / "trades.csv", index=False)
    round_trips_df.to_csv(RESULTS_DIR / "round_trips.csv", index=False)
    eval_df[["datetime", "equity", "equity_curve", "market_curve", "position", "close"]].to_csv(
        RESULTS_DIR / "equity_curve.csv",
        index=False,
    )
    decisions_df.to_csv(RESULTS_DIR / "decision_log.csv", index=False)

    with open(RESULTS_DIR / "training_summary.json", "w", encoding="utf-8") as f:
        json.dump(training_summary, f, indent=2, ensure_ascii=False)

    with open(RESULTS_DIR / "model_snapshot.json", "w", encoding="utf-8") as f:
        json.dump({"model_name": MODEL_NAME, "top_states": agent.export_q_table()}, f, indent=2, ensure_ascii=False)

    summary_lines = [
        f"Strategy: {STRATEGY_NAME}",
        f"Model: {MODEL_NAME}",
        f"Symbol: {SYMBOL}",
        f"Evaluation Range: {eval_df['datetime'].min()} to {eval_df['datetime'].max()}",
        f"Episodes: {training_summary['episodes']}",
        f"Learned States: {training_summary['learned_states']}",
        f"Total Return: {metrics['total_return']:.2%}",
        f"Annual Return: {metrics['annual_return']:.2%}",
        f"Volatility: {metrics['volatility']:.2%}",
        f"Sharpe Ratio: {metrics['sharpe']:.2f}",
        f"Max Drawdown: {metrics['max_drawdown']:.2%}",
        f"Win Rate: {trade_stats['win_rate']:.2%}",
        f"Profit/Loss Ratio: {trade_stats['profit_loss_ratio']:.2f}",
        f"Total Trades: {trade_stats['total_trades']}",
    ]
    (RESULTS_DIR / "summary.txt").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")


raw_df = load_processed_data(DATA_FILE)
feature_df = add_rl_features(raw_df)
train_df, eval_df = split_train_eval(feature_df)

agent = QLearningAgent(
    alpha=0.12,
    gamma=0.95,
    epsilon_start=1.0,
    epsilon_end=0.05,
    epsilon_decay=0.97,
    seed=RANDOM_SEED,
)

episode_rewards = []
for _ in range(EPISODES):
    _, _, _, episode_reward = run_episode(train_df, agent, training=True)
    episode_rewards.append(episode_reward)
    agent.decay_epsilon()

eval_result_df, trades_df, decisions_df, eval_reward = run_episode(eval_df, agent, training=False)
round_trips_df = build_round_trips(trades_df)
metrics = calculate_metrics(eval_result_df)
trade_stats = calculate_trade_stats(round_trips_df)

training_summary = {
    "model_name": MODEL_NAME,
    "episodes": EPISODES,
    "alpha": 0.12,
    "gamma": 0.95,
    "epsilon_start": 1.0,
    "epsilon_end": 0.05,
    "epsilon_final": agent.epsilon,
    "learned_states": agent.learned_states(),
    "avg_episode_reward_last_10": float(pd.Series(episode_rewards).tail(10).mean()),
    "train_rows": int(len(train_df)),
    "eval_rows": int(len(eval_df)),
    "train_start_date": str(train_df["datetime"].min()),
    "train_end_date": str(train_df["datetime"].max()),
    "eval_start_date": str(eval_df["datetime"].min()),
    "eval_end_date": str(eval_df["datetime"].max()),
    "live_data_interface": "engine.market_data.fetch_binance_klines",
}

save_rl_results(eval_result_df, trades_df, round_trips_df, decisions_df, metrics, trade_stats, training_summary, agent)
generate_report(results_dir=RESULTS_DIR, report_file=REPORT_FILE)

chosen_counts = decisions_df["chosen_action_name"].value_counts()
executed_counts = decisions_df["executed_action_name"].value_counts()

print("=== RL 训练摘要 ===")
print("训练轮数：", EPISODES)
print("训练区间：", training_summary["train_start_date"], "->", training_summary["train_end_date"])
print("评估区间：", training_summary["eval_start_date"], "->", training_summary["eval_end_date"])
print("最终 epsilon：", f"{agent.epsilon:.4f}")
print("学习到的状态数：", agent.learned_states())
print("最近 10 轮平均奖励：", f"{training_summary['avg_episode_reward_last_10']:.4f}")
print()

print("=== 智能体动作分布 ===")
print("选择动作：")
print(chosen_counts)
print()
print("实际执行动作：")
print(executed_counts)
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
    print("暂无完整买卖配对")
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

print("\n=== 文件输出 ===")
print("结果目录：", RESULTS_DIR)
print("报告文件：", REPORT_FILE)
