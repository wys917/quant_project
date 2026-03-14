import numpy as np
import pandas as pd


def calculate_metrics(df, equity_col="equity_curve"):
    """
    输入:
        df: 回测结果 dataframe
        equity_col: 净值列名
    输出:
        dict: 回测指标
    """

    equity = df[equity_col]

    # ===== 总收益 =====
    total_return = equity.iloc[-1] - 1

    # ===== 年化收益 =====
    days = (df["datetime"].iloc[-1] - df["datetime"].iloc[0]).days
    annual_return = (1 + total_return) ** (365 / days) - 1

    # ===== 每日收益 =====
    daily_returns = equity.pct_change().dropna()

    # ===== 波动率 =====
    volatility = daily_returns.std() * np.sqrt(365)

    # ===== Sharpe Ratio =====
    sharpe = daily_returns.mean() / daily_returns.std() * np.sqrt(365)

    # ===== 最大回撤 =====
    rolling_max = equity.cummax()
    drawdown = equity / rolling_max - 1
    max_drawdown = drawdown.min()

    metrics = {
        "total_return": total_return,
        "annual_return": annual_return,
        "volatility": volatility,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown
    }

    return metrics
