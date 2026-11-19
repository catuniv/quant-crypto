import pandas as pd

df = pd.DataFrame({
    "coin": ["BTC", "ETH", "SOL", "XRP"],
    "return":[3.2, -1.5, 7.8, 2.0]
})

# 1. return sort ascending=False
sorted_df = df.sort_values("return", ascending=False)
print(sorted_df)
print()


# 2. return rank
df["rank"] = df["return"].rank(ascending=False)
print(df)
print()

# 3. Equal Score
df2 = pd.DataFrame({
    "coin": ["BTC", "ETH", "SOL", "XRP"],
    "return": [5, 5, 2, -1]
})

df2["rank"] = df2["return"].rank(ascending=False, method="min")
print(df2)
print()

