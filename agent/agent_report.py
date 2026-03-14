import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from agent.prompt_templates import REPORT_SUMMARY_PROMPT

DEFAULT_RESULTS_DIR = ROOT_DIR / "data/processed/results"
DEFAULT_REPORT_FILE = ROOT_DIR / "report/strategy_report.md"


def fmt_pct(value):
    return f"{value:.2%}"


def fmt_num(value):
    return f"{value:.2f}"


def load_optional_json(file_path):
    file_path = Path(file_path)
    if file_path.exists():
        return json.loads(file_path.read_text(encoding="utf-8"))
    return {}


def load_optional_csv(file_path):
    file_path = Path(file_path)
    if file_path.exists():
        return pd.read_csv(file_path)
    return pd.DataFrame()


def build_strengths(metrics, trade_stats):
    strengths = []
    if metrics.get("total_return", 0) > 0.3:
        strengths.append("策略在当前样本区间内实现了正向累计收益。")
    if metrics.get("sharpe", 0) > 1:
        strengths.append("风险调整后收益表现相对稳健。")
    if trade_stats.get("profit_loss_ratio", 0) > 1.2:
        strengths.append("盈利交易相对亏损交易更有优势。")
    if trade_stats.get("win_rate", 0) >= 0.5:
        strengths.append("胜率具备一定基础，说明决策信号并非完全随机。")
    if metrics.get("model_name"):
        strengths.append("系统已经具备从结构化结果生成研究报告的自动化链路。")
    if not strengths:
        strengths.append("当前系统链路完整，适合作为后续实验底盘继续迭代。")
    return strengths


def build_weaknesses(metrics, trade_stats):
    weaknesses = []
    if metrics.get("max_drawdown", 0) < -0.3:
        weaknesses.append("最大回撤较大，策略在压力阶段的稳定性仍然不足。")
    if metrics.get("sharpe", 0) < 1:
        weaknesses.append("Sharpe Ratio 一般，说明收益稳定性还有提升空间。")
    if trade_stats.get("win_rate", 0) < 0.5:
        weaknesses.append("胜率不高，当前状态定义和奖励函数还可以继续优化。")
    if trade_stats.get("profit_loss_ratio", 0) < 1:
        weaknesses.append("盈亏比偏弱，说明卖出和止损节奏可能还不够好。")
    if not weaknesses:
        weaknesses.append("当前系统仍是原型版本，尚未覆盖更复杂的市场状态与风险控制。")
    return weaknesses


def build_next_steps(metrics):
    model_name = metrics.get("model_name", "agent")
    return [
        f"继续迭代 {model_name} 的状态空间、奖励函数和训练轮数。",
        "增加更多风险控制约束，例如止损、冷却期和仓位限制。",
        "把训练集/测试集拆分做得更严格，减少样本内偏差。",
        "接入实时数据接口，先做纸面交易，再考虑更进一步的自动化执行。",
        "结合 LLM 或研究助手模块，对训练结果和失败案例做更自然的复盘总结。",
    ]


def build_risk_comment(metrics):
    parts = [
        f"最大回撤为 {fmt_pct(metrics.get('max_drawdown', 0))}，说明策略在最差阶段会经历明显净值回落。",
        f"年化波动率为 {fmt_pct(metrics.get('volatility', 0))}，需要结合收益与回撤一起判断策略质量。",
    ]

    if metrics.get("max_drawdown", 0) < -0.4:
        parts.append("从风险特征看，这个系统仍然偏实验型，回撤控制是后续重点。")
    else:
        parts.append("从风险特征看，系统已经具备继续研究和迭代的基础。")

    return " ".join(parts)


def trade_behavior_analysis(round_trips_df):
    if len(round_trips_df) == 0:
        return {
            "top_wins": [],
            "top_losses": [],
            "distribution_text": "当前没有完整买卖配对，暂时无法分析交易行为。",
            "avg_holding_days": 0.0,
        }

    sorted_wins = round_trips_df.sort_values("pnl_pct", ascending=False).head(3)
    sorted_losses = round_trips_df.sort_values("pnl_pct", ascending=True).head(3)
    avg_holding_days = float(round_trips_df["holding_days"].mean()) if "holding_days" in round_trips_df.columns else 0.0

    median_pnl = float(round_trips_df["pnl_pct"].median())
    mean_pnl = float(round_trips_df["pnl_pct"].mean())

    if mean_pnl > 0 and median_pnl > 0:
        distribution_text = "单笔收益分布整体偏正，说明盈利并非完全依赖极少数大赚单。"
    elif mean_pnl > 0 and median_pnl <= 0:
        distribution_text = "单笔收益均值为正但中位数一般，说明结果可能依赖少数较大的盈利交易。"
    else:
        distribution_text = "单笔收益分布偏弱，说明当前决策规则还有明显优化空间。"

    return {
        "top_wins": sorted_wins.to_dict("records"),
        "top_losses": sorted_losses.to_dict("records"),
        "distribution_text": distribution_text,
        "avg_holding_days": avg_holding_days,
    }


