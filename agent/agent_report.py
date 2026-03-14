import json
import sys
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from agent.prompt_templates import REPORT_SUMMARY_PROMPT

RESULTS_DIR = ROOT_DIR / "data/processed/results"
REPORT_DIR = ROOT_DIR / "report"
REPORT_FILE = REPORT_DIR / "strategy_report.md"


def fmt_pct(value):
    return f"{value:.2%}"


def fmt_num(value):
    return f"{value:.2f}"


def build_strengths(metrics, trade_stats):
    strengths = []
    if metrics["total_return"] > 0.5:
        strengths.append("策略在当前样本区间内取得了较高的累计收益。")
    if metrics["sharpe"] > 1:
        strengths.append("策略的风险调整后收益表现较稳健。")
    if trade_stats["win_rate"] >= 0.5:
        strengths.append("盈利交易占比不低，交易命中率具备一定基础。")
    if trade_stats["profit_loss_ratio"] > 1.2:
        strengths.append("单笔盈利相对单笔亏损更有优势。")
    if not strengths:
        strengths.append("策略逻辑简单直接，适合作为研究底盘继续扩展。")
    return strengths


def build_weaknesses(metrics, trade_stats):
    weaknesses = []
    if metrics["max_drawdown"] < -0.3:
        weaknesses.append("最大回撤较大，策略在趋势反转或震荡阶段承压明显。")
    if metrics["sharpe"] < 1:
        weaknesses.append("Sharpe Ratio 一般，收益的稳定性还有提升空间。")
    if trade_stats["win_rate"] < 0.5:
        weaknesses.append("胜率不足一半，信号过滤可能仍不够。")
    if trade_stats["profit_loss_ratio"] < 1:
        weaknesses.append("盈亏比偏弱，说明盈利交易的优势不够明显。")
    if not weaknesses:
        weaknesses.append("当前规则较基础，仍缺少更细的市场状态与风控控制。")
    return weaknesses


def build_next_steps():
    return [
        "测试不同均线参数组合，观察收益与回撤变化。",
        "加入止损、止盈或移动止损，改善回撤表现。",
        "增加市场状态识别，区分趋势市与震荡市。",
        "扩展为多策略对比框架，支持统一实验记录。",
        "与未来的 LLM 总结模块结合，生成更自然的研究报告。",
    ]


def build_risk_comment(metrics):
    parts = [
        f"最大回撤为 {fmt_pct(metrics['max_drawdown'])}，说明策略在最差阶段会经历较明显的净值回落。",
        f"年化波动率为 {fmt_pct(metrics['volatility'])}，反映净值波动不低，需要结合收益一起判断风险回报。",
    ]

    if metrics["max_drawdown"] < -0.4:
        parts.append("从风险特征看，这是一类对趋势延续较敏感、对回撤容忍度要求较高的策略。")
    else:
        parts.append("从风险特征看，策略仍有波动，但整体属于可继续研究和迭代的基础模型。")

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
        distribution_text = "单笔收益分布整体偏正，说明大多数交易并非完全依赖极少数大赚单。"
    elif mean_pnl > 0 and median_pnl <= 0:
        distribution_text = "单笔收益均值为正但中位数一般，说明收益可能依赖少数较大的盈利交易。"
    else:
        distribution_text = "单笔收益分布偏弱，说明当前规则在交易层面还有明显优化空间。"

    return {
        "top_wins": sorted_wins.to_dict("records"),
        "top_losses": sorted_losses.to_dict("records"),
        "distribution_text": distribution_text,
        "avg_holding_days": avg_holding_days,
    }


def record_lines(records):
    lines = []
    for record in records:
        lines.append(
            f"- {record['buy_date']} -> {record['sell_date']}, "
            f"buy {record['buy_price']:.2f}, sell {record['sell_price']:.2f}, pnl {record['pnl_pct']:.2%}"
        )
    return "\n".join(lines) if lines else "- 暂无数据"


with open(RESULTS_DIR / "metrics.json", "r", encoding="utf-8") as f:
    metrics = json.load(f)

