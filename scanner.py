import yfinance as yf
import pandas as pd
import requests
import os
from ta.momentum import RSIIndicator

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise Exception("Missing BOT_TOKEN or CHAT_ID in GitHub Secrets")

stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "TATACAP.NS"]

results = []

for stock in stocks:
    try:
        df = yf.download(stock, period="3mo", interval="1d", progress=False)

        if df is None or len(df) < 20:
            continue

        df["RSI"] = RSIIndicator(df["Close"], window=8).rsi()

        latest = df.iloc[-1]

        if (
            pd.isna(latest["Open"]) or
            pd.isna(latest["Close"]) or
            pd.isna(latest["RSI"])
        ):
            continue

        gain = ((latest["Close"] - latest["Open"]) / latest["Open"]) * 100

        print(
    stock,
    "Open:", latest["Open"],
    "Low:", latest["Low"],
    "Close:", latest["Close"],
    "RSI:", latest["RSI"],
    

        if (
            latest["Low"] >= latest["Open"] * 0.998
            and latest["RSI"] > 70
            and gain > 3.5
        ):
            results.append(
                f"{stock} | +{gain:.2f}% | RSI {latest['RSI']:.1f}"
            )

    except Exception as e:
        print(f"Error in {stock}: {e}")

message = "🚀 NSE Scan\n\n" + "\n".join(results) if results else "No stocks found"


url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

requests.post(url, json={
    "chat_id": CHAT_ID,
    "text": message
})
