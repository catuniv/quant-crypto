import ccxt
import pandas as pd


# 1. Binance 연결
exchange = ccxt.binance()


# 2. BTC/USDT 1시간봉 1000개
ohlcv = exchange.fetch_ohlcv(
    symbol="BTC/USDT",
    timeframe="1h",
    limit=1000
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


# 6. Train / Test 분리
split_index = int(len(df) * 0.7)

train_df = df.iloc[:split_index].copy()
test_df = df.iloc[split_index:].copy()


print("Total rows:", len(df))
print("Train rows:", len(train_df))
print("Test rows:", len(test_df))


# 7. 수수료
fee_rate = 0.001


# 8. 후보 파라미터
short_windows = [5, 10, 15, 20]
long_windows = [30, 40, 50, 60]


# =========================
# 전략 평가 함수
# =========================

def backtest(data, short_window, long_window):

    data = data.copy()

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

    data["signal"] = 0

    data.loc[
        data["ma_short"] > data["ma_long"],
        "signal"
    ] = 1

    data["strategy_return"] = (
        data["signal"].shift(1)
        * data["return"]
    )

    data["trade"] = (
        data["signal"]
        .diff()
        .abs()
    )

    data["strategy_return_after_fee"] = (
        data["strategy_return"]
        - data["trade"] * fee_rate
    )

    data["equity"] = (
        1
        + data["strategy_return_after_fee"].fillna(0)
    ).cumprod()

    total_return = (
        data["equity"].iloc[-1] - 1
    ) * 100

    data["peak"] = data["equity"].cummax()

    data["drawdown"] = (
        data["equity"] / data["peak"]
    ) - 1

    mdd = (
        data["drawdown"].min()
    ) * 100

    trade_count = int(
        data["trade"].sum()
    )

    return {
        "return": total_return,
        "mdd": mdd,
        "trades": trade_count
    }


# =========================
# Train 구간에서 탐색
# =========================

results = []

for short_window in short_windows:

    for long_window in long_windows:

        if short_window >= long_window:
            continue

        result = backtest(
            train_df,
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


# =========================
# Train 최고 파라미터
# =========================

best = result_df.iloc[0]

best_short = int(
    best["short_ma"]
)

best_long = int(
    best["long_ma"]
)


print("\n===== TRAIN BEST =====")

print(
    f"Short MA: {best_short}"
)

print(
    f"Long MA: {best_long}"
)

print(
    f"Train Return: "
    f"{best['return']:.2f}%"
)

print(
    f"Train MDD: "
    f"{best['mdd']:.2f}%"
)


# =========================
# Test 구간 검증
# =========================

test_result = backtest(
    test_df,
    best_short,
    best_long
)


print("\n===== OUT OF SAMPLE TEST =====")

print(
    f"Test Return: "
    f"{test_result['return']:.2f}%"
)

print(
    f"Test MDD: "
    f"{test_result['mdd']:.2f}%"
)

print(
    f"Test Trades: "
    f"{test_result['trades']}"
)