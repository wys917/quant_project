# quant_project

一个面向初学者的量化研究练手项目，目标是逐步搭建一个“传统量化底盘 + 智能体研究助手”的系统原型。

## 项目定位

- 先把基础研究链路跑通，再逐步接入更智能的研究助手能力
- 当前重点不是做复杂框架，而是把数据、回测、指标、报告整理成清晰可复用的输入输出链路
- 项目适合学习 pandas、简单回测逻辑、结构化研究结果导出，以及后续的 Agent/LLM 接口准备

## 当前实现

- BTCUSDT 日线历史数据
- 双均线策略
- 当天收盘出信号、次日开盘成交的回测逻辑
- 回测指标输出
- 交易统计输出
- 自动导出结构化结果
- 自动生成 Markdown 策略报告

## 当前阶段

- 单标的：BTCUSDT
- 数据频率：1d
- 策略：双均线策略（MA5 / MA20）
- 系统形态：最小可用回测系统 + 规则驱动研究报告

## 目录结构

```text
quant_project/
├── data/
│   ├── raw/
│   └── processed/
│       ├── BTCUSDT_1d_full.csv
│       └── results/
│           ├── metrics.json
│           ├── trades.csv
│           ├── round_trips.csv
│           ├── equity_curve.csv
│           └── summary.txt
├── engine/
│   ├── __init__.py
│   └── metrics.py
├── notebooks/
│   ├── merge_monthly_data.py
│   ├── check_data.py
│   ├── ma_strategy.py
│   └── backtest_ma_v3.py
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

## 运行顺序

```bash
python notebooks/merge_monthly_data.py
python notebooks/check_data.py
python notebooks/ma_strategy.py
python notebooks/backtest_ma_v3.py
python agent/agent_report.py
```

## 回测结果输出

运行 `python notebooks/backtest_ma_v3.py` 后，会自动生成：

- `data/processed/results/metrics.json`
- `data/processed/results/trades.csv`
- `data/processed/results/round_trips.csv`
- `data/processed/results/equity_curve.csv`
- `data/processed/results/summary.txt`

运行 `python agent/agent_report.py` 后，会自动生成：

- `report/strategy_report.md`

## 当前限制

- 仅单标的
- 仅单策略
- 仅日线研究
- 未接入真实 LLM / OpenAI API
- 仍是研究系统，不是实盘系统

## 下一步计划

- 接入 LLM 生成更自然的研究报告
- 增加市场状态识别
- 增加多策略对比
- 增加参数实验系统
- 增加风控模块

## 免责声明

本项目仅用于学习和研究，不构成任何投资建议。
