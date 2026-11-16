import pandas as pd

data = {
    "coin": ["BTC", "ETH", "SOL"],
    "price": [65000, 1800, 150],
    "change": [2.5, -1.2, 4.8]
}

df = pd.DataFrame(data)

print(df)

print("\nPrice column")
print(df["price"])

print("\nAverage price")
print(df["price"].mean())