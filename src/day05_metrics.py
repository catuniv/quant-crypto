import ccxt
import pandas as pd
import matplotlib.pyplot as plt


# 1. Binance 연결
exchange = ccxt.binance()


# 2. BTC/USDT 1시간봉 500개 가져오기
ohlcv = exchange.fetch_ohlcv(
    symbol="BTC/USDT",
    timeframe="1h",
    limit=500
)


# 3. DataFrame 생성
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


# 4. 시간 변환
df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    unit="ms"
)


# 5. BTC 수익률
df["return"] = df["close"].pct_change()


# 6. 이동평균
df["ma_short"] = df["close"].rolling(window=10).mean()
df["ma_long"] = df["close"].rolling(window=30).mean()


# 7. 포지션
df["signal"] = 0

df.loc[
    df["ma_short"] > df["ma_long"],
    "signal"
] = 1


# 8. 전략 수익률
df["strategy_return"] = (
    df["signal"].shift(1)
    * df["return"]
)


# 9. 거래 발생
df["trade"] = df["signal"].diff().abs()


# 10. 수수료
fee_rate = 0.001

df["strategy_return_after_fee"] = (
    df["strategy_return"]
    - df["trade"] * fee_rate
)


# 11. 누적 자산
df["equity"] = (
    1 + df["strategy_return_after_fee"].fillna(0)
).cumprod()


# =========================
# 12. 전략 평가 지표
# =========================


# 최종 수익률
total_return = (
    df["equity"].iloc[-1] - 1
) * 100


# 승률
winning_periods = (
    df["strategy_return_after_fee"] > 0
).sum()

losing_periods = (
    df["strategy_return_after_fee"] < 0
).sum()

win_rate = (
    winning_periods
    / (winning_periods + losing_periods)
    * 100
)


# 최대 낙폭 MDD
df["peak"] = df["equity"].cummax()

df["drawdown"] = (
    df["equity"] / df["peak"]
) - 1

max_drawdown = (
    df["drawdown"].min()
) * 100


# Sharpe Ratio
mean_return = df["strategy_return_after_fee"].mean()

std_return = df["strategy_return_after_fee"].std()

sharpe_ratio = (
    mean_return / std_return
) * (24 * 365) ** 0.5


# 거래 횟수
trade_count = int(
    df["trade"].sum()
)


# =========================
# 13. 결과 출력
# =========================

print("===== STRATEGY METRICS =====")

print(
    f"Total Return: "
    f"{total_return:.2f}%"
)

print(
    f"Win Rate: "
    f"{win_rate:.2f}%"
)

print(
    f"Max Drawdown: "
    f"{max_drawdown:.2f}%"
)

print(
    f"Sharpe Ratio: "
    f"{sharpe_ratio:.2f}"
)

print(
    f"Number of Trades: "
    f"{trade_count}"
)


# =========================
# 14. Equity Curve
# =========================

plt.figure(figsize=(12, 6))

plt.plot(
    df["timestamp"],
    df["equity"],
    label="Strategy Equity"
)

plt.title("Strategy Equity Curve")
plt.xlabel("Time")
plt.ylabel("Growth of $1")

plt.legend()
plt.grid()

plt.show()