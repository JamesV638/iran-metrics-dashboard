#!/usr/bin/env python3
"""
Iran Metrics Dashboard - Data Fetcher
Pulls real-time data from various free APIs and saves to JSON for the dashboard.
Run this script periodically (cron job) or manually to update data.
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Try to import required libraries
try:
    import yfinance as yf
except ImportError:
    print("Installing yfinance...")
    os.system("pip3 install yfinance")
    import yfinance as yf

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system("pip3 install requests")
    import requests

# Baseline values from February 27, 2026
BASELINE = {
    "sp500": 6877.17,
    "msci_etf": 188.00,       # URTH ETF price baseline
    "msci_index": 4556.35,     # MSCI World Index baseline (ETF * ~24.24)
    "brent": 67.87,
    "wti": 67.00,
    "henryhub": 3.15,
    "vix": 15.0,
    "treasury": 4.25,
    "ttf": 31.00,
    "fuel": 2.98
}

# Conversion factor: MSCI World Index = URTH ETF Price * this factor
MSCI_CONVERSION_FACTOR = 24.24

def fetch_yahoo_finance_data():
    """Fetch financial data from Yahoo Finance."""
    print("Fetching Yahoo Finance data...")

    symbols = {
        "^GSPC": "sp500",      # S&P 500
        "URTH": "msci",         # iShares MSCI World ETF
        "BZ=F": "brent",        # Brent Crude Futures
        "CL=F": "wti",          # WTI Crude Futures
        "NG=F": "henryhub",     # Natural Gas Futures
        "^VIX": "vix",          # VIX Volatility Index
        "^TNX": "treasury"      # 10-Year Treasury Yield
    }

    data = {}

    for symbol, name in symbols.items():
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            price = info.last_price if hasattr(info, 'last_price') else info.get('lastPrice', 0)

            if price and price > 0:
                # Special handling for MSCI - convert ETF price to index value
                if name == "msci":
                    etf_price = price
                    index_value = etf_price * MSCI_CONVERSION_FACTOR
                    baseline = BASELINE.get("msci_index", index_value)
                    change_pct = ((index_value - baseline) / baseline) * 100

                    data[name] = {
                        "value": round(index_value, 2),
                        "etf_price": round(etf_price, 2),
                        "change_pct": round(change_pct, 2),
                        "source": "Yahoo Finance (URTH ETF converted)",
                        "live": True
                    }
                    print(f"  {name}: {index_value:.2f} (ETF: ${etf_price:.2f}, {change_pct:+.2f}%)")
                else:
                    baseline = BASELINE.get(name, price)
                    change_pct = ((price - baseline) / baseline) * 100

                    data[name] = {
                        "value": round(price, 2),
                        "change_pct": round(change_pct, 2),
                        "source": "Yahoo Finance",
                        "live": True
                    }
                    print(f"  {name}: ${price:.2f} ({change_pct:+.2f}%)")
            else:
                print(f"  {name}: No data available")
        except Exception as e:
            print(f"  Error fetching {name}: {e}")

    return data

def fetch_gas_prices():
    """Fetch US average gas prices from EIA API."""
    print("Fetching gas price data...")

    # EIA API - requires free API key from eia.gov
    # For demo, using estimated current value
    data = {
        "fuel": {
            "value": 4.24,
            "change_pct": round(((4.24 - BASELINE["fuel"]) / BASELINE["fuel"]) * 100, 2),
            "source": "EIA/AAA",
            "live": False
        }
    }

    # Try EIA API if key is available
    eia_key = os.environ.get("EIA_API_KEY")
    if eia_key:
        try:
            url = f"https://api.eia.gov/v2/petroleum/pri/gnd/data/?api_key={eia_key}&frequency=weekly&data[0]=value&facets[product][]=EPMRU&facets[duession][]=Y&sort[0][column]=period&sort[0][direction]=desc&length=1"
            response = requests.get(url, timeout=10)
            if response.ok:
                result = response.json()
                if result.get("response", {}).get("data"):
                    price = float(result["response"]["data"][0]["value"])
                    data["fuel"]["value"] = price
                    data["fuel"]["change_pct"] = round(((price - BASELINE["fuel"]) / BASELINE["fuel"]) * 100, 2)
                    data["fuel"]["live"] = True
                    print(f"  Gas price: ${price:.2f}")
        except Exception as e:
            print(f"  Error fetching EIA data: {e}")

    return data

def get_manual_data():
    """Return manually updated data for metrics without API access."""
    print("Adding manual data points...")

    return {
        "gdp": {
            "value": "2.5%",
            "change": "-0.2%",
            "source": "IMF World Economic Outlook",
            "live": False
        },
        "inflation": {
            "value": "3.8% - 6.1%",
            "change": "+1.1% to +3.3%",
            "source": "IMF/World Bank",
            "live": False
        },
        "ttf": {
            "value": 48.75,
            "change_pct": round(((48.75 - BASELINE["ttf"]) / BASELINE["ttf"]) * 100, 2),
            "source": "ICE Exchange",
            "live": False
        },
        "trump_approval": {
            "value": -19.1,
            "change": "-6 pts",
            "source": "FiveThirtyEight/RealClearPolitics",
            "live": False,
            "note": "Net approval rating"
        },
        "iran_war_approval": {
            "value": -22.8,
            "change": "-9 pts",
            "source": "Aggregate Polling",
            "live": False,
            "note": "Net approval for/against Iran conflict"
        }
    }

def save_data(data):
    """Save data to JSON file."""
    output_path = Path(__file__).parent / "data.json"

    full_data = {
        "last_updated": datetime.now().isoformat(),
        "baseline_date": "2026-02-27",
        "metrics": data
    }

    with open(output_path, "w") as f:
        json.dump(full_data, f, indent=2)

    print(f"\nData saved to {output_path}")
    return output_path

def main():
    print("=" * 50)
    print("Iran Metrics Dashboard - Data Fetcher")
    print(f"Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # Collect all data
    all_data = {}

    # Fetch live market data
    market_data = fetch_yahoo_finance_data()
    all_data.update(market_data)

    # Fetch gas prices
    gas_data = fetch_gas_prices()
    all_data.update(gas_data)

    # Add manual data
    manual_data = get_manual_data()
    all_data.update(manual_data)

    # Save to JSON
    save_data(all_data)

    print("\n" + "=" * 50)
    print("Data fetch complete!")
    print("=" * 50)

    return all_data

if __name__ == "__main__":
    main()
