import yfinance as yf
import pandas as pd
import requests
import os
from ta.momentum import RSIIndicator

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

results = []

for stock in stocks:
    try:
        df = yf.download(stock, period="3mo", interval="1d", progress=False)

        if df is None or len(df) < 20:
            continue

        df["RSI"] = RSIIndicator(df["Close"], window=14).rsi()

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        if pd.isna(latest["RSI"]):
            continue

        gain = ((latest["Close"] - prev["Close"]) / prev["Close"]) * 100

        if (
            latest["Low"] <= latest["Open"] * 1.001
            and latest["RSI"] > 70
            and gain > 4
        ):
            results.append(f"{stock} | {gain:.2f}% | RSI {latest['RSI']:.1f}")

    except Exception as e:
        print(f"Error in {stock}: {e}")

message = "🚀 NSE Scan\n\n" + "\n".join(results) if results else "No stocks found"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

requests.post(url, json={
    "chat_id": CHAT_ID,
    "text": message
})
