#!/usr/bin/env python3
"""
Iran Metrics Dashboard - Data Fetcher
Pulls real-time data from Yahoo Finance, FRED, and Silicon Analysts APIs.
"""

import json
import os
from datetime import datetime
from pathlib import Path

import yfinance as yf
import requests

# Baseline values from February 27, 2026 (war start date)
BASELINE = {
    # Markets
    "sp500": 6877.17,
    "msci_index": 4556.35,
    "vix": 15.0,
    "treasury": 4.25,
    # Energy
    "brent": 67.87,
    "wti": 67.00,
    "henryhub": 3.15,
    "ttf": 31.00,
    "fuel": 2.98,
    # Sector ETFs (Feb 27, 2026 baseline prices)
    "xlk": 210.50,  # Technology
    "xle": 42.30,   # Energy
    "xlf": 48.20,   # Financials
    "xlv": 145.80,  # Health Care
    "xly": 195.40,  # Consumer Discretionary
    "xlp": 78.50,   # Consumer Staples
    "xli": 168.30,  # Industrials
    "xlb": 82.40,   # Materials
    "xlu": 68.90,   # Utilities
    "xlre": 42.10,  # Real Estate
    "xlc": 82.70,   # Communication Services
    # Commodities
    "gold": 2850.00,
    "copper": 4.25,
    "wheat": 575.00,
    # Consumer sentiment baseline
    "umcsent": 64.7,
    "inflation_1yr": 3.0,
    "inflation_5yr": 2.8,
}

SECTOR_ETFS = {
    "XLK": {"name": "Technology", "key": "xlk", "industries": "Semiconductors, Software, Hardware"},
    "XLE": {"name": "Energy", "key": "xle", "industries": "Oil & Gas, Energy Equipment"},
    "XLF": {"name": "Financials", "key": "xlf", "industries": "Banks, Insurance, Capital Markets"},
    "XLV": {"name": "Health Care", "key": "xlv", "industries": "Pharma, Biotech, Medical Devices"},
    "XLY": {"name": "Consumer Discretionary", "key": "xly", "industries": "Retail, Autos, Hotels"},
    "XLP": {"name": "Consumer Staples", "key": "xlp", "industries": "Food, Beverages, Household"},
    "XLI": {"name": "Industrials", "key": "xli", "industries": "Aerospace, Defense, Machinery"},
    "XLB": {"name": "Materials", "key": "xlb", "industries": "Chemicals, Metals, Mining"},
    "XLU": {"name": "Utilities", "key": "xlu", "industries": "Electric, Gas, Water"},
    "XLRE": {"name": "Real Estate", "key": "xlre", "industries": "REITs, Property Management"},
    "XLC": {"name": "Communication Services", "key": "xlc", "industries": "Media, Telecom, Entertainment"},
}

MSCI_CONVERSION_FACTOR = 24.24

def calc_change(current, baseline):
    """Calculate percentage change from baseline."""
    if baseline == 0:
        return 0
    return round(((current - baseline) / baseline) * 100, 2)

def fetch_yahoo_finance_data():
    """Fetch market data from Yahoo Finance."""
    print("Fetching Yahoo Finance data...")

    # Core market symbols
    symbols = {
        "^GSPC": "sp500",
        "URTH": "msci",
        "BZ=F": "brent",
        "CL=F": "wti",
        "NG=F": "henryhub",
        "^VIX": "vix",
        "^TNX": "treasury",
        "GC=F": "gold",
        "HG=F": "copper",
        "ZW=F": "wheat",
    }

    data = {}

    # Fetch core market data
    for symbol, name in symbols.items():
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.fast_info
            price = info.last_price if hasattr(info, 'last_price') else info.get('lastPrice', 0)

            if price and price > 0:
                if name == "msci":
                    index_value = price * MSCI_CONVERSION_FACTOR
                    baseline = BASELINE.get("msci_index", index_value)
                    data[name] = {
                        "value": round(index_value, 2),
                        "etf_price": round(price, 2),
                        "change_pct": calc_change(index_value, baseline),
                        "source": "Yahoo Finance (URTH)",
                        "live": True
                    }
                else:
                    baseline = BASELINE.get(name, price)
                    data[name] = {
                        "value": round(price, 2),
                        "change_pct": calc_change(price, baseline),
                        "source": "Yahoo Finance",
                        "live": True
                    }
                print(f"  {name}: {price:.2f} ({data[name]['change_pct']:+.2f}%)")
        except Exception as e:
            print(f"  Error fetching {name}: {e}")

    return data

