import ccxt
import pandas as pd


# =========================
# 1. Binance 연결
# =========================

exchange = ccxt.binance()


# =========================
# 2. BTC/USDT 데이터
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
# 5. 1시간 수익률
# =========================

df["return"] = (
    df["close"]
    .pct_change()
)


# =========================
# 6. Train / Test
# =========================

split_index = int(
    len(df) * 0.7
)

train_df = (
    df.iloc[:split_index]
    .copy()
)

test_df = (
    df.iloc[split_index:]
    .copy()
)


# =========================
# 7. 설정
# =========================

fee_rate = 0.001

lookbacks = [
    3,
    6,
    12,
    24
]


# =========================
# 8. Alpha 백테스트
# =========================

def backtest_alpha(
    data,
    lookback,
    alpha_type
):

    data = data.copy()


    # -------------------------
    # 과거 N시간 수익률
    # -------------------------

    data["past_return"] = (
        data["close"]
        .pct_change(
            periods=lookback
        )
    )


    # -------------------------
    # 기본 포지션
    # -------------------------

    data["signal"] = 0


    # -------------------------
    # Momentum
    # -------------------------

    if alpha_type == "momentum":

        data.loc[
            data["past_return"] > 0,
            "signal"
        ] = 1


    # -------------------------
    # Mean Reversion
    # -------------------------

    elif alpha_type == "mean_reversion":

        data.loc[
            data["past_return"] < 0,
            "signal"
        ] = 1


    # -------------------------
    # 전략 수익률
    # -------------------------

    data["strategy_return"] = (
        data["signal"].shift(1)
        * data["return"]
    )


    # -------------------------
    # 거래 발생
    # -------------------------

    data["trade"] = (
        data["signal"]
        .diff()
        .abs()
    )


    # -------------------------
    # 수수료
    # -------------------------

    data["strategy_return_after_fee"] = (
        data["strategy_return"]
        - data["trade"] * fee_rate
    )


    # -------------------------
    # 누적 자산
    # -------------------------

    data["equity"] = (
        1
        + data[
            "strategy_return_after_fee"
        ].fillna(0)
    ).cumprod()


    # -------------------------
    # 총 수익률
    # -------------------------

    total_return = (
        data["equity"].iloc[-1]
        - 1
    ) * 100


    # -------------------------
    # MDD
    # -------------------------

    data["peak"] = (
        data["equity"]
        .cummax()
    )

    data["drawdown"] = (
        data["equity"]
        / data["peak"]
        - 1
    )

    mdd = (
        data["drawdown"]
        .min()
    ) * 100


    # -------------------------
    # 거래 횟수
    # -------------------------

    trades = int(
        data["trade"]
        .sum()
    )


    return {
        "return": total_return,
        "mdd": mdd,
        "trades": trades
    }


# =========================
# 9. Train에서 Alpha 연구
# =========================

results = []


for alpha_type in [
    "momentum",
    "mean_reversion"
]:

    for lookback in lookbacks:

        result = backtest_alpha(
            train_df,
            lookback,
            alpha_type
        )

        results.append(
            {
                "alpha": alpha_type,
                "lookback": lookback,
                "return": result["return"],
                "mdd": result["mdd"],
                "trades": result["trades"]
            }
        )


# =========================
# 10. 결과표
# =========================

result_df = pd.DataFrame(
    results
)


print(
    "\n===== TRAIN ALPHA RESEARCH ====="
)

print(
    result_df.to_string(
        index=False
    )
)


# =========================
# 11. Alpha별 최고 전략
# =========================

momentum_results = (
    result_df[
        result_df["alpha"]
        == "momentum"
    ]
    .sort_values(
        by="return",
        ascending=False
    )
)


mean_reversion_results = (
    result_df[
        result_df["alpha"]
        == "mean_reversion"
    ]
    .sort_values(
        by="return",
        ascending=False
    )
)


best_momentum = (
    momentum_results.iloc[0]
)

best_mean_reversion = (
    mean_reversion_results.iloc[0]
)


# =========================
# 12. Test 검증
# =========================

momentum_test = backtest_alpha(
    test_df,
    int(
        best_momentum["lookback"]
    ),
    "momentum"
)


mean_reversion_test = backtest_alpha(
    test_df,
    int(
        best_mean_reversion[
            "lookback"
        ]
    ),
    "mean_reversion"
)


# =========================
# 13. 최종 출력
# =========================

print(
    "\n===== BEST MOMENTUM ====="
)

print(
    f"Lookback: "
    f"{int(best_momentum['lookback'])}h"
)

print(
    f"Train Return: "
    f"{best_momentum['return']:.2f}%"
)

print(
    f"Test Return: "
    f"{momentum_test['return']:.2f}%"
)

print(
    f"Test MDD: "
    f"{momentum_test['mdd']:.2f}%"
)

print(
    f"Test Trades: "
    f"{momentum_test['trades']}"
)


print(
    "\n===== BEST MEAN REVERSION ====="
)

print(
    f"Lookback: "
    f"{int(best_mean_reversion['lookback'])}h"
)

print(
    f"Train Return: "
    f"{best_mean_reversion['return']:.2f}%"
)

print(
    f"Test Return: "
    f"{mean_reversion_test['return']:.2f}%"
)

print(
    f"Test MDD: "
    f"{mean_reversion_test['mdd']:.2f}%"
)

print(
    f"Test Trades: "
    f"{mean_reversion_test['trades']}"
)