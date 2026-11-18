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
# 6. 24h Momentum
# =========================

df["momentum_24h"] = (
    df["close"]
    .pct_change(periods=24)
)


# =========================
# 7. Volume Mean
# =========================

volume_window = 24


df["volume_mean"] = (
    df["volume"]
    .rolling(window=volume_window)
    .mean()
)


# =========================
# 8. Volume Ratio
# =========================

df["volume_ratio"] = (
    df["volume"]
    / df["volume_mean"]
)


# =========================
# 9. Signal
# =========================

df["signal"] = 0


df.loc[
    (
        df["momentum_24h"] > 0
    )
    &
    (
        df["volume_ratio"] > 1.0
    ),
    "signal"
] = 1


# =========================
# 10. Strategy Return
# =========================

df["strategy_return"] = (
    df["signal"]
    .shift(1)
    * df["return"]
)


# =========================
# 11. Trade
# =========================

df["trade"] = (
    df["signal"]
    .diff()
    .abs()
)


# =========================
# 12. Fee
# =========================

fee_rate = 0.001


df["strategy_return_after_fee"] = (
    df["strategy_return"]
    - df["trade"] * fee_rate
)


# =========================
# 13. Equity
# =========================

df["equity"] = (
    1
    + df["strategy_return_after_fee"]
    .fillna(0)
).cumprod()


# =========================
# 14. Initial Capital
# =========================

initial_capital = 100


df["portfolio_value"] = (
    initial_capital
    * df["equity"]
)


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


final_value = (
    df["portfolio_value"]
    .iloc[-1]
)


profit_loss = (
    final_value
    - initial_capital
)


# =========================
# 17. Buy & Hold
# =========================

df["buy_hold_equity"] = (
    1
    + df["return"]
    .fillna(0)
).cumprod()


buy_hold_return = (
    df["buy_hold_equity"]
    .iloc[-1]
    - 1
) * 100


buy_hold_final = (
    initial_capital
    * df["buy_hold_equity"]
    .iloc[-1]
)


# =========================
# 18. Result
# =========================

print(
    "\n===== DAY 15 VOLUME ALPHA ====="
)

print(
    f"Initial Capital: "
    f"${initial_capital:.2f}"
)

print(
    f"Final Value: "
    f"${final_value:.2f}"
)

print(
    f"Profit / Loss: "
    f"${profit_loss:.2f}"
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
    f"Buy & Hold Final: "
    f"${buy_hold_final:.2f}"
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
            "volume",
            "volume_mean",
            "volume_ratio",
            "momentum_24h",
            "signal"
        ]
    ].tail(15)
)