# Iran Metrics Dashboard - Partner Briefing

## Executive Summary

This dashboard tracks key economic, market, and political indicators to monitor the impact of the Iran situation. It compares current values against a baseline date of **February 27, 2026**.

---

## How It Works

### Architecture
```
[Data Sources] --> [Python Script] --> [data.json] --> [HTML Dashboard]
                         |
                   Runs every hour
                   via macOS automation
```

### Components
1. **fetch_data.py** - Python script that pulls live market data from APIs
2. **data.json** - Stores the latest data in JSON format
3. **index.html** - Interactive dashboard that reads from data.json
4. **LaunchAgent** - macOS service that runs the fetch script hourly (persists through restarts)

### Update Schedule
- **Live data (markets):** Fetched every hour automatically
- **Manual data (polling, GDP):** Updated manually as new data is released

---

## Data Sources & Reliability Assessment

### LIVE DATA (Automated - HIGH Reliability)

| Metric | Source | Ticker | Update Frequency | Reliability |
|--------|--------|--------|------------------|-------------|
| **S&P 500** | Yahoo Finance | ^GSPC | Real-time | HIGH |
| **MSCI World Index** | Yahoo Finance | URTH ETF* | Real-time | HIGH |
| **Brent Crude Oil** | Yahoo Finance | BZ=F | Real-time | HIGH |
| **WTI Crude Oil** | Yahoo Finance | CL=F | Real-time | HIGH |
| **Henry Hub Natural Gas** | Yahoo Finance | NG=F | Real-time | HIGH |
| **VIX (Volatility)** | Yahoo Finance/CBOE | ^VIX | Real-time | HIGH |
| **US 10-Year Treasury** | Yahoo Finance | ^TNX | Real-time | HIGH |

*MSCI World uses URTH ETF price multiplied by 24.24 conversion factor to approximate index value

### MANUAL DATA (Requires Updates)

| Metric | Source | Update Frequency | Reliability | Notes |
|--------|--------|------------------|-------------|-------|
| **Global GDP Growth** | IMF World Economic Outlook | Quarterly | HIGH | Gold standard for economic projections |
| **Global Inflation** | IMF/World Bank | Quarterly | HIGH | Aggregate from major economies |
| **Dutch TTF Gas** | ICE Exchange | Daily | HIGH | European gas benchmark; could be automated with ICE API |
| **US Fuel Prices** | AAA/EIA | Weekly | HIGH | Can be automated with free EIA API key |
| **Trump Net Approval** | FiveThirtyEight/RCP | Daily | MEDIUM-HIGH | Polling aggregates have methodological limitations |
| **Iran War Approval** | Aggregate Polling | Weekly | MEDIUM | Question wording varies across polls |

---

## Reliability Considerations

### High Confidence Data (Live Markets)
- **Source:** Yahoo Finance API (free, widely used)
- **Why it's reliable:** Direct feed from exchanges; same data used by financial institutions
- **Limitations:** Brief outages possible; data delayed ~15 minutes for some securities
- **Backup options:** Alpha Vantage, IEX Cloud, or Bloomberg Terminal for institutional grade

### Medium-High Confidence Data (Polling)
- **Source:** FiveThirtyEight, RealClearPolitics aggregates
- **Why it's reliable:** Aggregates multiple polls, reduces individual poll bias
- **Limitations:**
  - Polling methodology varies
  - Sample sizes differ
  - Question wording affects responses
  - "Net approval" = % approve - % disapprove

### Context on Specific Metrics

**VIX (Fear Gauge)**
- Measures expected S&P 500 volatility over next 30 days
- Below 15 = low fear, 15-25 = normal, above 25 = elevated fear
- Spikes correlate with geopolitical events

**10-Year Treasury Yield**
- Falls during "flight to safety" when investors seek safe assets
- Rises when confidence returns
- Key indicator of market stress perception

**Dutch TTF Hub**
- European natural gas benchmark
- Highly sensitive to Middle East/Russia supply disruptions
- Measured in EUR/MWh

---

## Setting Up for Partners

### Option 1: Share the Dashboard Link (Simplest)
- Host the dashboard on an internal web server
- Partners access via browser; no installation needed

### Option 2: Local Installation (Full Control)

**Requirements:**
- macOS computer
- Python 3 installed
- Internet connection

**Setup Steps:**
1. Copy the `iran-metrics-dashboard` folder to their Desktop
2. Double-click `setup_automation.command` to enable hourly updates
3. Grant Full Disk Access when prompted (System Settings > Privacy & Security)
4. Double-click `Iran Dashboard.app` to view

**Maintenance:**
- Manual data points need updating (edit fetch_data.py or data.json)
- Check logs in `logs/` folder if data stops updating

### Option 3: Cloud Deployment (Recommended for Firm-Wide)
- Deploy to AWS/Azure/GCP
- Use cron job for scheduled updates
- Access via web browser from anywhere
- No local installation required

---

## Updating Manual Data

To update polling or GDP data, edit `fetch_data.py` in the `get_manual_data()` function:

```python
"trump_approval": {
    "value": -19.1,      # Update this number
    "change": "-6 pts",   # Change from baseline
    ...
}
```

Or directly edit `data.json` with current values.

---

## Recommendations for Production Use

1. **Add EIA API Key** - Free registration at eia.gov for automated gas prices
2. **Consider Bloomberg/Reuters** - For institutional reliability guarantees
3. **Add Monitoring** - Alert when data fetch fails
4. **Backup Data Sources** - Alpha Vantage or IEX Cloud as fallback APIs
5. **Version Control** - Track changes to manual data updates

---

## Support & Troubleshooting

**Data not updating?**
- Check `logs/fetch_error.log` for errors
- Verify Full Disk Access is granted to Python
- Run `python3 fetch_data.py` manually to test

**Markets showing stale data?**
- Markets only update during trading hours (9:30 AM - 4:00 PM ET weekdays)
- Weekend/holiday data will show Friday's close

**Questions?**
Contact: [Your IT/Dashboard Administrator]

---

*Last updated: June 2026*
