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


# 5. BTC 자체 수익률
df["return"] = df["close"].pct_change()


# 6. 이동평균
df["ma_short"] = df["close"].rolling(window=10).mean()
df["ma_long"] = df["close"].rolling(window=30).mean()


# 7. 매매 방향
df["signal"] = 0

df.loc[
    df["ma_short"] > df["ma_long"],
    "signal"
] = 1

df.loc[
    df["ma_short"] < df["ma_long"],
    "signal"
] = 0


# 8. 전략 수익률 계산
df["strategy_return"] = (
    df["signal"].shift(1)
    * df["return"]
)


# 9. 누적 수익률 계산
df["buy_hold"] = (
    1 + df["return"].fillna(0)
).cumprod()

df["strategy"] = (
    1 + df["strategy_return"].fillna(0)
).cumprod()


# 10. 최종 결과
print("Buy & Hold:")
print(df["buy_hold"].iloc[-1])

print()

print("Moving Average Strategy:")
print(df["strategy"].iloc[-1])


# 11. 그래프
plt.figure(figsize=(12, 6))

plt.plot(
    df["timestamp"],
    df["buy_hold"],
    label="Buy & Hold"
)

plt.plot(
    df["timestamp"],
    df["strategy"],
    label="MA Strategy"
)

plt.title("Backtest Result")
plt.xlabel("Time")
plt.ylabel("Growth of $1")

plt.legend()
plt.grid()

plt.show()