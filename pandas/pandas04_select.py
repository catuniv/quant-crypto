import pandas as pd

data = {
    "coin":[
        "BTC",
        "ETH",
        "SOL",
        "XRP"
    ],

    "price":[
        65000,
        1800,
        150,
        0.7
    ],

    "change":[
        2.5,
        -1.2,
        4.8,
        -0.5
    ]
}

df = pd.DataFrame(data)
df["price"] = df["price"].astype(int)


print("==== ORIGINAL ====")
print(df)

print("\n==== FIRST ROW ====")
print(df.iloc[0])

print("\n==== THIRD ROW ====")
print(df.iloc[2])

print("\n==== FIRST TOW ROW ====")
print(df.iloc[0:2])

print("\n==== BTC PRICE ====")
print(df.iloc[0]["price"])

