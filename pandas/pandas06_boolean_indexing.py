import pandas as pd

data = {
    "coin": [
        "BTC",
        "ETH",
        "XRP",
        "SOL"
    ],

    "price": [
        65000,
        1800,
        150,
        10
    ],

    "change": [
        1.2,
        -1.5,
        2.3,
        9.8
    ]
}

df = pd.DataFrame(data)

print(df["price"] > 1000)
print()

print(df[df["price"] > 1000])
print()

print((df["price"] > 100) & (df["change"] > 0))
print()

print((df["price"] < 100) | (df["change"] > 0))


df["signal"] = 0

df.loc[
    df["change"] > 0,
    "signal"
] = 1

print(df)