trades_df = pd.read_csv(RESULTS_DIR / "trades.csv")
round_trips_df = pd.read_csv(RESULTS_DIR / "round_trips.csv")
equity_curve_df = pd.read_csv(RESULTS_DIR / "equity_curve.csv")

REPORT_DIR.mkdir(parents=True, exist_ok=True)

trade_stats = {
    "win_rate": metrics["win_rate"],
    "avg_win": metrics["avg_win"],
    "avg_loss": metrics["avg_loss"],
    "profit_loss_ratio": metrics["profit_loss_ratio"],
    "total_trades": metrics["total_trades"],
}

strengths = build_strengths(metrics, trade_stats)
weaknesses = build_weaknesses(metrics, trade_stats)
next_steps = build_next_steps()
behavior = trade_behavior_analysis(round_trips_df)

metrics_summary = (
    f"Total Return={fmt_pct(metrics['total_return'])}, "
    f"Annual Return={fmt_pct(metrics['annual_return'])}, "
    f"Volatility={fmt_pct(metrics['volatility'])}, "
    f"Sharpe={fmt_num(metrics['sharpe'])}, "
    f"Max Drawdown={fmt_pct(metrics['max_drawdown'])}"
)
trade_stats_summary = (
    f"Total Trades={metrics['total_trades']}, "
    f"Win Rate={fmt_pct(metrics['win_rate'])}, "
    f"Average Win={fmt_pct(metrics['avg_win'])}, "
    f"Average Loss={fmt_pct(metrics['avg_loss'])}, "
    f"Profit/Loss Ratio={fmt_num(metrics['profit_loss_ratio'])}"
)

report = f"""# Strategy Report

## 1. Strategy Overview
- 策略名称: {metrics['strategy_name']}
- 交易标的: {metrics['symbol']}
- 回测时间区间: {metrics['start_date']} to {metrics['end_date']}
- 数据频率: 1d

## 2. Performance Summary
- Total Return: {fmt_pct(metrics['total_return'])}
- Annual Return: {fmt_pct(metrics['annual_return'])}
- Volatility: {fmt_pct(metrics['volatility'])}
- Sharpe Ratio: {fmt_num(metrics['sharpe'])}
- Max Drawdown: {fmt_pct(metrics['max_drawdown'])}

## 3. Trade Statistics
- Total Trades: {metrics['total_trades']}
- Win Rate: {fmt_pct(metrics['win_rate'])}
- Average Win: {fmt_pct(metrics['avg_win'])}
- Average Loss: {fmt_pct(metrics['avg_loss'])}
- Profit/Loss Ratio: {fmt_num(metrics['profit_loss_ratio'])}

## 4. Risk Analysis
{build_risk_comment(metrics)}

## 5. Trade Behavior Analysis
- 平均持仓天数: {behavior['avg_holding_days']:.2f}
- 单笔收益分布特征: {behavior['distribution_text']}
- 最赚钱的几笔交易:
{record_lines(behavior['top_wins'])}
- 最亏钱的几笔交易:
{record_lines(behavior['top_losses'])}

## 6. Strengths and Weaknesses
### Strengths
{chr(10).join(f"- {item}" for item in strengths)}

### Weaknesses
{chr(10).join(f"- {item}" for item in weaknesses)}

## 7. Next Step Suggestions
{chr(10).join(f"- {item}" for item in next_steps)}

---

## Prompt Template Preview
This project also prepares a future LLM input template for research summarization.

```text
{REPORT_SUMMARY_PROMPT.format(
    strategy_name=metrics['strategy_name'],
    symbol=metrics['symbol'],
    metrics_summary=metrics_summary,
    trade_stats_summary=trade_stats_summary,
    strengths='; '.join(strengths),
    weaknesses='; '.join(weaknesses),
    next_step_suggestions='; '.join(next_steps),
)}
```
"""

REPORT_FILE.write_text(report, encoding="utf-8")

print("Strategy report saved to:", REPORT_FILE)
print("Metrics source:", RESULTS_DIR / "metrics.json")
print("Trades rows:", len(trades_df))
print("Round trips rows:", len(round_trips_df))
print("Equity curve rows:", len(equity_curve_df))
