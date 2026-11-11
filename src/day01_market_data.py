import ccxt
import pandas as pd
import matplotlib.pyplot as plt

exchange = ccxt.binance()

ohlcv = exchange.fetch_ohlcv(
    symbol="BTC/USDT",
    timeframe="1h",
    limit=500
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

print(df.head())
print()
print(df.tail())

df.to_csv(
    "data/btc_usdt_1h.csv",
    index=False
)

plt.figure(figsize=(12, 5))
plt.plot(df["timestamp"], df["close"])

plt.title("BTC/USDT Price")
plt.xlabel("Time")
plt.ylabel("Price")
plt.grid()

plt.show()