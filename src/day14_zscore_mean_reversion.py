import ccxt
import pandas as pd


# =========================
# 1. Exchange
# =========================

exchange = ccxt.binance()


# =========================
# 2. Market Data
# =========================

ohlcv = exchange.fetch_ohlcv(
    symbol="BTC/USDT",
    timeframe="1h",
    limit=1000
)


# =========================
# 3. DataFrame
# =========================

df = pd.DataFrame(
    ohlcv,
    columns=[
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]
)


# =========================
# 4. Timestamp
# =========================

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    unit="ms"
)


# =========================
# 5. 1h Return
# =========================

df["return"] = (
    df["close"]
    .pct_change()
)


# =========================
# 6. 24h Return
# =========================

df["return_24h"] = (
    df["close"]
    .pct_change(periods=24)
)


# =========================
# 7. Rolling Mean
# =========================

lookback = 168


df["return_24h_mean"] = (
    df["return_24h"]
    .rolling(window=lookback)
    .mean()
)


# =========================
# 8. Rolling Standard Deviation
# =========================

df["return_24h_std"] = (
    df["return_24h"]
    .rolling(window=lookback)
    .std()
)


# =========================
# 9. Z-Score
# =========================

df["zscore"] = (
    (
        df["return_24h"]
        - df["return_24h_mean"]
    )
    /
    df["return_24h_std"]
)


# =========================
# 10. Signal
# =========================

entry_z = -1.5


df["signal"] = 0


df.loc[
    df["zscore"] < entry_z,
    "signal"
] = 1


# =========================
# 11. Strategy Return
# =========================

df["strategy_return"] = (
    df["signal"]
    .shift(1)
    * df["return"]
)


# =========================
# 12. Trade
# =========================

df["trade"] = (
    df["signal"]
    .diff()
    .abs()
)


# =========================
# 13. Fee
# =========================

fee_rate = 0.001


df["strategy_return_after_fee"] = (
    df["strategy_return"]
    - df["trade"] * fee_rate
)


# =========================
# 14. Equity
# =========================

df["equity"] = (
    1
    + df["strategy_return_after_fee"]
    .fillna(0)
).cumprod()


# =========================
# 15. Peak / Drawdown
# =========================

df["peak"] = (
    df["equity"]
    .cummax()
)


df["drawdown"] = (
    df["equity"]
    / df["peak"]
    - 1
)


# =========================
# 16. Metrics
# =========================

total_return = (
    df["equity"].iloc[-1]
    - 1
) * 100


mdd = (
    df["drawdown"]
    .min()
) * 100


trades = int(
    df["trade"]
    .fillna(0)
    .sum()
)


long_hours = int(
    (
        df["signal"] == 1
    )
    .sum()
)


# =========================
# 17. Buy & Hold
# =========================

df["buy_hold_equity"] = (
    1
    + df["return"].fillna(0)
).cumprod()


buy_hold_return = (
    df["buy_hold_equity"].iloc[-1]
    - 1
) * 100


# =========================
# 18. Result
# =========================

print(
    "\n===== DAY 14 Z-SCORE MEAN REVERSION ====="
)

print(
    f"Entry Z: {entry_z}"
)

print(
    f"Strategy Return: "
    f"{total_return:.2f}%"
)

print(
    f"Buy & Hold Return: "
    f"{buy_hold_return:.2f}%"
)

print(
    f"MDD: "
    f"{mdd:.2f}%"
)

print(
    f"Trades: "
    f"{trades}"
)

print(
    f"Long Hours: "
    f"{long_hours}"
)


print(
    "\n===== LATEST STATE ====="
)

print(
    df[
        [
            "timestamp",
            "close",
            "return_24h",
            "return_24h_mean",
            "return_24h_std",
            "zscore",
            "signal"
        ]
    ].tail(15)
)