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
    # Supply chain commodities (Feb 27, 2026 baselines)
    "aluminum": 2450.00,
    "nickel": 16500.00,
    "zinc": 2650.00,
    "uranium_etf": 28.50,    # URA ETF
    "lithium_etf": 42.00,    # LIT ETF
    "shipping_etf": 8.50,    # BDRY - Breakwave Dry Bulk Shipping
    "fertilizer": 48.00,     # MOS - Mosaic Company
    "rare_earth": 68.00,     # REMX - Rare Earth ETF
    "steel": 78.00,          # SLX - Steel ETF
    "agriculture": 22.50,    # DBA - Agriculture ETF
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
                            close_val = row["Close"]
                            vol_val = row["Volume"]
                            # Skip NaN values
                            if close_val != close_val:  # NaN check
                                continue
                            history.append({
                                "date": date.strftime("%Y-%m-%d"),
                                "close": round(float(close_val), 2),
                                "volume": int(vol_val) if vol_val == vol_val and vol_val else 0
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

def fetch_supply_chain_commodities():
    """Fetch supply chain related commodities and ETFs."""
    print("\nFetching supply chain commodities...")

    # Supply chain symbols - mix of futures and ETFs as proxies
    symbols = {
        "ALI=F": {"name": "Aluminum", "key": "aluminum", "unit": "$/ton", "category": "metals"},
        "^SPGSIN": {"name": "Nickel", "key": "nickel", "unit": "$/ton", "category": "metals"},
        "URA": {"name": "Uranium (ETF)", "key": "uranium_etf", "unit": "$", "category": "energy"},
        "LIT": {"name": "Lithium (ETF)", "key": "lithium_etf", "unit": "$", "category": "battery"},
        "BDRY": {"name": "Dry Bulk Shipping", "key": "shipping_etf", "unit": "$", "category": "shipping"},
        "MOS": {"name": "Fertilizers (Mosaic)", "key": "fertilizer", "unit": "$", "category": "agriculture"},
        "REMX": {"name": "Rare Earth Metals", "key": "rare_earth", "unit": "$", "category": "metals"},
        "SLX": {"name": "Steel", "key": "steel", "unit": "$", "category": "metals"},
        "DBA": {"name": "Agriculture", "key": "agriculture", "unit": "$", "category": "agriculture"},
        "SOYB": {"name": "Soybeans (ETF)", "key": "soybeans", "unit": "$", "category": "agriculture"},
        "CORN": {"name": "Corn (ETF)", "key": "corn", "unit": "$", "category": "agriculture"},
        "PALL": {"name": "Palladium", "key": "palladium", "unit": "$", "category": "metals"},
        "PPLT": {"name": "Platinum", "key": "platinum", "unit": "$", "category": "metals"},
    }

    data = {"supply_chain_live": {}}

    for symbol, info in symbols.items():
        try:
            ticker = yf.Ticker(symbol)
            fast_info = ticker.fast_info
            price = fast_info.last_price if hasattr(fast_info, 'last_price') else fast_info.get('lastPrice', 0)

            if price and price > 0:
                baseline = BASELINE.get(info["key"], price)
                change_pct = calc_change(price, baseline)

                # Determine status based on change from baseline
                if change_pct > 75:
                    status = "critical"
                elif change_pct > 35:
                    status = "elevated"
                elif change_pct > 15:
                    status = "stressed"
                elif change_pct > -15:
                    status = "stable"
                elif change_pct > -40:
                    status = "below_baseline"
                else:
                    status = "below_baseline"

                data["supply_chain_live"][info["key"]] = {
                    "symbol": symbol,
                    "name": info["name"],
                    "category": info["category"],
                    "price": round(price, 2),
                    "baseline": baseline,
                    "change_pct": change_pct,
                    "status": status,
                    "unit": info["unit"],
                    "live": True
                }
                print(f"  {info['name']}: {price:.2f} ({change_pct:+.2f}%) - {status}")
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
        # Peace deal status
        "peace_deal": {
            "status": "Framework Agreed",
            "announced": "June 14, 2026",
            "signing_date": "June 19, 2026",
            "location": "Switzerland",
            "key_terms": [
                "60-day ceasefire extension",
                "Strait of Hormuz reopening",
                "US naval blockade lifted",
                "Lebanon hostilities ended"
            ],
            "unresolved": [
                "Nuclear enrichment limits",
                "Highly enriched uranium stockpiles",
                "Sanctions relief timeline",
                "Frozen asset releases"
            ],
            "mediators": ["Pakistan", "Oman"],
            "source": "CNBC, Al Jazeera, NPR",
            "live": False
        },
        # Consumer sentiment comprehensive data (from U of M reports - manual update)
        # Removed old partisan_sentiment - now in consumer_data
        "consumer_data": {
            "overall_sentiment": {
                "value": 48.9,
                "baseline": 64.7,
                "change_pct": -24.4,
                "historic_low": 44.8,
                "historic_low_date": "May 2026"
            },
            "current_conditions": {
                "value": 56.2,
                "baseline": 72.3,
                "change_pct": -22.3,
                "description": "Assessment of current financial situation"
            },
            "expectations": {
                "value": 44.1,
                "baseline": 59.8,
                "change_pct": -26.3,
                "description": "Expectations for economy over next year"
            },
            "buying_conditions": {
                "durables": {
                    "value": 82,
                    "baseline": 121,
                    "assessment": "Poor",
                    "reason": "High prices and uncertainty"
                },
                "vehicles": {
                    "value": 78,
                    "baseline": 115,
                    "assessment": "Poor",
                    "reason": "Chip shortages, high prices"
                },
                "homes": {
                    "value": 45,
                    "baseline": 62,
                    "assessment": "Very Poor",
                    "reason": "High rates and prices"
                }
            },
            "inflation_expectations": {
                "one_year": {
                    "value": 4.6,
                    "baseline": 3.0,
                    "change": 1.6
                },
                "five_year": {
                    "value": 3.4,
                    "baseline": 2.8,
                    "change": 0.6
                }
            },
            "gas_price_impact": {
                "current_price": 4.24,
                "baseline_price": 2.98,
                "pct_increase": 42.3,
                "monthly_cost_increase": 85,
                "description": "Average household paying $85/month more for gas"
            },
            "by_party": {
                "democrat": {
                    "sentiment": 28.5,
                    "inflation_exp_1yr": 5.8,
                    "change_from_baseline": -38.2,
                    "direction": "down",
                    "economic_outlook": "Very Pessimistic"
                },
                "republican": {
                    "sentiment": 72.4,
                    "inflation_exp_1yr": 3.1,
                    "change_from_baseline": +8.5,
                    "direction": "up",
                    "economic_outlook": "Optimistic"
                },
                "independent": {
                    "sentiment": 41.2,
                    "inflation_exp_1yr": 5.2,
                    "change_from_baseline": -28.4,
                    "direction": "down",
                    "economic_outlook": "Pessimistic"
                }
            },
            "key_concerns": [
                {"concern": "Gas prices", "pct_citing": 68},
                {"concern": "Inflation/prices", "pct_citing": 54},
                {"concern": "War/conflict", "pct_citing": 41},
                {"concern": "Job security", "pct_citing": 23},
                {"concern": "Interest rates", "pct_citing": 19}
            ],
            "spending_intentions": {
                "cut_discretionary": 58,
                "delay_major_purchases": 64,
                "reduce_travel": 52,
                "switch_to_cheaper_brands": 47
            },
            "source": "U of Michigan Survey of Consumers",
            "last_updated": "June 2026",
            "next_release": "June 28, 2026",
            "live": False
        },
        # Supply chain impacts (manual analysis for non-tradeable commodities)
        # UPDATED June 16, 2026: Based on actual market data and news
        "supply_chain_manual": {
            "helium": {
                "status": "critical",
                "change": "+40-100%",
                "impact": "Semiconductor manufacturing, MRI machines, aerospace, fiber optics",
                "notes": "STILL CRITICAL: Airgas at 50% allocation, declared force majeure. Recovery will take YEARS not weeks. Qatar production offline. Russia/Algeria cannot fill gap. No substitutes exist for advanced chip manufacturing.",
                "affected_industries": ["Semiconductors", "Healthcare", "Aerospace", "Telecom"],
                "live": False
            },
            "strait_of_hormuz": {
                "status": "reopening",
                "change": "Opening June 19",
                "impact": "20% of global oil, 25% of LNG transits",
                "notes": "Peace deal signed June 14. Formal reopening June 19. Oil down 5% on news. Full normalization depends on deal implementation.",
                "affected_industries": ["Energy", "Shipping", "All sectors"],
                "live": False
            },
            "container_shipping": {
                "status": "stressed",
                "change": "+25-40% above pre-crisis",
                "impact": "Container rates, delivery times, inventory costs",
                "notes": "Red Sea PARTIALLY reopening. Some carriers resuming Suez routes. But rates still 25-40% elevated, Cape diversions still adding 10-14 days. June seeing rate spike due to early peak season.",
                "affected_industries": ["Retail", "Manufacturing", "Auto"],
                "live": False
            },
            "oil_supply": {
                "status": "falling",
                "change": "-22.9% this month",
                "impact": "Global energy prices, inflation",
                "notes": "Brent at $81.55, down from ~$104 peak. Dropped 5% on peace deal. War premium unwinding. If deal holds, could reach $75-80.",
                "affected_industries": ["Energy", "Transport", "Manufacturing"],
                "live": False
            },
            "petrochemicals": {
                "status": "elevated",
                "change": "+30-40%",
                "impact": "Plastics, packaging, synthetic materials",
                "notes": "Still elevated but easing with oil prices. Feedstock costs declining. Full normalization depends on sustained Hormuz access.",
                "affected_industries": ["Packaging", "Consumer Goods", "Construction"],
                "live": False
            },
            "ammonia": {
                "status": "elevated",
                "change": "+50-60%",
                "impact": "Fertilizer production, food prices",
                "notes": "Still elevated. Natural gas prices easing but Middle East exports not fully restored. Food inflation risk remains.",
                "affected_industries": ["Agriculture", "Food"],
                "live": False
            },
            "neon": {
                "status": "elevated",
                "change": "+45%",
                "impact": "Chip lithography, laser manufacturing",
                "notes": "Less affected by Hormuz. US/EU alternative sources ramping but not at full capacity. Prices holding steady.",
                "affected_industries": ["Semiconductors", "Lasers"],
                "live": False
            },
            "automotive_parts": {
                "status": "constrained",
                "change": "Lead times +3-4 weeks",
                "impact": "Vehicle production, EV batteries",
                "notes": "Helium shortage still constraining chip supply. Shipping improving but not normalized. Battery materials (lithium +100%) still critical.",
                "affected_industries": ["Auto", "EV"],
                "live": False
            }
        },
        # Scenario projections - UPDATED June 15, 2026 for peace deal
        "scenarios": {
            "deescalation": {
                "name": "Peace Deal Holds",
                "probability": "55%",
                "oil_price": "$70-80",
                "inflation_impact": "-0.5 to -1.0%",
                "gdp_impact": "+0.2 to +0.4%",
                "duration": "Resolved",
                "description": "June 19 signing holds. Hormuz open, sanctions relief phased in, nuclear talks continue. Markets normalize over 2-3 months."
            },
            "baseline": {
                "name": "Partial Resolution",
                "probability": "30%",
                "oil_price": "$80-90",
                "inflation_impact": "+0.3-0.5%",
                "gdp_impact": "-0.1%",
                "duration": "3-6 months",
                "description": "Deal signed but implementation delayed. Nuclear issues unresolved. Reduced but ongoing uncertainty."
            },
            "escalation": {
                "name": "Deal Collapse",
                "probability": "12%",
                "oil_price": "$100-120",
                "inflation_impact": "+1.5-2.5%",
                "gdp_impact": "-0.5 to -1.0%",
                "duration": "6-12 months",
                "description": "Hardliners derail deal. Hostilities resume. Hormuz re-closed. Return to conflict scenario."
            },
            "severe": {
                "name": "Major Escalation",
                "probability": "3%",
                "oil_price": "$150+",
                "inflation_impact": "+4.0-6.0%",
                "gdp_impact": "-2.0 to -3.5%",
                "duration": "12+ months",
                "description": "Deal rejected, expanded military engagement, full regional war. Least likely given current momentum."
            }
        },
        # Industry impact analysis - UPDATED June 15 for peace deal
        "industry_impacts": {
            "winners": [
                {"industry": "Airlines", "etf": "JETS", "reason": "Fuel costs dropping, routes reopening"},
                {"industry": "Shipping/Logistics", "etf": "IYT", "reason": "Hormuz open, rates normalizing"},
                {"industry": "Consumer Discretionary", "etf": "XLY", "reason": "Gas prices falling, confidence rising"},
                {"industry": "Semiconductors", "etf": "SMH", "reason": "Helium supply resuming from Qatar"},
                {"industry": "Retail", "etf": "XRT", "reason": "Consumer spending to recover"}
            ],
            "losers": [
                {"industry": "Defense/Aerospace", "etf": "ITA", "reason": "War premium fading, peace reducing urgency"},
                {"industry": "US Oil & Gas", "etf": "XLE", "reason": "Oil prices falling on peace deal"},
                {"industry": "Gold/Precious Metals", "etf": "GLD", "reason": "Safe haven demand declining"},
                {"industry": "Alternative Energy", "etf": "ICLN", "reason": "Oil price drop reduces urgency"},
                {"industry": "Cybersecurity", "etf": "CIBR", "reason": "Threat premium easing"}
            ]
        }
    }

import math

def clean_for_json(obj):
    """Recursively clean NaN and Inf values from data."""
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(item) for item in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj

def save_data(data):
    """Save data to JSON file."""
    output_path = Path(__file__).parent / "data.json"

    full_data = {
        "last_updated": datetime.now().isoformat(),
        "baseline_date": "2026-02-27",
        "metrics": clean_for_json(data)
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

    # Fetch supply chain commodities
    all_data.update(fetch_supply_chain_commodities())

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