def fetch_sector_etfs():
    """Fetch all 11 GICS sector ETFs with historical data."""
    print("\nFetching sector ETFs...")

    data = {"sectors": {}}

    for symbol, info in SECTOR_ETFS.items():
        try:
            ticker = yf.Ticker(symbol)
            fast_info = ticker.fast_info
            price = fast_info.last_price if hasattr(fast_info, 'last_price') else fast_info.get('lastPrice', 0)

            if price and price > 0:
                baseline = BASELINE.get(info["key"], price)
                change_pct = calc_change(price, baseline)

                # Fetch historical data (since war start: Feb 27, 2026)
                history = []
                try:
                    hist = ticker.history(start="2026-02-27", interval="1d")
                    if not hist.empty:
                        for date, row in hist.iterrows():
                            history.append({
                                "date": date.strftime("%Y-%m-%d"),
                                "close": round(row["Close"], 2),
                                "volume": int(row["Volume"]) if row["Volume"] else 0
                            })
                except Exception as e:
                    print(f"    Could not fetch history for {symbol}: {e}")

                # Get top holdings if available
                top_holdings = []
                try:
                    holdings = ticker.get_institutional_holders()
                    # For ETFs, try to get the actual holdings
                except:
                    pass

                data["sectors"][info["key"]] = {
                    "symbol": symbol,
                    "name": info["name"],
                    "industries": info["industries"],
                    "price": round(price, 2),
                    "baseline": baseline,
                    "change_pct": change_pct,
                    "live": True,
                    "history": history[-90:] if len(history) > 90 else history,  # Last 90 days
                    "week_change": calc_change(price, history[-5]["close"]) if len(history) >= 5 else 0,
                    "month_change": calc_change(price, history[-22]["close"]) if len(history) >= 22 else 0,
                }
                print(f"  {info['name']} ({symbol}): ${price:.2f} ({change_pct:+.2f}%) - {len(history)} days of history")
        except Exception as e:
            print(f"  Error fetching {symbol}: {e}")

    return data

def fetch_fred_data():
    """Fetch consumer sentiment and inflation expectations from FRED."""
    print("\nFetching FRED data...")

    # FRED API (free, but requires key for full access)
    # Using fallback values if no API key
    fred_key = os.environ.get("FRED_API_KEY")

    data = {
        "consumer_sentiment": {
            "value": 48.9,
            "change_pct": calc_change(48.9, BASELINE["umcsent"]),
            "source": "U of Michigan via FRED",
            "live": False,
            "note": "June 2026 preliminary"
        },
        "inflation_1yr": {
            "value": 4.6,
            "change_pct": round(4.6 - BASELINE["inflation_1yr"], 2),
            "source": "U of Michigan via FRED",
            "live": False,
            "unit": "percentage points"
        },
        "inflation_5yr": {
            "value": 3.4,
            "change_pct": round(3.4 - BASELINE["inflation_5yr"], 2),
            "source": "U of Michigan via FRED",
            "live": False,
            "unit": "percentage points"
        }
    }

    if fred_key:
        try:
            # Consumer Sentiment
            url = f"https://api.stlouisfed.org/fred/series/observations?series_id=UMCSENT&api_key={fred_key}&file_type=json&sort_order=desc&limit=1"
            response = requests.get(url, timeout=10)
            if response.ok:
                result = response.json()
                if result.get("observations"):
                    value = float(result["observations"][0]["value"])
                    data["consumer_sentiment"]["value"] = value
                    data["consumer_sentiment"]["change_pct"] = calc_change(value, BASELINE["umcsent"])
                    data["consumer_sentiment"]["live"] = True
                    print(f"  Consumer Sentiment: {value}")

            # 1-Year Inflation Expectations
            url = f"https://api.stlouisfed.org/fred/series/observations?series_id=MICH&api_key={fred_key}&file_type=json&sort_order=desc&limit=1"
            response = requests.get(url, timeout=10)
            if response.ok:
                result = response.json()
                if result.get("observations"):
                    value = float(result["observations"][0]["value"])
                    data["inflation_1yr"]["value"] = value
                    data["inflation_1yr"]["change_pct"] = round(value - BASELINE["inflation_1yr"], 2)
                    data["inflation_1yr"]["live"] = True
                    print(f"  1-Year Inflation Exp: {value}%")
        except Exception as e:
            print(f"  Error fetching FRED data: {e}")
    else:
        print("  No FRED API key, using cached values")

    return data

