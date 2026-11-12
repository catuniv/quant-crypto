import ccxt
import pandas as pd
import matplotlib.pyplot as plt


# 1. Binance 연결
exchange = ccxt.binance()


# 2. 실제 BTC/USDT 1시간봉 500개 가져오기
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


# 9. 매매 발생 여부 확인
df["trade"] = df["signal"].diff().abs()


# 10. Binance Spot 수수료
fee_rate = 0.001     # 0.1%


# 11. 수수료 차감
df["strategy_return_after_fee"] = (
    df["strategy_return"]
    - df["trade"] * fee_rate
)


# 12. 누적 수익률
df["buy_hold"] = (
    1 + df["return"].fillna(0)
).cumprod()

df["strategy_no_fee"] = (
    1 + df["strategy_return"].fillna(0)
).cumprod()

df["strategy_with_fee"] = (
    1 + df["strategy_return_after_fee"].fillna(0)
).cumprod()


# 13. 거래 횟수
trade_count = df["trade"].sum()


# 14. 최종 결과
print("===== BACKTEST RESULT =====")

print(
    f"Buy & Hold: "
    f"{(df['buy_hold'].iloc[-1] - 1) * 100:.2f}%"
)

print(
    f"Strategy without fee: "
    f"{(df['strategy_no_fee'].iloc[-1] - 1) * 100:.2f}%"
)

print(
    f"Strategy with fee: "
    f"{(df['strategy_with_fee'].iloc[-1] - 1) * 100:.2f}%"
)

print(
    f"Number of trades: "
    f"{int(trade_count)}"
)


# 15. 그래프
plt.figure(figsize=(12, 6))

plt.plot(
    df["timestamp"],
    df["buy_hold"],
    label="Buy & Hold"
)

plt.plot(
    df["timestamp"],
    df["strategy_no_fee"],
    label="Strategy No Fee"
)

plt.plot(
    df["timestamp"],
    df["strategy_with_fee"],
    label="Strategy With Fee"
)

plt.title("Backtest With Binance Trading Fee")
plt.xlabel("Time")
plt.ylabel("Growth of $1")

plt.legend()
plt.grid()

plt.show()