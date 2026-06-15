import yfinance as yf
import pandas as pd
import requests
import os
from ta.momentum import RSIIndicator
from datetime import datetime

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise Exception("Missing BOT_TOKEN or CHAT_ID in GitHub Secrets")

# Load NSE symbols from your file
with open("nse_symbols.csv") as f:
    stocks = [line.strip() for line in f if line.strip()]

qualified = []

for stock in stocks:
    try:
        df = yf.download(stock, period="3mo", interval="1d", progress=False)

        if df is None or len(df) < 20:
            continue

        # Ensure Close is a Series
        if isinstance(df["Close"], pd.DataFrame):
            df["Close"] = df["Close"].iloc[:, 0]

        df["RSI"] = RSIIndicator(df["Close"].squeeze(), window=8).rsi()
        latest = df.iloc[-1]
        date = latest.name.strftime("%d-%m-%Y")

        # Convert values to scalars safely
        open_price = float(latest["Open"])
        close_price = float(latest["Close"])
        low_price = float(latest["Low"])
        high_price = float(latest["High"])
        rsi_value = float(latest["RSI"])

        gain = ((close_price - open_price) / open_price) * 100

        # Qualification logic (matches your scanner)
        if (
            rsi_value > 75
            and close_price > df["Close"].iloc[-2]
            and close_price > df["Close"].iloc[-3]
            and close_price > open_price
        ):
            stock_info = (
                f"{stock} | Date {date} | "
                f"Open {open_price:.2f} | "
                f"Close {close_price:.2f} | "
                f"Low {low_price:.2f} | "
                f"High {high_price:.2f} | "
                f"RSI {rsi_value:.1f} | "
                f"Gain {gain:.2f}%"
            )
            qualified.append("✅ " + stock_info)

    except Exception:
        continue

# Build Telegram message
scan_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
message = f"🚀 NSE Scan (Run at {scan_time})\n\n"
message += "Legend: ✅ Qualified\n\n"

if qualified:
    message += "Qualified Stocks\n" + "\n".join(qualified)
else:
    message += "No stocks qualified today"

# Send to Telegram
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
requests.post(url, json={"chat_id": CHAT_ID, "text": message})
