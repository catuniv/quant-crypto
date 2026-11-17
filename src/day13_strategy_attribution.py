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
# 6. Volatility
# =========================

df["volatility_24h"] = (
    df["return"]
    .rolling(window=24)
    .std()
)


df["volatility_mean"] = (
    df["volatility_24h"]
    .rolling(window=168)
    .mean()
)


# =========================
# 7. Regime
# =========================

df["regime"] = "normal"


df.loc[
    df["volatility_24h"]
    > df["volatility_mean"],
    "regime"
] = "high_vol"


df.loc[
    df["volatility_24h"]
    <= df["volatility_mean"],
    "regime"
] = "low_vol"


# =========================
# 8. Momentum
# =========================

df["momentum"] = (
    df["close"]
    .pct_change(periods=24)
)


# =========================
# 9. Separate Signals
# =========================

df["momentum_signal"] = 0

df.loc[
    (
        (df["regime"] == "low_vol")
        &
        (df["momentum"] > 0)
    ),
    "momentum_signal"
] = 1


df["reversion_signal"] = 0

df.loc[
    (
        (df["regime"] == "high_vol")
        &
        (df["momentum"] < 0)
    ),
    "reversion_signal"
] = 1


# =========================
# 10. Strategy Returns
# =========================

df["momentum_return"] = (
    df["momentum_signal"]
    .shift(1)
    * df["return"]
)


df["reversion_return"] = (
    df["reversion_signal"]
    .shift(1)
    * df["return"]
)


# =========================
# 11. Trades
# =========================

df["momentum_trade"] = (
    df["momentum_signal"]
    .diff()
    .abs()
)


df["reversion_trade"] = (
    df["reversion_signal"]
    .diff()
    .abs()
)


# =========================
# 12. Fee
# =========================

fee_rate = 0.001


df["momentum_after_fee"] = (
    df["momentum_return"]
    - df["momentum_trade"] * fee_rate
)


df["reversion_after_fee"] = (
    df["reversion_return"]
    - df["reversion_trade"] * fee_rate
)


# =========================
# 13. Equity
# =========================

df["momentum_equity"] = (
    1
    + df["momentum_after_fee"]
    .fillna(0)
).cumprod()


df["reversion_equity"] = (
    1
    + df["reversion_after_fee"]
    .fillna(0)
).cumprod()


# =========================
# 14. Drawdown
# =========================

df["momentum_peak"] = (
    df["momentum_equity"]
    .cummax()
)


df["momentum_drawdown"] = (
    df["momentum_equity"]
    / df["momentum_peak"]
    - 1
)


df["reversion_peak"] = (
    df["reversion_equity"]
    .cummax()
)


df["reversion_drawdown"] = (
    df["reversion_equity"]
    / df["reversion_peak"]
    - 1
)


# =========================
# 15. Metrics
# =========================

momentum_total_return = (
    df["momentum_equity"].iloc[-1]
    - 1
) * 100


momentum_mdd = (
    df["momentum_drawdown"]
    .min()
) * 100


momentum_trades = int(
    df["momentum_trade"]
    .fillna(0)
    .sum()
)


reversion_total_return = (
    df["reversion_equity"].iloc[-1]
    - 1
) * 100


reversion_mdd = (
    df["reversion_drawdown"]
    .min()
) * 100


reversion_trades = int(
    df["reversion_trade"]
    .fillna(0)
    .sum()
)


# =========================
# 16. Fee Sensitivity
# =========================

fee_rates = [
    0.0,
    0.0005,
    0.001
]


print("\n===== FEE SENSITIVITY =====")


for fee in fee_rates:

    momentum_fee_return = (
        df["momentum_return"]
        - df["momentum_trade"] * fee
    )

    momentum_fee_equity = (
        1
        + momentum_fee_return.fillna(0)
    ).cumprod()


    reversion_fee_return = (
        df["reversion_return"]
        - df["reversion_trade"] * fee
    )

    reversion_fee_equity = (
        1
        + reversion_fee_return.fillna(0)
    ).cumprod()


    momentum_result = (
        momentum_fee_equity.iloc[-1]
        - 1
    ) * 100


    reversion_result = (
        reversion_fee_equity.iloc[-1]
        - 1
    ) * 100


    print(
        f"\nFee: {fee * 100:.2f}%"
    )

    print(
        f"Momentum Return: "
        f"{momentum_result:.2f}%"
    )

    print(
        f"Reversion Return: "
        f"{reversion_result:.2f}%"
    )


# =========================
# 17. Final Result
# =========================

print("\n===== MOMENTUM STRATEGY =====")

print(
    f"Return: "
    f"{momentum_total_return:.2f}%"
)

print(
    f"MDD: "
    f"{momentum_mdd:.2f}%"
)

print(
    f"Trades: "
    f"{momentum_trades}"
)


print("\n===== MEAN REVERSION STRATEGY =====")

print(
    f"Return: "
    f"{reversion_total_return:.2f}%"
)

print(
    f"MDD: "
    f"{reversion_mdd:.2f}%"
)

print(
    f"Trades: "
    f"{reversion_trades}"
)


print("\n===== LATEST STATE =====")

print(
    df[
        [
            "timestamp",
            "close",
            "momentum",
            "regime",
            "momentum_signal",
            "reversion_signal"
        ]
    ].tail(10)
)