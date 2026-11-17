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


print("==== DATAFRAME ====")
print(df)

print("==== ONE COLUMN====")
print(df["price"])

print("==== TWO COLUMN ====")
print(df[["coin", "price"]])

print("==== SHAPE ====")
print(df.shape)

print("==== COLUMNS ====")
print(df.columns)

print("==== DTYPES ====")
print(df.dtypes)

print("==== INFO ====")
df.info()