def fetch_silicon_analysts_data():
    """Fetch semiconductor supply chain data from Silicon Analysts API."""
    print("\nFetching semiconductor supply chain data...")

    data = {
        "semiconductor": {
            "supply_signals": [],
            "chip_costs": {},
            "hbm_market": {},
            "live": False
        }
    }

    try:
        # Market pulse / supply chain signals
        response = requests.get("https://siliconanalysts.com/api/v1/market-pulse", timeout=15)
        if response.ok:
            signals = response.json()
            # Get latest 5 supply chain signals
            if isinstance(signals, list):
                data["semiconductor"]["supply_signals"] = signals[:5]
                data["semiconductor"]["live"] = True
                print(f"  Got {len(signals[:5])} supply chain signals")

        # HBM market data
        response = requests.get("https://siliconanalysts.com/api/v1/hbm", timeout=15)
        if response.ok:
            hbm = response.json()
            data["semiconductor"]["hbm_market"] = hbm
            print(f"  Got HBM market data")

        # Wafer pricing
        response = requests.get("https://siliconanalysts.com/api/v1/foundry/wafer-pricing", timeout=15)
        if response.ok:
            wafer = response.json()
            data["semiconductor"]["wafer_pricing"] = wafer
            print(f"  Got wafer pricing data")

    except Exception as e:
        print(f"  Error fetching Silicon Analysts data: {e}")

    return data

