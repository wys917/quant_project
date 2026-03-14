# quant_project

一个面向初学者的量化交易练手项目，路线是：**传统量化底盘 + 智能体研究助手**。

## 当前阶段

- 单标的：BTCUSDT
- 数据频率：日线（1d）
- 策略：双均线策略（MA）
- 系统：最小回测系统（含交易记录与基础绩效指标）

## 目录结构

```text
quant_project/
├── main.py
├── engine/
│   └── metrics.py
├── notebooks/
│   ├── merge_monthly_data.py
│   ├── check_data.py
│   ├── ma_strategy.py
│   ├── backtest_ma.py
│   ├── backtest_ma_v2.py
│   ├── backtest_ma_v3.py
│   └── prepare_data.py
├── data/
│   ├── raw/
│   │   └── monthly/         # 原始月度K线（默认不入库）
│   └── processed/           # 合并后的数据与回测结果样例
├── config/
├── strategies/
└── report/
```

## 数据准备

1. 将 BTCUSDT 日线月度原始数据放入 `data/raw/monthly/`（例如 Binance 导出的月度 CSV）。
2. 运行数据合并脚本生成全量日线文件。
3. 使用数据检查脚本确认字段和时间范围。

> 说明：`data/raw/` 已在 `.gitignore` 中忽略，避免将大体量原始数据上传到 GitHub。

## 运行方式

```bash
python notebooks/merge_monthly_data.py
python notebooks/check_data.py
python notebooks/ma_strategy.py
python notebooks/backtest_ma_v3.py
```

## 当前已实现功能

- 原始月度数据合并为统一日线数据
- 数据质量检查与可视化验证
- 双均线信号生成
- 回测执行（含交易记录、回合交易、基础绩效统计）

## 下一步计划

- 增加参数网格与批量回测
- 增加手续费/滑点与更真实的成交模型
- 扩展到多标的与组合视角
- 逐步接入“智能体研究助手”用于实验管理与结果解释

## 免责声明

本项目仅用于学习与研究，不构成任何投资建议。
