import numpy as np

STATE_FEATURE_NAMES = ["ma_gap", "rsi14", "macd_ratio", "momentum_5", "volume_ratio", "position"]


def add_rl_features(df):
    feature_df = df.copy()

    feature_df["return_1d"] = feature_df["close"].pct_change()
    feature_df["momentum_5"] = feature_df["close"].pct_change(5)

    feature_df["ma5"] = feature_df["close"].rolling(5).mean()
    feature_df["ma20"] = feature_df["close"].rolling(20).mean()
    feature_df["ma_gap"] = (feature_df["ma5"] - feature_df["ma20"]) / feature_df["close"]

    delta = feature_df["close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    feature_df["rsi14"] = 100 - (100 / (1 + rs))

    ema12 = feature_df["close"].ewm(span=12, adjust=False).mean()
    ema26 = feature_df["close"].ewm(span=26, adjust=False).mean()
    feature_df["macd_line"] = ema12 - ema26
    feature_df["macd_signal"] = feature_df["macd_line"].ewm(span=9, adjust=False).mean()
    feature_df["macd_hist"] = feature_df["macd_line"] - feature_df["macd_signal"]
    feature_df["macd_ratio"] = feature_df["macd_hist"] / feature_df["close"]

    feature_df["volume_ma20"] = feature_df["volume"].rolling(20).mean()
    feature_df["volume_ratio"] = feature_df["volume"] / feature_df["volume_ma20"]

    feature_df = feature_df.dropna().reset_index(drop=True)
    return feature_df


def _bin_value(value, thresholds):
    for idx, threshold in enumerate(thresholds):
        if value < threshold:
            return idx
    return len(thresholds)


def build_state(row, position):
    trend_bin = _bin_value(row["ma_gap"], [-0.01, 0.01])
    rsi_bin = _bin_value(row["rsi14"], [35, 65])
    macd_bin = _bin_value(row["macd_ratio"], [-0.002, 0.002])
    momentum_bin = _bin_value(row["momentum_5"], [-0.03, 0.03])
    volume_bin = _bin_value(row["volume_ratio"], [0.8, 1.2])
    return (trend_bin, rsi_bin, macd_bin, momentum_bin, volume_bin, int(position))
