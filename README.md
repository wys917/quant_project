# quant_project

一个面向初学者的量化研究练手项目，目标是逐步搭建一个“传统量化底盘 + 智能体研究助手”的系统原型。

## 项目定位

- 先把基础研究链路跑通，再逐步接入更智能的研究助手能力
- 当前重点是把 RL 智能体、回测系统、结构化结果和自动报告连起来
- 项目适合学习 pandas、简单回测逻辑、基础强化学习和 Agent 输入输出链路设计

## 当前实现

- BTCUSDT 日线历史数据
- 双均线策略回测
- Tabular Q-Learning 强化学习交易原型
- 当天观察状态、次日开盘执行的回测逻辑
- 回测指标输出
- 交易统计输出
- 自动导出结构化结果
- 自动生成 Markdown 策略报告
- 预留 Binance API 实时数据接口

## 当前阶段

- 单标的：BTCUSDT
- 数据频率：1d
- 策略类型：
  - 双均线策略（MA5 / MA20）
  - RL 原型策略（Q-Learning, long-only）
- 系统形态：最小可用回测系统 + 规则驱动研究报告 + RL 决策原型

## 目录结构

```text
quant_project/
├── data/
│   ├── raw/
│   └── processed/
│       ├── BTCUSDT_1d_full.csv
│       ├── results/
│       └── results_rl/
├── engine/
│   ├── __init__.py
│   ├── market_data.py
│   └── metrics.py
├── rl/
│   ├── __init__.py
│   ├── features.py
│   └── q_learning_agent.py
├── notebooks/
│   ├── merge_monthly_data.py
│   ├── check_data.py
│   ├── ma_strategy.py
│   ├── backtest_ma_v3.py
│   └── backtest_rl_agent.py
├── agent/
│   ├── __init__.py
│   ├── agent_report.py
│   └── prompt_templates.py
├── report/
│   └── strategy_report.md
└── README.md
```

## 如何准备数据

1. 下载 Binance 的 BTCUSDT 日线月度 CSV 数据到 `data/raw/monthly/`
2. 运行 `python notebooks/merge_monthly_data.py`
3. 生成标准研究数据文件 `data/processed/BTCUSDT_1d_full.csv`
4. 如需检查数据，再运行 `python notebooks/check_data.py`

说明：

- `data/raw/` 主要放原始月度数据，通常不建议上传到远程仓库
- 当前研究主数据文件是 `data/processed/BTCUSDT_1d_full.csv`
- `engine/market_data.py` 里预留了 `fetch_binance_klines()`，方便后续接入实时行情

## 运行顺序

```bash
python notebooks/merge_monthly_data.py
python notebooks/check_data.py
python notebooks/ma_strategy.py
python notebooks/backtest_ma_v3.py
python notebooks/backtest_rl_agent.py
python agent/agent_report.py --results-dir data/processed/results_rl --report-file report/strategy_report.md
```

## 输出结果

运行 `python notebooks/backtest_ma_v3.py` 后，会自动生成：

- `data/processed/results/metrics.json`
- `data/processed/results/trades.csv`
- `data/processed/results/round_trips.csv`
- `data/processed/results/equity_curve.csv`
- `data/processed/results/summary.txt`

运行 `python notebooks/backtest_rl_agent.py` 后，会自动生成：

- `data/processed/results_rl/metrics.json`
- `data/processed/results_rl/trades.csv`
- `data/processed/results_rl/round_trips.csv`
- `data/processed/results_rl/equity_curve.csv`
- `data/processed/results_rl/decision_log.csv`
- `data/processed/results_rl/training_summary.json`
- `data/processed/results_rl/model_snapshot.json`
- `data/processed/results_rl/summary.txt`
- `report/strategy_report.md`

## 当前限制

- 仅单标的
- 仅 long-only 持仓
- RL 仍是基础 Q-Learning 原型，不是复杂深度强化学习系统
- 实时数据接口已预留，但默认验证流程仍以历史数据回测为主
- 未接入真实 LLM / OpenAI API
- 仍是研究系统，不是实盘系统

## 下一步计划

- 继续优化状态空间、奖励函数和训练轮数
- 接入更严格的训练集 / 测试集实验流程
- 增加市场状态识别和风险控制
- 增加多策略对比和参数实验
- 接入 LLM 生成更自然的研究报告和实验复盘

## 免责声明

本项目仅用于学习和研究，不构成任何投资建议。
