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
# 5. Return
# =========================

df["return"] = (
    df["close"]
    .pct_change()
)


# =========================
# 6. 24h Volatility
# =========================

df["volatility_24h"] = (
    df["return"]
    .rolling(window=24)
    .std()
)


# =========================
# 7. Long-term Volatility
# =========================

df["volatility_mean"] = (
    df["volatility_24h"]
    .rolling(window=168)
    .mean()
)


# =========================
# 8. Regime
# =========================

df["regime"] = "normal"


df.loc[
    df["volatility_24h"] > df["volatility_mean"],
    "regime"
] = "high_vol"


df.loc[
    df["volatility_24h"] <= df["volatility_mean"],
    "regime"
] = "low_vol"


# =========================
# 9. 24h Momentum
# =========================

df["momentum"] = (
    df["close"]
    .pct_change(periods=24)
)


# =========================
# 10. Signal
# =========================

df["signal"] = 0


# Low Vol + Positive Momentum
df.loc[
    (
        df["regime"] == "low_vol"
    )
    &
    (
        df["momentum"] > 0
    ),
    "signal"
] = 1


# High Vol + Negative Momentum
df.loc[
    (
        df["regime"] == "high_vol"
    )
    &
    (
        df["momentum"] < 0
    ),
    "signal"
] = 1


# =========================
# 11. Strategy Return
# =========================

df["strategy_return"] = (
    df["signal"].shift(1)
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
# 15. Drawdown
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


# =========================
# 17. Regime Statistics
# =========================

low_vol_momentum_hours = (
    (
        (df["regime"] == "low_vol")
        &
        (df["momentum"] > 0)
    )
    .sum()
)


high_vol_reversion_hours = (
    (
        (df["regime"] == "high_vol")
        &
        (df["momentum"] < 0)
    )
    .sum()
)


# =========================
# 18. Result
# =========================

print("\n===== DAY 12 REGIME STRATEGY =====")

print(
    f"Total Return: {total_return:.2f}%"
)

print(
    f"MDD: {mdd:.2f}%"
)

print(
    f"Trades: {trades}"
)

print(
    f"Low Vol Momentum Hours: "
    f"{low_vol_momentum_hours}"
)

print(
    f"High Vol Reversion Hours: "
    f"{high_vol_reversion_hours}"
)


print("\n===== LATEST MARKET STATE =====")

print(
    df[
        [
            "timestamp",
            "close",
            "volatility_24h",
            "volatility_mean",
            "momentum",
            "regime",
            "signal"
        ]
    ].tail(10)
)