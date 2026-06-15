import pandas as pd

df = pd.read_csv("EQUITY_L.csv")

symbols = df["SYMBOL"].astype(str) + ".NS"

symbols.to_csv("nse_symbols.csv", index=False, header=False)

print("nse_symbols.csv created successfully")
