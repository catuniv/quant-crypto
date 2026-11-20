import pandas as pd

df = pd.DataFrame({
    "coin": ["BTC", "ETH", "BTC", "ETH", "SOL", "SOL"],
    "return": [3, 2, -1, 4, 5, -2],
    "volume": [100, 200, 150, 300, 120, 180]
})

print(df)