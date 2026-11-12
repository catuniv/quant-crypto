import ccxt
import pandas as pd


# 1. Binance 연결
exchange = ccxt.binance()


# 2. BTC/USDT 1시간봉 500개
ohlcv = exchange.fetch_ohlcv(
    symbol="BTC/USDT",
    timeframe="1h",
    limit=500
)


# 3. DataFrame
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


# 5. 수익률
df["return"] = df["close"].pct_change()


# 6. 수수료
fee_rate = 0.001


# 7. 결과 저장용 리스트
results = []


# 8. 단기 이동평균 후보
short_windows = [
    5,
    10,
    15,
    20
]


# 9. 장기 이동평균 후보
long_windows = [
    30,
    40,
    50,
    60
]


# 10. 모든 조합 테스트
for short_window in short_windows:

    for long_window in long_windows:

        # 단기 MA가 장기 MA보다 작아야 함
        if short_window >= long_window:
            continue


        # 이동평균
        df["ma_short"] = (
            df["close"]
            .rolling(window=short_window)
            .mean()
        )

        df["ma_long"] = (
            df["close"]
            .rolling(window=long_window)
            .mean()
        )


        # 포지션
        df["signal"] = 0

        df.loc[
            df["ma_short"] > df["ma_long"],
            "signal"
        ] = 1


        # 전략 수익률
        df["strategy_return"] = (
            df["signal"].shift(1)
            * df["return"]
        )


        # 거래 발생
        df["trade"] = (
            df["signal"]
            .diff()
            .abs()
        )


        # 수수료 포함 수익률
        df["strategy_return_after_fee"] = (
            df["strategy_return"]
            - df["trade"] * fee_rate
        )


        # 누적 자산
        df["equity"] = (
            1
            + df["strategy_return_after_fee"].fillna(0)
        ).cumprod()


        # 최종 수익률
        total_return = (
            df["equity"].iloc[-1] - 1
        ) * 100


        # MDD
        df["peak"] = (
            df["equity"].cummax()
        )

        df["drawdown"] = (
            df["equity"]
            / df["peak"]
        ) - 1

        max_drawdown = (
            df["drawdown"].min()
        ) * 100


        # 거래 횟수
        trade_count = int(
            df["trade"].sum()
        )


        # 결과 저장
        results.append(
            {
                "short_ma": short_window,
                "long_ma": long_window,
                "return": total_return,
                "mdd": max_drawdown,
                "trades": trade_count
            }
        )


# 11. 결과 DataFrame
result_df = pd.DataFrame(results)


# 12. 수익률 높은 순서로 정렬
result_df = result_df.sort_values(
    by="return",
    ascending=False
)


# 13. 전체 결과
print(
    "\n===== PARAMETER SEARCH RESULT ====="
)

print(
    result_df.to_string(
        index=False
    )
)


# 14. 최고 결과
best = result_df.iloc[0]

print(
    "\n===== BEST PARAMETER ====="
)

print(
    f"Short MA: {int(best['short_ma'])}"
)

print(
    f"Long MA: {int(best['long_ma'])}"
)

print(
    f"Return: {best['return']:.2f}%"
)

print(
    f"MDD: {best['mdd']:.2f}%"
)

print(
    f"Trades: {int(best['trades'])}"
)