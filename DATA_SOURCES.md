# Iran Metrics Dashboard - Data Sources & Reliability Assessment

## Overview
This document details where each metric is sourced from and provides a reliability assessment for partner review.

---

## LIVE DATA (Automated via Yahoo Finance API)

### 1. S&P 500 Index
- **Ticker:** ^GSPC
- **Source:** Yahoo Finance API
- **Update Frequency:** Real-time during market hours
- **Reliability:** HIGH
- **Notes:** Direct index data, highly reliable and widely used

### 2. Global Equities (MSCI World Index)
- **Ticker:** URTH (iShares MSCI World ETF)
- **Source:** Yahoo Finance API (converted to index value)
- **Update Frequency:** Real-time during market hours
- **Reliability:** HIGH
- **Notes:** ETF price × 24.24 conversion factor approximates MSCI World Index value. The ETF closely tracks the index.

### 3. Brent Crude Oil
- **Ticker:** BZ=F
- **Source:** Yahoo Finance API (Futures)
- **Update Frequency:** Real-time during trading hours
- **Reliability:** HIGH
- **Notes:** Front-month Brent futures contract, standard industry benchmark

### 4. WTI Crude Oil
- **Ticker:** CL=F
- **Source:** Yahoo Finance API (Futures)
- **Update Frequency:** Real-time during trading hours
- **Reliability:** HIGH
- **Notes:** Front-month WTI futures contract, US oil benchmark

### 5. Henry Hub Natural Gas
- **Ticker:** NG=F
- **Source:** Yahoo Finance API (Futures)
- **Update Frequency:** Real-time during trading hours
- **Reliability:** HIGH
- **Notes:** Front-month natural gas futures, US benchmark

### 6. VIX (Volatility Index)
- **Ticker:** ^VIX
- **Source:** Yahoo Finance API (CBOE data)
- **Update Frequency:** Real-time during market hours
- **Reliability:** HIGH
- **Notes:** Official CBOE VIX index, measures S&P 500 implied volatility ("fear gauge")

### 7. US 10-Year Treasury Yield
- **Ticker:** ^TNX
- **Source:** Yahoo Finance API
- **Update Frequency:** Real-time during market hours
- **Reliability:** HIGH
- **Notes:** Benchmark US government bond yield, key indicator for market stress

---

## MANUAL DATA (Updated from official sources)

### 8. Global GDP Growth 2026
- **Source:** IMF World Economic Outlook
- **Update Frequency:** Quarterly (April, July, October, January)
- **Reliability:** HIGH
- **Notes:** IMF is the gold standard for global economic projections. Updates typically lag 1-2 weeks after publication.
- **How to Update:** Check imf.org/en/Publications/WEO for latest projections

### 9. Global Inflation Range
- **Source:** IMF World Economic Outlook / World Bank
- **Update Frequency:** Quarterly
- **Reliability:** HIGH
- **Notes:** Aggregate range from major economy inflation rates
- **How to Update:** Check IMF WEO and World Bank data

### 10. Dutch TTF Hub (European Gas)
- **Source:** ICE Intercontinental Exchange
- **Update Frequency:** Daily
- **Reliability:** HIGH
- **Notes:** European natural gas benchmark. Can be automated with ICE API access.
- **How to Update:** Check theice.com or trading platforms for TTF front-month prices

### 11. Avg. US Fuel Prices
- **Source:** AAA / EIA (Energy Information Administration)
- **Update Frequency:** Weekly (EIA) / Daily (AAA)
- **Reliability:** HIGH
- **Notes:** EIA provides official government data. Can be automated with free EIA API key.
- **How to Update:** Check gasprices.aaa.com or eia.gov
- **Automation:** Get free API key at eia.gov/opendata/register.php

### 12. Trump Net Approval Rating
- **Source:** FiveThirtyEight / RealClearPolitics
- **Update Frequency:** Daily aggregate
- **Reliability:** MEDIUM-HIGH
- **Notes:** Polling aggregates have methodological limitations but represent best available consensus
- **How to Update:** Check fivethirtyeight.com or realclearpolitics.com

### 13. US Net Approval for Iran War
- **Source:** Aggregate of major polls (Gallup, Pew, Reuters/Ipsos, etc.)
- **Update Frequency:** As polls are released (typically weekly)
- **Reliability:** MEDIUM
- **Notes:** Question wording varies across polls. Net approval = % approve - % disapprove
- **How to Update:** Check major polling aggregators and individual poll releases

---

## ADDED METRICS (Recommended additions)

These metrics were added as they provide valuable context for the Iran situation:

1. **VIX (Volatility Index)** - Measures market fear/uncertainty. Spikes correlate with geopolitical events.

2. **US 10-Year Treasury Yield** - Flight-to-safety indicator. Falls when investors seek safe assets during crises.

3. **Dutch TTF Hub** - European gas prices. Iran situation affects global energy markets, and European gas prices are particularly sensitive.

---

## Reliability Summary

| Metric | Source Type | Reliability | Update Frequency |
|--------|-------------|-------------|------------------|
| S&P 500 | Live API | HIGH | Real-time |
| MSCI World | Live API (converted) | HIGH | Real-time |
| Brent Crude | Live API | HIGH | Real-time |
| WTI Crude | Live API | HIGH | Real-time |
| Henry Hub Gas | Live API | HIGH | Real-time |
| VIX | Live API | HIGH | Real-time |
| US 10-Year Treasury | Live API | HIGH | Real-time |
| Global GDP | Manual | HIGH | Quarterly |
| Global Inflation | Manual | HIGH | Quarterly |
| Dutch TTF | Manual | HIGH | Daily |
| US Fuel Prices | Manual | HIGH | Weekly |
| Trump Approval | Manual | MEDIUM-HIGH | Daily |
| Iran War Approval | Manual | MEDIUM | Weekly |

---

## Baseline Date
All comparisons are made against **February 27, 2026** as the baseline date. This should align with the start date used in your FGS Global tracking.

---

## Updating Manual Data

To update manual data points, edit the `fetch_data.py` file in the `get_manual_data()` function, or directly edit `data.json`.

Example for updating Trump approval:
```python
"trump_approval": {
    "value": -19.1,  # Update this value
    "change": "-6 pts",  # Update change from baseline
    ...
}
```

---

## API Limitations

1. **Yahoo Finance:** Free tier has no rate limits for reasonable usage. May occasionally have brief outages.

2. **EIA API:** Free with registration. 1000 requests/hour limit.

3. **Polling Data:** No API available. Must be updated manually from aggregator websites.

---

## Recommendations for Production

1. **Add EIA API Key:** Register at eia.gov/opendata/register.php for automated gas price updates

2. **Consider Bloomberg/Reuters:** For institutional use, Bloomberg Terminal or Reuters Eikon provide more reliable, comprehensive data

3. **Backup Data Sources:** Consider adding Alpha Vantage or IEX Cloud as backup APIs

4. **Polling Automation:** Consider scraping FiveThirtyEight or building RSS/API integration for polling data
