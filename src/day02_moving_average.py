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


# 3. DataFrame 변환
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


# 5. 수익률 계산
df["return"] = df["close"].pct_change()


# 6. 이동평균 계산
df["ma_short"] = df["close"].rolling(window=10).mean()
df["ma_long"] = df["close"].rolling(window=30).mean()


# 7. 매매 신호 생성
df["signal"] = 0

df.loc[
    df["ma_short"] > df["ma_long"],
    "signal"
] = 1

df.loc[
    df["ma_short"] < df["ma_long"],
    "signal"
] = -1


# 8. 결과 확인
print(
    df[
        [
            "timestamp",
            "close",
            "ma_short",
            "ma_long",
            "signal"
        ]
    ].tail(20)
)


# 9. 그래프
plt.figure(figsize=(12, 6))

plt.plot(
    df["timestamp"],
    df["close"],
    label="BTC Price"
)

plt.plot(
    df["timestamp"],
    df["ma_short"],
    label="MA 10"
)

plt.plot(
    df["timestamp"],
    df["ma_long"],
    label="MA 30"
)

plt.title("BTC Moving Average Strategy")
plt.xlabel("Time")
plt.ylabel("Price")

plt.legend()
plt.grid()

plt.show()