import yfinance as yf
import pandas as pd
import requests
import os
from ta.momentum import RSIIndicator

BOT_TOKEN = os.environ["8872188056:AAEa4Xh-vji0KfCYjA4rLfUkT1tSPAVJlRk"]
CHAT_ID = os.environ["981639685"]

# START SIMPLE FIRST (we will upgrade later to full NSE list)
stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

results = []

for stock in stocks:
    df = yf.download(stock, period="3mo", interval="1d", progress=False)

    if len(df) < 20:
        continue

    df["RSI"] = RSIIndicator(df["Close"], window=14).rsi()

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    gain = ((latest["Close"] - prev["Close"]) / prev["Close"]) * 100

    if (
        latest["Low"] <= latest["Open"] * 1.001 and
        latest["RSI"] > 70 and
        gain > 4
    ):
        results.append(f"{stock} | {gain:.2f}% | RSI {latest['RSI']:.1f}")

message = "🚀 NSE Scan\n\n" + "\n".join(results) if results else "No stocks found"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

requests.post(url, json={
    "chat_id": CHAT_ID,
    "text": message
})
