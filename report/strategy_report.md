# Strategy Report

## 1. Strategy Overview
- 策略名称: rl_q_learning_v1
- 交易标的: BTCUSDT
- 回测时间区间: 2024-04-29 00:00:00 to 2026-02-28 00:00:00
- 数据频率: 1d
- 模型: tabular_q_learning
- 训练轮数: 80
- 学到的状态数: 275

## 2. Performance Summary
- Total Return: -26.47%
- Annual Return: -15.42%
- Volatility: 21.27%
- Sharpe Ratio: -0.68
- Max Drawdown: -32.33%

## 3. Trade Statistics
- Total Trades: 91
- Win Rate: 50.55%
- Average Win: 1.83%
- Average Loss: -2.44%
- Profit/Loss Ratio: 0.75

## 4. Risk Analysis
最大回撤为 -32.33%，说明策略在最差阶段会经历明显净值回落。 年化波动率为 21.27%，需要结合收益与回撤一起判断策略质量。 从风险特征看，系统已经具备继续研究和迭代的基础。

## 5. Trade Behavior Analysis
- 平均持仓天数: 1.63
- 单笔收益分布特征: 单笔收益分布偏弱，说明当前决策规则还有明显优化空间。
- 最赚钱的几笔交易:
- 2025-04-22 -> 2025-04-23, buy 87516.22, sell 93442.99, pnl 6.57%
- 2025-06-07 -> 2025-06-10, buy 104288.43, sell 110263.02, pnl 5.53%
- 2024-11-09 -> 2024-11-11, buy 76509.78, sell 80370.01, pnl 4.85%
- 最亏钱的几笔交易:
- 2024-09-28 -> 2024-10-03, buy 65769.95, sell 60649.27, pnl -7.99%
- 2024-04-30 -> 2024-05-03, buy 63866.00, sell 59060.60, pnl -7.72%
- 2026-01-31 -> 2026-02-01, buy 84260.50, sell 78741.10, pnl -6.75%

## 6. Agent Decision Analysis
- 智能体选择动作分布：HOLD=336, SELL=214, BUY=120。
- 实际执行动作分布：HOLD=487, BUY=92, SELL=91。
- 不同执行动作的平均单步奖励：BUY=0.0092, HOLD=-0.0532, SELL=-0.1000。
- BUY 决策出现时，平均 ma_gap=-0.0006，平均 RSI=51.02。
- SELL 决策出现时，平均 ma_gap=-0.0004，平均 RSI=51.29。
- 训练共运行 80 轮，最终 epsilon=0.0874，学习到 275 个状态。

## 7. Strengths and Weaknesses
### Strengths
- 胜率具备一定基础，说明决策信号并非完全随机。
- 系统已经具备从结构化结果生成研究报告的自动化链路。

### Weaknesses
- 最大回撤较大，策略在压力阶段的稳定性仍然不足。
- Sharpe Ratio 一般，说明收益稳定性还有提升空间。
- 盈亏比偏弱，说明卖出和止损节奏可能还不够好。

## 8. Next Step Suggestions
- 继续迭代 tabular_q_learning 的状态空间、奖励函数和训练轮数。
- 增加更多风险控制约束，例如止损、冷却期和仓位限制。
- 把训练集/测试集拆分做得更严格，减少样本内偏差。
- 接入实时数据接口，先做纸面交易，再考虑更进一步的自动化执行。
- 结合 LLM 或研究助手模块，对训练结果和失败案例做更自然的复盘总结。

---

## Prompt Template Preview
```text
You are a quantitative research assistant.

Please write a clean strategy research summary based on the following inputs:

Strategy Name:
rl_q_learning_v1

Symbol:
BTCUSDT

Metrics Summary:
Total Return=-26.47%, Annual Return=-15.42%, Volatility=21.27%, Sharpe=-0.68, Max Drawdown=-32.33%

Trade Stats Summary:
Total Trades=91, Win Rate=50.55%, Average Win=1.83%, Average Loss=-2.44%, Profit/Loss Ratio=0.75

Decision Summary:
智能体选择动作分布：HOLD=336, SELL=214, BUY=120。 实际执行动作分布：HOLD=487, BUY=92, SELL=91。 不同执行动作的平均单步奖励：BUY=0.0092, HOLD=-0.0532, SELL=-0.1000。 BUY 决策出现时，平均 ma_gap=-0.0006，平均 RSI=51.02。 SELL 决策出现时，平均 ma_gap=-0.0004，平均 RSI=51.29。 训练共运行 80 轮，最终 epsilon=0.0874，学习到 275 个状态。

Strengths:
胜率具备一定基础，说明决策信号并非完全随机。; 系统已经具备从结构化结果生成研究报告的自动化链路。

Weaknesses:
最大回撤较大，策略在压力阶段的稳定性仍然不足。; Sharpe Ratio 一般，说明收益稳定性还有提升空间。; 盈亏比偏弱，说明卖出和止损节奏可能还不够好。

Next-Step Suggestions:
继续迭代 tabular_q_learning 的状态空间、奖励函数和训练轮数。; 增加更多风险控制约束，例如止损、冷却期和仓位限制。; 把训练集/测试集拆分做得更严格，减少样本内偏差。; 接入实时数据接口，先做纸面交易，再考虑更进一步的自动化执行。; 结合 LLM 或研究助手模块，对训练结果和失败案例做更自然的复盘总结。

Write the summary in a structured and concise format that is suitable for a research log.
```
