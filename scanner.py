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

stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "TATACAP.NS"]

qualified = []
all_results = []

for stock in stocks:
    try:
        df = yf.download(stock, period="3mo", interval="1d", progress=False)

        if df is None or len(df) < 20:
            all_results.append(f"{stock} | Error: Not enough data")
            continue

        df["RSI"] = RSIIndicator(df["Close"], window=8).rsi()
        latest = df.iloc[-1]
        date = latest.name.strftime("%d-%m-%Y")  # candle date

        if (
            pd.isna(latest["Open"]) or
            pd.isna(latest["Close"]) or
            pd.isna(latest["RSI"])
        ):
            all_results.append(f"{stock} | Error: Missing values")
            continue

        gain = ((latest["Close"] - latest["Open"]) / latest["Open"]) * 100

        stock_info = (
            f"{stock} | Date {date} | "
            f"Open {latest['Open']:.2f} | "
            f"Close {latest['Close']:.2f} | "
            f"Low {latest['Low']:.2f} | "
            f"RSI {latest['RSI']:.1f} | "
            f"Gain {gain:.2f}%"
        )

        if (
            latest["Low"] >= latest["Open"] * 0.998
            and latest["RSI"] > 70
            and gain > 3.5
        ):
            qualified.append("✅ " + stock_info)
            all_results.append("✅ " + stock_info)
        else:
            all_results.append("❌ " + stock_info)

    except Exception as e:
        all_results.append(f"{stock} | Error: {e}")

# Build Telegram message
scan_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
message = f"🚀 NSE Scan (Run at {scan_time})\n\n"

if qualified:
    message += "Qualified Stocks ✅\n" + "\n".join(qualified) + "\n\n"
else:
    message += "Qualified Stocks ✅\nNone found today\n\n"

message += "All Stocks (with prices)\n" + "\n".join(all_results)

# Send to Telegram
url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
requests.post(url, json={"chat_id": CHAT_ID, "text": message})
