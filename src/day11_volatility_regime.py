import ccxt
import pandas as pd


# =========================
# 1. Binance 연결
# =========================

exchange = ccxt.binance()


# =========================
# 2. BTC/USDT 1시간봉
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
# 4. 시간 변환
# =========================

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    unit="ms"
)


# =========================
# 5. 수익률
# =========================

df["return"] = (
    df["close"]
    .pct_change()
)


# =========================
# 6. 최근 24시간 변동성
# =========================

df["volatility_24h"] = (
    df["return"]
    .rolling(window=24)
    .std()
)


# =========================
# 7. 장기 평균 변동성
# =========================

df["volatility_mean"] = (
    df["volatility_24h"]
    .rolling(window=168)
    .mean()
)


# =========================
# 8. Regime 분류
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
# 9. Momentum signal
# =========================

df["momentum"] = (
    df["close"]
    .pct_change(periods=24)
)

df["signal"] = 0

df.loc[
    (
        df["momentum"] > 0
    )
    &
    (
        df["regime"] == "low_vol"
    ),
    "signal"
] = 1


# =========================
# 10. 전략 수익률
# =========================

df["strategy_return"] = (
    df["signal"].shift(1)
    * df["return"]
)


# =========================
# 11. 거래 발생
# =========================

df["trade"] = (
    df["signal"]
    .diff()
    .abs()
)


# =========================
# 12. 수수료
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
# 14. MDD
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

mdd = (
    df["drawdown"]
    .min()
) * 100


# =========================
# 15. Total Return
# =========================

total_return = (
    df["equity"].iloc[-1]
    - 1
) * 100


# =========================
# 16. Regime 통계
# =========================

high_vol_count = (
    df["regime"]
    == "high_vol"
).sum()

low_vol_count = (
    df["regime"]
    == "low_vol"
).sum()


# =========================
# 17. 출력
# =========================

print(
    "\n===== VOLATILITY REGIME ====="
)

print(
    f"High Volatility Hours: "
    f"{high_vol_count}"
)

print(
    f"Low Volatility Hours: "
    f"{low_vol_count}"
)

print(
    f"Total Return: "
    f"{total_return:.2f}%"
)

print(
    f"MDD: "
    f"{mdd:.2f}%"
)

print(
    f"Trades: "
    f"{int(df['trade'].sum())}"
)


print(
    "\n===== LATEST MARKET STATE ====="
)

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