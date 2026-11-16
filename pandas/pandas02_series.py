import pandas as pd

prices = pd.Series(
    [65000, 1800, 150],
    index=["BTC", "ETH", "SOL"]
)

print("=== Series ===")
print(prices)

print("\n=== BTC Price ===")
print(prices["BTC"])

print("\n=== First Value ===")
print(prices.iloc[0])

print("\n=== X2 ===")
print(prices * 2)

print("\n=== Over 1000 ===")
print(prices > 1000)

print("\n=== Filtered ===")
print(prices[prices > 1000])

print("\n=== Statistics ===")
print("Mean:", prices.mean())
print("Max:", prices.max())
print("Min:", prices.min())
print("Sum:", prices.sum())