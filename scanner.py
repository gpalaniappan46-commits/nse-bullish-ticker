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
        open_price = latest["Open"].item() if hasattr(latest["Open"], "item") else float(latest["Open"])
        close_price = latest["Close"].item() if hasattr(latest["Close"], "item") else float(latest["Close"])
        low_price = latest["Low"].item() if hasattr(latest["Low"], "item") else float(latest["Low"])
        rsi_value = latest["RSI"].item() if hasattr(latest["RSI"], "item") else float(latest["RSI"])

        gain = ((close_price - open_price) / open_price) * 100

        # Qualification logic
        if low_price >= open_price * 0.998 and rsi_value > 70 and gain > 3.5 and close_price > df["Close"].iloc[-2] and close_price > df["Close"].iloc[-3] :
            stock_info = (
                f"{stock} | Date {date} | "
                f"Open {open_price:.2f} | "
                f"Close {close_price:.2f} | "
                f"Low {low_price:.2f} | "
                f"RSI {rsi_value:.1f} | "
                f"Gain {gain:.2f}%"
            )
            qualified.append("✅ " + stock_info)

    except Exception as e:
        # Skip errors silently
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
