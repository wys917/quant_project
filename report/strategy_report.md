# Strategy Report

## 1. Strategy Overview
- 策略名称: ma_crossover_v3
- 交易标的: BTCUSDT
- 回测时间区间: 2020-01-01 00:00:00 to 2026-02-28 00:00:00
- 数据频率: 1d

## 2. Performance Summary
- Total Return: 496.48%
- Annual Return: 33.60%
- Volatility: 41.84%
- Sharpe Ratio: 0.90
- Max Drawdown: -63.10%

## 3. Trade Statistics
- Total Trades: 64
- Win Rate: 31.25%
- Average Win: 24.72%
- Average Loss: -5.22%
- Profit/Loss Ratio: 4.73

## 4. Risk Analysis
最大回撤为 -63.10%，说明策略在最差阶段会经历较明显的净值回落。 年化波动率为 41.84%，反映净值波动不低，需要结合收益一起判断风险回报。 从风险特征看，这是一类对趋势延续较敏感、对回撤容忍度要求较高的策略。

## 5. Trade Behavior Analysis
- 平均持仓天数: 18.83
- 单笔收益分布特征: 单笔收益均值为正但中位数一般，说明收益可能依赖少数较大的盈利交易。
- 最赚钱的几笔交易:
- 2020-10-09 -> 2020-12-12, buy 10925.44, sell 18036.53, pnl 64.89%
- 2020-12-15 -> 2021-01-22, buy 19273.69, sell 30851.99, pnl 59.87%
- 2023-10-18 -> 2023-12-31, buy 28395.91, sell 42140.29, pnl 48.20%
- 最亏钱的几笔交易:
- 2022-10-26 -> 2022-11-10, buy 20079.02, sell 15922.68, pnl -20.90%
- 2022-03-03 -> 2022-03-08, buy 43892.99, sell 37988.01, pnl -13.65%
- 2021-05-04 -> 2021-05-14, buy 57169.39, sell 49671.92, pnl -13.31%

## 6. Strengths and Weaknesses
### Strengths
- 策略在当前样本区间内取得了较高的累计收益。
- 单笔盈利相对单笔亏损更有优势。

### Weaknesses
- 最大回撤较大，策略在趋势反转或震荡阶段承压明显。
- Sharpe Ratio 一般，收益的稳定性还有提升空间。
- 胜率不足一半，信号过滤可能仍不够。

## 7. Next Step Suggestions
- 测试不同均线参数组合，观察收益与回撤变化。
- 加入止损、止盈或移动止损，改善回撤表现。
- 增加市场状态识别，区分趋势市与震荡市。
- 扩展为多策略对比框架，支持统一实验记录。
- 与未来的 LLM 总结模块结合，生成更自然的研究报告。

---

## Prompt Template Preview
This project also prepares a future LLM input template for research summarization.

```text
You are a quantitative research assistant.

Please write a clean strategy research summary based on the following inputs:

Strategy Name:
ma_crossover_v3

Symbol:
BTCUSDT

Metrics Summary:
Total Return=496.48%, Annual Return=33.60%, Volatility=41.84%, Sharpe=0.90, Max Drawdown=-63.10%

Trade Stats Summary:
Total Trades=64, Win Rate=31.25%, Average Win=24.72%, Average Loss=-5.22%, Profit/Loss Ratio=4.73

Strengths:
策略在当前样本区间内取得了较高的累计收益。; 单笔盈利相对单笔亏损更有优势。

Weaknesses:
最大回撤较大，策略在趋势反转或震荡阶段承压明显。; Sharpe Ratio 一般，收益的稳定性还有提升空间。; 胜率不足一半，信号过滤可能仍不够。

Next-Step Suggestions:
测试不同均线参数组合，观察收益与回撤变化。; 加入止损、止盈或移动止损，改善回撤表现。; 增加市场状态识别，区分趋势市与震荡市。; 扩展为多策略对比框架，支持统一实验记录。; 与未来的 LLM 总结模块结合，生成更自然的研究报告。

Write the summary in a structured and concise format that is suitable for a research log.
```