def decision_behavior_analysis(decision_log_df, training_summary):
    if len(decision_log_df) == 0:
        return [
            "当前没有 decision log，暂时无法分析智能体决策过程。",
        ]

    lines = []
    chosen_counts = decision_log_df["chosen_action_name"].value_counts()
    executed_counts = decision_log_df["executed_action_name"].value_counts()

    chosen_summary = ", ".join(f"{action}={count}" for action, count in chosen_counts.items())
    executed_summary = ", ".join(f"{action}={count}" for action, count in executed_counts.items())

    lines.append(f"智能体选择动作分布：{chosen_summary}。")
    lines.append(f"实际执行动作分布：{executed_summary}。")

    reward_by_action = decision_log_df.groupby("executed_action_name")["reward"].mean().sort_index()
    if len(reward_by_action) > 0:
        reward_summary = ", ".join(f"{action}={value:.4f}" for action, value in reward_by_action.items())
        lines.append(f"不同执行动作的平均单步奖励：{reward_summary}。")

    buy_rows = decision_log_df[decision_log_df["chosen_action_name"] == "BUY"]
    sell_rows = decision_log_df[decision_log_df["chosen_action_name"] == "SELL"]

    if len(buy_rows) > 0:
        lines.append(
            "BUY 决策出现时，平均 ma_gap={:.4f}，平均 RSI={:.2f}。".format(
                buy_rows["ma_gap"].mean(),
                buy_rows["rsi14"].mean(),
            )
        )
    if len(sell_rows) > 0:
        lines.append(
            "SELL 决策出现时，平均 ma_gap={:.4f}，平均 RSI={:.2f}。".format(
                sell_rows["ma_gap"].mean(),
                sell_rows["rsi14"].mean(),
            )
        )

    if training_summary:
        lines.append(
            "训练共运行 {episodes} 轮，最终 epsilon={epsilon_final:.4f}，学习到 {learned_states} 个状态。".format(
                episodes=training_summary.get("episodes", 0),
                epsilon_final=training_summary.get("epsilon_final", 0.0),
                learned_states=training_summary.get("learned_states", 0),
            )
        )

    return lines


def record_lines(records):
    lines = []
    for record in records:
        lines.append(
            f"- {record['buy_date']} -> {record['sell_date']}, "
            f"buy {record['buy_price']:.2f}, sell {record['sell_price']:.2f}, pnl {record['pnl_pct']:.2%}"
        )
    return "\n".join(lines) if lines else "- 暂无数据"


