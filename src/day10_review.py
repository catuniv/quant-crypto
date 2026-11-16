# import ccxt
# import pandas as pd
# import matplotlib.pyplot as plt

# exchange = ccxt.binance()

# ohlcv = exchange.fetch_ohlcv(
#     symbol = "BTC/USDT",
#     timeframe="1h",
#     limit=1000
# )

# df = pd.DataFrame(
#     ohlcv,
#     columns=[
#         "timestamp",
#         "open",
#         "high",
#         "low",
#         "close",
#         "volume"
#     ]
# )

# df["timestamp"] = pd.to_datetime(
#     df["timestamp"],
#     unit = "ms"
# )

# df["return"] = df["close"].pct_change()

# 직접 코딩 1
# import ccxt
# import pandas as pd
# import matplotlib.pyplot as plt

# exchange = ccxt.binance()

# ohlcv = exchange.fetch_ohlcv(
#     symbol="BTC/USDT",
#     timeframe="1h",
#     limit=1000
# )

# df = pd.DataFrame(
#     ohlcv,
#     columns=[
#         "timestamp",
#         "open",
#         "high",
#         "low",
#         "close",
#         "volume"
#     ]
# )

# df["timestamp"] = pd.to_datetime(
#     df["timestamp"],
#     unit="ms"
# )

# df["return"] = df["close"].pct_change()


# df["ma10"] = (
#     df["close"].rolling(window=10).mean()
# )

# df["ma30"] = (
#     df["close"].rolling(window=30).mean()
# )

# print(df.tail())



# 실전 과제
import ccxt
import pandas as pd

exchange = ccxt.binance()

ohlcv = exchange.fetch_ohlcv(
    symbol="BTC/USDT",
    timeframe="1h",
    limit=1000
)

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

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    unit="ms"
)

df["return"] = df["close"].pct_change()
df["signal"] = 0

df["MA10"] = (df["close"].rolling(window=10).mean())
df["MA30"] = (df["close"].rolling(window=30).mean())

df.loc[
    df["MA10"] > df["MA30"],
    "signal"
] = 1

print(
    df[
        [
            "timestamp",
            "close",
            "MA10",
            "MA30",
            "signal"
        ]
    ].tail(10)
)

df["strategy_return"] = (
    df["signal"].shift(1) * df["return"]
)

df["trade"] = (
    df["signal"].diff().abs()
)

fee_rate = 0.001
df["strategy_return_after_fee"] = (
    df["strategy_return"] - df["trade"] * fee_rate
)

df["equity"] = (
    1 + df["strategy_return_after_fee"].fillna(0)
).cumprod()

df["peak"] = (
    df["equity"].cummax()
)

df["drawdown"] = (
    df["equity"] / df["peak"] - 1
)

mdd = (
    df["drawdown"].min()
) * 100

total_return = (
    df["equity"].iloc[-1] -1
) * 100

print(f"Total Return: {total_return:.2f}%")
print(f"MDD: {mdd:.2f}%")




