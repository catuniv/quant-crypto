import ccxt
import pandas as pd


# =========================
# 1. Binance 연결
# =========================

exchange = ccxt.binance()


# =========================
# 2. BTC/USDT 1시간봉 1000개
# =========================

ohlcv = exchange.fetch_ohlcv(
    symbol="BTC/USDT",
    timeframe="1h",
    limit=1000
)


# =========================
# 3. DataFrame 생성
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

df["return"] = df["close"].pct_change()


# =========================
# 6. 설정값
# =========================

fee_rate = 0.001

short_windows = [
    5,
    10,
    15,
    20
]

long_windows = [
    30,
    40,
    50,
    60
]


# =========================
# 7. 백테스트 함수
# =========================

def backtest(
    data,
    short_window,
    long_window
):

    data = data.copy()

    # 이동평균
    data["ma_short"] = (
        data["close"]
        .rolling(window=short_window)
        .mean()
    )

    data["ma_long"] = (
        data["close"]
        .rolling(window=long_window)
        .mean()
    )


    # 포지션
    data["signal"] = 0

    data.loc[
        data["ma_short"] > data["ma_long"],
        "signal"
    ] = 1


    # 전략 수익률
    data["strategy_return"] = (
        data["signal"].shift(1)
        * data["return"]
    )


    # 거래 발생
    data["trade"] = (
        data["signal"]
        .diff()
        .abs()
    )


    # 수수료 반영
    data["strategy_return_after_fee"] = (
        data["strategy_return"]
        - data["trade"] * fee_rate
    )


    # 누적 자산
    data["equity"] = (
        1
        + data["strategy_return_after_fee"].fillna(0)
    ).cumprod()


    # 총 수익률
    total_return = (
        data["equity"].iloc[-1] - 1
    ) * 100


    # MDD
    data["peak"] = (
        data["equity"].cummax()
    )

    data["drawdown"] = (
        data["equity"]
        / data["peak"]
    ) - 1

    mdd = (
        data["drawdown"].min()
    ) * 100


    # 거래 횟수
    trades = int(
        data["trade"].sum()
    )


    return {
        "return": total_return,
        "mdd": mdd,
        "trades": trades
    }


# =========================
# 8. Train에서 최고의 파라미터 찾기
# =========================

def find_best_parameter(train_data):

    results = []

    for short_window in short_windows:

        for long_window in long_windows:

            if short_window >= long_window:
                continue

            result = backtest(
                train_data,
                short_window,
                long_window
            )

            results.append(
                {
                    "short_ma": short_window,
                    "long_ma": long_window,
                    "return": result["return"],
                    "mdd": result["mdd"],
                    "trades": result["trades"]
                }
            )


    result_df = pd.DataFrame(results)

    result_df = result_df.sort_values(
        by="return",
        ascending=False
    )

    best = result_df.iloc[0]

    return (
        int(best["short_ma"]),
        int(best["long_ma"]),
        best["return"]
    )


# =========================
# 9. Walk-Forward 설정
# =========================

train_size = 400
test_size = 100

start = 0

walk_forward_results = []


# =========================
# 10. Walk-Forward 반복
# =========================

while (
    start
    + train_size
    + test_size
    <= len(df)
):


    train_start = start

    train_end = (
        start + train_size
    )

    test_start = train_end

    test_end = (
        test_start + test_size
    )


    # Train / Test 생성
    train_df = (
        df.iloc[
            train_start:train_end
        ]
        .copy()
    )

    test_df = (
        df.iloc[
            test_start:test_end
        ]
        .copy()
    )


    # Train에서 최고 파라미터 찾기
    best_short, best_long, train_return = (
        find_best_parameter(
            train_df
        )
    )


    # Test에서 검증
    test_result = backtest(
        test_df,
        best_short,
        best_long
    )


    # 결과 저장
    walk_forward_results.append(
        {
            "train_start": train_df["timestamp"].iloc[0],
            "train_end": train_df["timestamp"].iloc[-1],
            "test_start": test_df["timestamp"].iloc[0],
            "test_end": test_df["timestamp"].iloc[-1],

            "short_ma": best_short,
            "long_ma": best_long,

            "train_return": train_return,

            "test_return": test_result["return"],
            "test_mdd": test_result["mdd"],
            "test_trades": test_result["trades"]
        }
    )


    # 다음 구간으로 이동
    start += test_size


# =========================
# 11. 결과 DataFrame
# =========================

result_df = pd.DataFrame(
    walk_forward_results
)


# =========================
# 12. 결과 출력
# =========================

print(
    "\n===== WALK-FORWARD RESULT ====="
)

print(
    result_df[
        [
            "short_ma",
            "long_ma",
            "train_return",
            "test_return",
            "test_mdd",
            "test_trades"
        ]
    ].to_string(
        index=False
    )
)


# =========================
# 13. 평균 Test 성능
# =========================

average_test_return = (
    result_df["test_return"].mean()
)

average_test_mdd = (
    result_df["test_mdd"].mean()
)


print(
    "\n===== SUMMARY ====="
)

print(
    f"Average Test Return: "
    f"{average_test_return:.2f}%"
)

print(
    f"Average Test MDD: "
    f"{average_test_mdd:.2f}%"
)

print(
    f"Number of Walk-Forward Tests: "
    f"{len(result_df)}"
)