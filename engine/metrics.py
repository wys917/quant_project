import numpy as np
import pandas as pd
def calculate_trade_stats(trades_df):
    if len(trades_df) == 0:
        return {
            "win_rate": 0,
            "avg_win": 0,
            "avg_loss": 0,
            "profit_loss_ratio": 0
        }

    pnl = trades_df["pnl_pct"]

    win_trades = pnl[pnl > 0]
    loss_trades = pnl[pnl < 0]

    win_rate = len(win_trades) / len(pnl)

    avg_win = win_trades.mean() if len(win_trades) > 0 else 0
    avg_loss = loss_trades.mean() if len(loss_trades) > 0 else 0

    profit_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else float("inf")

    return {
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_loss_ratio": profit_loss_ratio
    }

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
