import numpy as np


def calculate_trade_stats(round_trips_df):
    if len(round_trips_df) == 0 or "pnl_pct" not in round_trips_df.columns:
        return {
            "win_rate": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "profit_loss_ratio": 0.0,
            "total_trades": 0,
        }

    pnl = round_trips_df["pnl_pct"].dropna()
    total_trades = int(len(pnl))

    if total_trades == 0:
        return {
            "win_rate": 0.0,
            "avg_win": 0.0,
            "avg_loss": 0.0,
            "profit_loss_ratio": 0.0,
            "total_trades": 0,
        }

    win_trades = pnl[pnl > 0]
    loss_trades = pnl[pnl < 0]

    win_rate = len(win_trades) / total_trades
    avg_win = float(win_trades.mean()) if len(win_trades) > 0 else 0.0
    avg_loss = float(loss_trades.mean()) if len(loss_trades) > 0 else 0.0

    if avg_loss == 0:
        profit_loss_ratio = 0.0
    else:
        profit_loss_ratio = abs(avg_win / avg_loss)

    return {
        "win_rate": float(win_rate),
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_loss_ratio": float(profit_loss_ratio),
        "total_trades": total_trades,
    }


def calculate_metrics(df, equity_col="equity_curve", periods_per_year=365):
    equity = df[equity_col]
    total_return = float(equity.iloc[-1] - 1)

    days = (df["datetime"].iloc[-1] - df["datetime"].iloc[0]).days
    if days > 0:
        annual_return = float((1 + total_return) ** (periods_per_year / days) - 1)
    else:
        annual_return = 0.0

    daily_returns = equity.pct_change().dropna()

    if len(daily_returns) > 0:
        volatility = float(daily_returns.std() * np.sqrt(periods_per_year))
    else:
        volatility = 0.0

    if len(daily_returns) > 0 and daily_returns.std() != 0:
        sharpe = float(daily_returns.mean() / daily_returns.std() * np.sqrt(periods_per_year))
    else:
        sharpe = 0.0

    rolling_max = equity.cummax()
    drawdown = equity / rolling_max - 1
    max_drawdown = float(drawdown.min())

    return {
        "total_return": total_return,
        "annual_return": annual_return,
        "volatility": volatility,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
    }
