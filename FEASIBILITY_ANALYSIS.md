# Iran Metrics Dashboard - Expansion Feasibility Analysis

## Executive Summary

| Feature | Feasibility | Auto-Update | Notes |
|---------|-------------|-------------|-------|
| Current prices + % change | **YES** | YES | Already working |
| Michigan Consumer Survey (aggregate) | **YES** | YES | Via FRED API |
| Michigan Survey by party | **PARTIAL** | NO | PDF reports only, no API |
| GICS Level 3 (74 industries) | **PARTIAL** | YES | Use sector ETFs as proxy |
| Individual stock EPS by industry | **NO** | - | Requires paid data ($$$) |
| Nate Silver polling | **PARTIAL** | NO | Data available, no API |
| Supply chain / semiconductor | **YES** | YES | Silicon Analysts API (free) |
| Scenario modeling | **YES** | - | Static analysis, user-driven |

---

## Detailed Analysis

### 1. Michigan Consumer Survey

**What's Available (FREE):**
- Consumer Sentiment Index (UMCSENT) via FRED API
- 1-Year Inflation Expectations (MICH) via FRED API
- 5-Year Inflation Expectations via FRED API
- Monthly updates, auto-fetchable

**What's NOT Available via API:**
- Party affiliation breakdowns (Democrat/Republican/Independent)
- These are only published in PDF reports at https://data.sca.isr.umich.edu/reports.php

**Recommendation:** Auto-fetch aggregate data, manually update partisan data monthly from reports.

---

### 2. GICS Level 3 Industry Data

**The Problem:**
- GICS classification is proprietary (S&P/MSCI)
- Individual stock → GICS mapping requires paid services ($10K+/year)
- EPS data by industry also requires Bloomberg/Refinitiv ($$$)

**The Solution - Sector ETFs:**
We can use SPDR Sector ETFs as proxies for the 11 GICS sectors:

| Sector | ETF | What It Tracks |
|--------|-----|----------------|
| Technology | XLK | Semiconductors, software, hardware |
| Energy | XLE | Oil, gas, energy equipment |
| Financials | XLF | Banks, insurance, capital markets |
| Health Care | XLV | Pharma, biotech, healthcare equipment |
| Consumer Discretionary | XLY | Retail, autos, hotels, restaurants |
| Consumer Staples | XLP | Food, beverages, household products |
| Industrials | XLI | Aerospace, defense, machinery |
| Materials | XLB | Chemicals, metals, packaging |
| Utilities | XLU | Electric, gas, water utilities |
| Real Estate | XLRE | REITs, real estate services |
| Communication Services | XLC | Media, telecom, entertainment |

**What We CAN Do:**
- Track price changes for all 11 sectors since war start (Feb 27, 2026)
- Show sector performance heat map
- Identify winners/losers by sector
- All via Yahoo Finance (free)

**What We CANNOT Do (without paid data):**
- Individual company EPS changes
- True GICS Level 3 (74 industries) breakdown
- Bottom-up industry analysis

---

### 3. Nate Silver / Silver Bulletin Polling

**What's Available:**
- Raw polling data downloadable (free with attribution)
- Presidential approval tracker
- No formal API

**Recommendation:**
- Manually fetch CSV data weekly
- Or scrape their approval tracker page
- Attribute to Silver Bulletin

---

### 4. Supply Chain / Semiconductor Analysis

**Silicon Analysts API (FREE):**
- 50-100 requests/day free tier
- AI accelerator chip costs (NVIDIA, AMD, Intel, etc.)
- HBM market data (pricing, supply)
- Wafer pricing by process node
- Supply chain signals (geopolitical impacts)
- Packaging cost benchmarks

**This is highly relevant for:**
- Helium shortage impacts on chip manufacturing
- Second-order effects on AI/data centers
- Supply chain disruption tracking

**Other Free Sources:**
- Commodity prices via Yahoo Finance (gold, copper, etc.)
- Baltic Dry Index (shipping)
- Energy prices (already have)

---

### 5. Scenario Modeling

**What's Feasible:**
- Static scenario analysis (pre-written)
- User-selectable scenarios (dropdown)
- Display different projections based on scenario

**Scenarios to Model:**
1. **Baseline:** Limited conflict, Hormuz stays open
2. **Escalation:** Hormuz blocked 30-60 days
3. **Full Conflict:** Extended military engagement
4. **De-escalation:** Diplomatic resolution

**For Each Scenario, Show:**
- Oil price projections
- Inflation impact
- Supply chain disruptions
- Industry winners/losers

---

## Recommended Dashboard Structure

```
IRAN SITUATION METRICS
├── Markets (live)
│   ├── S&P 500, MSCI, VIX, Treasury
│   └── All 11 sector ETFs with % change
├── Energy (live)
│   ├── Brent, WTI, Henry Hub
│   └── Commodities (gold, copper, etc.)
├── Consumer Sentiment (FRED API)
│   ├── Michigan Consumer Index
│   ├── Inflation Expectations (1yr, 5yr)
│   └── Partisan breakdown (manual update)
├── Political (manual)
│   ├── Trump approval
│   ├── War approval
│   └── Silver Bulletin tracker link
├── Sector Analysis (live)
│   ├── Heat map of 11 sectors
│   ├── Best/worst performers
│   └── War-related industries highlighted
├── Supply Chain (API + manual)
│   ├── Semiconductor supply signals
│   ├── Helium/chip manufacturing
│   ├── Key commodity impacts
│   └── Shipping indicators
└── Scenario Analysis (static)
    ├── Scenario selector
    ├── Projected impacts table
    └── Key industries affected
```

---

## Implementation Plan

### Phase 1: Core Updates (auto-update capable)
- Add all 11 sector ETFs
- Add FRED consumer sentiment/inflation data
- Add more commodity prices
- Clean up UI

### Phase 2: Supply Chain
- Integrate Silicon Analysts API
- Add semiconductor supply chain section
- Add key commodity tracking

### Phase 3: Analysis Sections
- Build scenario selector
- Create supply chain impact analysis
- Add industry-specific sections

### Phase 4: Manual Data
- Create admin section for manual updates
- Partisan sentiment (monthly)
- Polling data (weekly)

---

## Data Sources Summary

| Data | Source | Update Frequency | Method |
|------|--------|------------------|--------|
| Market prices | Yahoo Finance | Live | yfinance |
| Sector ETFs | Yahoo Finance | Live | yfinance |
| Consumer sentiment | FRED | Monthly | API |
| Inflation expectations | FRED | Monthly | API |
| Semiconductor data | Silicon Analysts | Daily | API |
| Trump approval | Silver Bulletin | Daily | Manual/scrape |
| Partisan sentiment | U of M Reports | Monthly | Manual |
| Scenario analysis | Internal | Static | Pre-written |
