import pandas as pd
import numpy as np

data = {
    "coin": [
        "BTC",
        "ETH",
        "SOL",
        "XRP"
    ],

    "price": [
        65000,
        1800,
        np.nan,
        1
    ],

    "change": [
        2.5,
        np.nan,
        4.8,
        -0.5
    ]
}

df = pd.DataFrame(data)

print("\n==== NaN 행 제거 ====")
dropped_df = (
    df.dropna()
)

print(dropped_df)

print("\n==== ISNA ====")
print(df.isna())

print("\n==== NA COUNT ====")
print(df.isna().sum())

print("\n==== FILLNA ====")
filled_df = (
    df.fillna(0)
)

print(filled_df)

print("\n==== 특정 열만 채우기 ====")
df["change"] = (
    df["change"].fillna(0)
)

print(df)