def get_manual_data():
    """Return manually updated data for metrics without API access."""
    print("\nAdding manual data points...")

    return {
        "fuel": {
            "value": 4.24,
            "change_pct": calc_change(4.24, BASELINE["fuel"]),
            "source": "EIA/AAA",
            "live": False
        },
        "ttf": {
            "value": 48.75,
            "change_pct": calc_change(48.75, BASELINE["ttf"]),
            "source": "ICE Exchange",
            "live": False
        },
        "gdp": {
            "value": "2.5%",
            "change": "-0.2%",
            "source": "IMF",
            "live": False
        },
        "inflation": {
            "value": "3.8% - 6.1%",
            "change": "+1.1% to +3.3%",
            "source": "IMF/World Bank",
            "live": False
        },
        "trump_approval": {
            "value": -19.1,
            "change": "-6 pts",
            "source": "Silver Bulletin",
            "live": False,
            "url": "https://www.natesilver.net"
        },
        "iran_war_approval": {
            "value": -22.8,
            "change": "-9 pts",
            "source": "Aggregate Polling",
            "live": False
        },
        # Partisan sentiment (from U of M reports - manual update)
        "partisan_sentiment": {
            "democrat": {
                "sentiment": 28.5,
                "inflation_exp": 5.8,
                "direction": "down"
            },
            "republican": {
                "sentiment": 72.4,
                "inflation_exp": 3.1,
                "direction": "stable"
            },
            "independent": {
                "sentiment": 41.2,
                "inflation_exp": 5.2,
                "direction": "down"
            },
            "source": "U of Michigan Survey",
            "last_updated": "June 2026",
            "live": False
        },
        # Supply chain impacts (manual analysis)
        "supply_chain_impacts": {
            "helium": {
                "status": "critical",
                "change": "+180%",
                "impact": "Semiconductor manufacturing, MRI machines, aerospace",
                "notes": "Qatar supplies 30% of global high-purity helium; Strait of Hormuz closure disrupting"
            },
            "neon": {
                "status": "elevated",
                "change": "+45%",
                "impact": "Chip lithography",
                "notes": "Alternative sources from US/EU partially offsetting"
            },
            "shipping": {
                "status": "disrupted",
                "change": "+85%",
                "impact": "Container rates, delivery times",
                "notes": "Red Sea/Suez diversions adding 10-14 days to Asia-Europe routes"
            },
            "semiconductors": {
                "status": "constrained",
                "change": "Lead times +6 weeks",
                "impact": "Auto, consumer electronics, data centers",
                "notes": "Helium shortage affecting advanced node production"
            }
        },
        # Scenario projections
        "scenarios": {
            "baseline": {
                "name": "Limited Conflict",
                "probability": "45%",
                "oil_price": "$85-95",
                "inflation_impact": "+0.5-1.0%",
                "gdp_impact": "-0.1 to -0.3%",
                "duration": "3-6 months",
                "description": "Hormuz stays open, limited military engagement, diplomatic off-ramps pursued"
            },
            "escalation": {
                "name": "Hormuz Disruption",
                "probability": "35%",
                "oil_price": "$120-150",
                "inflation_impact": "+2.0-3.5%",
                "gdp_impact": "-0.8 to -1.5%",
                "duration": "6-12 months",
                "description": "30-60 day Strait closure, oil supply shock, global recession risk"
            },
            "severe": {
                "name": "Extended Conflict",
                "probability": "15%",
                "oil_price": "$150-200+",
                "inflation_impact": "+4.0-6.0%",
                "gdp_impact": "-2.0 to -3.5%",
                "duration": "12+ months",
                "description": "Prolonged military engagement, sustained supply disruption, stagflation"
            },
            "deescalation": {
                "name": "Diplomatic Resolution",
                "probability": "5%",
                "oil_price": "$70-80",
                "inflation_impact": "-0.5%",
                "gdp_impact": "+0.2%",
                "duration": "1-3 months",
                "description": "Ceasefire, sanctions relief framework, rapid normalization"
            }
        },
        # Industry impact analysis
        "industry_impacts": {
            "winners": [
                {"industry": "Defense/Aerospace", "etf": "XLI/ITA", "reason": "Increased military spending"},
                {"industry": "US Oil & Gas", "etf": "XLE", "reason": "Higher prices, domestic production"},
                {"industry": "Alternative Energy", "etf": "ICLN", "reason": "Accelerated transition"},
                {"industry": "Cybersecurity", "etf": "CIBR", "reason": "Elevated threat environment"},
                {"industry": "Gold/Precious Metals", "etf": "GLD", "reason": "Safe haven demand"}
            ],
            "losers": [
                {"industry": "Airlines", "etf": "JETS", "reason": "Fuel costs, route disruptions"},
                {"industry": "Autos", "etf": "CARZ", "reason": "Chip shortage, consumer pullback"},
                {"industry": "Retail", "etf": "XRT", "reason": "Consumer spending decline"},
                {"industry": "Shipping/Logistics", "etf": "IYT", "reason": "Route disruptions, costs"},
                {"industry": "Semiconductors", "etf": "SMH", "reason": "Helium shortage, demand uncertainty"}
            ]
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

def main():
    print("=" * 60)
    print("Iran Metrics Dashboard - Data Fetcher")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    all_data = {}

    # Fetch live market data
    all_data.update(fetch_yahoo_finance_data())

    # Fetch sector ETFs
    all_data.update(fetch_sector_etfs())

    # Fetch FRED consumer data
    all_data.update(fetch_fred_data())

    # Fetch semiconductor supply chain data
    all_data.update(fetch_silicon_analysts_data())

    # Add manual data
    all_data.update(get_manual_data())

    # Save to JSON
    save_data(all_data)

    print("\n" + "=" * 60)
    print("Data fetch complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
