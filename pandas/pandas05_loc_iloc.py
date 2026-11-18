import pandas as pd

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
        150,
        1
    ],

    "change": [
        2.5,
        -1.2,
        4.8,
        -0.5
    ]
}

df = pd.DataFrame(data,
            index=[
                "A",
                "B",
                "C",
                "D"
            ]
)


print(df.loc["A"])
print()

print(df.loc["A", "price"])
print()

print(df.loc["A":"C"])
print()

print(df.loc["A":"C", ["coin", "price"]])
print()