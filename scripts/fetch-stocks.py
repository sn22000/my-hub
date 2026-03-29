#!/usr/bin/env python3
"""
Stock Data Fetcher
Fetches stock/index data using yfinance for each Hub's ticker list.
Outputs JSON files with price, change, and sparkline data.
"""

import json
import os
import sys
from datetime import datetime, timezone

try:
    import yfinance as yf
except ImportError:
    print("Installing yfinance...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance", "-q"])
    import yfinance as yf

# --- Ticker configurations per Hub ---

HUBS = {
    "ai": {
        "file": "stocks-ai.json",
        "tickers": [
            {"symbol": "NVDA",  "name": "NVIDIA"},
            {"symbol": "MSFT",  "name": "Microsoft"},
            {"symbol": "GOOGL", "name": "Alphabet"},
            {"symbol": "META",  "name": "Meta"},
            {"symbol": "AMD",   "name": "AMD"},
            {"symbol": "PLTR",  "name": "Palantir"},
            {"symbol": "SMCI",  "name": "Super Micro"},
        ],
    },
    "finance": {
        "file": "stocks-finance.json",
        "tickers": [
            {"symbol": "JPM",   "name": "JPMorgan"},
            {"symbol": "GS",    "name": "Goldman Sachs"},
            {"symbol": "V",     "name": "Visa"},
            {"symbol": "BRK-B", "name": "Berkshire"},
            {"symbol": "BLK",   "name": "BlackRock"},
            {"symbol": "COIN",  "name": "Coinbase"},
            {"symbol": "MA",    "name": "Mastercard"},
        ],
    },
    "economics": {
        "file": "stocks-economics.json",
        "tickers": [
            {"symbol": "^GSPC",  "name": "S&P 500"},
            {"symbol": "^IXIC",  "name": "NASDAQ"},
            {"symbol": "^DJI",   "name": "Dow Jones"},
            {"symbol": "^TNX",   "name": "US 10Y Yield"},
            {"symbol": "GLD",    "name": "Gold ETF"},
            {"symbol": "USO",    "name": "Oil ETF"},
            {"symbol": "UUP",    "name": "US Dollar"},
        ],
    },
    "seo": {
        "file": "stocks-seo.json",
        "tickers": [
            {"symbol": "GOOGL", "name": "Alphabet"},
        ],
    },
    "galaxy": {
        "file": "stocks-galaxy.json",
        "tickers": [
            {"symbol": "RKLB",  "name": "Rocket Lab"},
            {"symbol": "BA",    "name": "Boeing"},
            {"symbol": "LMT",   "name": "Lockheed Martin"},
            {"symbol": "NOC",   "name": "Northrop Grumman"},
            {"symbol": "LHX",   "name": "L3Harris"},
            {"symbol": "IRDM",  "name": "Iridium"},
            {"symbol": "LUNR",  "name": "Intuitive Machines"},
        ],
    },
    "travel": {
        "file": "stocks-travel.json",
        "tickers": [
            {"symbol": "BKNG",   "name": "Booking.com"},
            {"symbol": "ABNB",   "name": "Airbnb"},
            {"symbol": "EXPE",   "name": "Expedia"},
            {"symbol": "DAL",    "name": "Delta Air"},
            {"symbol": "UAL",    "name": "United Air"},
            {"symbol": "MAR",    "name": "Marriott"},
            {"symbol": "HLT",    "name": "Hilton"},
        ],
    },
}


def fetch_ticker_data(symbol, name):
    """Fetch price data and sparkline for a single ticker."""
    print(f"  Fetching: {symbol} ({name})...")
    try:
        ticker = yf.Ticker(symbol)

        # Get 5-day history at 1h intervals for sparkline
        hist = ticker.history(period="5d", interval="1h")
        if hist.empty:
            # Fallback to daily
            hist = ticker.history(period="1mo", interval="1d")

        if hist.empty:
            print(f"    [WARN] No data for {symbol}")
            return None

        closes = hist["Close"].dropna().tolist()
        if len(closes) < 2:
            return None

        current = closes[-1]
        prev_close = closes[0]
        change = current - prev_close
        change_pct = (change / prev_close) * 100 if prev_close != 0 else 0

        # Normalize sparkline to 0-100 range for rendering
        min_val = min(closes)
        max_val = max(closes)
        val_range = max_val - min_val if max_val != min_val else 1
        sparkline = [round((v - min_val) / val_range * 100, 1) for v in closes]

        # Downsample sparkline to ~50 points for performance
        if len(sparkline) > 50:
            step = len(sparkline) / 50
            sparkline = [sparkline[int(i * step)] for i in range(50)]

        return {
            "symbol": symbol,
            "name": name,
            "price": round(current, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "high": round(max_val, 2),
            "low": round(min_val, 2),
            "sparkline": sparkline,
        }

    except Exception as e:
        print(f"    [WARN] Error fetching {symbol}: {e}")
        return None


def main():
    print("=== Stock Data Fetcher ===")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")

    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(out_dir, exist_ok=True)

    for hub_name, hub_config in HUBS.items():
        print(f"\n--- {hub_name.upper()} Hub ---")
        stocks = []

        for ticker_info in hub_config["tickers"]:
            data = fetch_ticker_data(ticker_info["symbol"], ticker_info["name"])
            if data:
                stocks.append(data)

        output = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "hub": hub_name,
            "stocks": stocks,
        }

        out_path = os.path.join(out_dir, hub_config["file"])
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"  -> {len(stocks)} tickers saved to {out_path}")

    print("\nDone!")


if __name__ == "__main__":
    main()