def generate_report(results_dir=DEFAULT_RESULTS_DIR, report_file=DEFAULT_REPORT_FILE):
    results_dir = Path(results_dir)
    report_file = Path(report_file)

    with open(results_dir / "metrics.json", "r", encoding="utf-8") as f:
        metrics = json.load(f)

    trades_df = pd.read_csv(results_dir / "trades.csv")
    round_trips_df = pd.read_csv(results_dir / "round_trips.csv")
    equity_curve_df = pd.read_csv(results_dir / "equity_curve.csv")
    training_summary = load_optional_json(results_dir / "training_summary.json")
    decision_log_df = load_optional_csv(results_dir / "decision_log.csv")

    report_file.parent.mkdir(parents=True, exist_ok=True)

    trade_stats = {
        "win_rate": metrics.get("win_rate", 0.0),
        "avg_win": metrics.get("avg_win", 0.0),
        "avg_loss": metrics.get("avg_loss", 0.0),
        "profit_loss_ratio": metrics.get("profit_loss_ratio", 0.0),
        "total_trades": metrics.get("total_trades", 0),
    }

    strengths = build_strengths(metrics, trade_stats)
    weaknesses = build_weaknesses(metrics, trade_stats)
    next_steps = build_next_steps(metrics)
    behavior = trade_behavior_analysis(round_trips_df)
    decision_lines = decision_behavior_analysis(decision_log_df, training_summary)

    metrics_summary = (
        f"Total Return={fmt_pct(metrics.get('total_return', 0))}, "
        f"Annual Return={fmt_pct(metrics.get('annual_return', 0))}, "
        f"Volatility={fmt_pct(metrics.get('volatility', 0))}, "
        f"Sharpe={fmt_num(metrics.get('sharpe', 0))}, "
        f"Max Drawdown={fmt_pct(metrics.get('max_drawdown', 0))}"
    )
    trade_stats_summary = (
        f"Total Trades={trade_stats['total_trades']}, "
        f"Win Rate={fmt_pct(trade_stats['win_rate'])}, "
        f"Average Win={fmt_pct(trade_stats['avg_win'])}, "
        f"Average Loss={fmt_pct(trade_stats['avg_loss'])}, "
        f"Profit/Loss Ratio={fmt_num(trade_stats['profit_loss_ratio'])}"
    )
    decision_summary = " ".join(decision_lines)

    model_lines = []
    if metrics.get("model_name"):
        model_lines.append(f"- 模型: {metrics['model_name']}")
    if training_summary.get("episodes"):
        model_lines.append(f"- 训练轮数: {training_summary['episodes']}")
    if training_summary.get("learned_states"):
        model_lines.append(f"- 学到的状态数: {training_summary['learned_states']}")

    report = f"""# Strategy Report

## 1. Strategy Overview
- 策略名称: {metrics.get('strategy_name', 'unknown_strategy')}
- 交易标的: {metrics.get('symbol', 'unknown_symbol')}
- 回测时间区间: {metrics.get('start_date', 'N/A')} to {metrics.get('end_date', 'N/A')}
- 数据频率: {metrics.get('data_frequency', 'N/A')}
{chr(10).join(model_lines) if model_lines else ""}

## 2. Performance Summary
- Total Return: {fmt_pct(metrics.get('total_return', 0))}
- Annual Return: {fmt_pct(metrics.get('annual_return', 0))}
- Volatility: {fmt_pct(metrics.get('volatility', 0))}
- Sharpe Ratio: {fmt_num(metrics.get('sharpe', 0))}
- Max Drawdown: {fmt_pct(metrics.get('max_drawdown', 0))}

## 3. Trade Statistics
- Total Trades: {trade_stats['total_trades']}
- Win Rate: {fmt_pct(trade_stats['win_rate'])}
- Average Win: {fmt_pct(trade_stats['avg_win'])}
- Average Loss: {fmt_pct(trade_stats['avg_loss'])}
- Profit/Loss Ratio: {fmt_num(trade_stats['profit_loss_ratio'])}

## 4. Risk Analysis
{build_risk_comment(metrics)}

## 5. Trade Behavior Analysis
- 平均持仓天数: {behavior['avg_holding_days']:.2f}
- 单笔收益分布特征: {behavior['distribution_text']}
- 最赚钱的几笔交易:
{record_lines(behavior['top_wins'])}
- 最亏钱的几笔交易:
{record_lines(behavior['top_losses'])}

## 6. Agent Decision Analysis
{chr(10).join(f"- {line}" for line in decision_lines)}

## 7. Strengths and Weaknesses
### Strengths
{chr(10).join(f"- {item}" for item in strengths)}

### Weaknesses
{chr(10).join(f"- {item}" for item in weaknesses)}

## 8. Next Step Suggestions
{chr(10).join(f"- {item}" for item in next_steps)}

---

## Prompt Template Preview
```text
{REPORT_SUMMARY_PROMPT.format(
    strategy_name=metrics.get('strategy_name', 'unknown_strategy'),
    symbol=metrics.get('symbol', 'unknown_symbol'),
    metrics_summary=metrics_summary,
    trade_stats_summary=trade_stats_summary,
    decision_summary=decision_summary,
    strengths='; '.join(strengths),
    weaknesses='; '.join(weaknesses),
    next_step_suggestions='; '.join(next_steps),
)}
```
"""

    report_file.write_text(report, encoding="utf-8")

    print("Strategy report saved to:", report_file)
    print("Metrics source:", results_dir / "metrics.json")
    print("Trades rows:", len(trades_df))
    print("Round trips rows:", len(round_trips_df))
    print("Equity curve rows:", len(equity_curve_df))
    print("Decision log rows:", len(decision_log_df))


def main():
    parser = argparse.ArgumentParser(description="Generate a Markdown strategy report from structured result files.")
    parser.add_argument("--results-dir", default=str(DEFAULT_RESULTS_DIR))
    parser.add_argument("--report-file", default=str(DEFAULT_REPORT_FILE))
    args = parser.parse_args()
    generate_report(results_dir=args.results_dir, report_file=args.report_file)


if __name__ == "__main__":
    main()
