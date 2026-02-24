"""
Google Trends Data Fetcher for E-commerce Forecasting
------------------------------------------------------
Fetches search interest data for earbuds/electronics from Google Trends.
Includes fallback to generate realistic synthetic trends when API is blocked (429).

Usage:
    python src/fetch_google_trends.py
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import time

# ── Configuration ────────────────────────────────────────────────────────────
KEYWORDS = [
    "earbuds india",
    "wireless earphones",
    "bluetooth earbuds",
    "best earbuds under 2000",
    "noise earbuds"
]

TIMEFRAME = '2022-01-01 2024-12-31'
GEO = 'IN'

OUTPUT_DIR = 'data/google_trends'
os.makedirs(OUTPUT_DIR, exist_ok=True)

DATE_TAG = datetime.now().strftime("%Y%m%d")
OUTPUT_FILE      = f'{OUTPUT_DIR}/earbuds_trends_{DATE_TAG}.csv'
OUTPUT_FILE_BASE = f'{OUTPUT_DIR}/earbuds_trends_{DATE_TAG}_base.csv'


# ── Live fetch (pytrends) ────────────────────────────────────────────────────
def fetch_trends_live(keywords, timeframe, geo='IN', retries=3, pause=10):
    """Try fetching from Google Trends with retries + back-off."""
    try:
        from pytrends.request import TrendReq
    except ImportError:
        print("  pytrends not installed - skipping live fetch.")
        return None

    for attempt in range(1, retries + 1):
        try:
            print(f"  Attempt {attempt}/{retries} ...")
            pt = TrendReq(hl='en-IN', tz=330, retries=2, backoff_factor=1)
            pt.build_payload(kw_list=keywords, timeframe=timeframe, geo=geo)
            df = pt.interest_over_time()
            if df.empty:
                raise ValueError("Empty response")
            if 'isPartial' in df.columns:
                df = df.drop(columns=['isPartial'])
            return df
        except Exception as e:
            print(f"  X Attempt {attempt} failed: {e}")
            if attempt < retries:
                wait = pause * attempt
                print(f"  Waiting {wait}s before retry ...")
                time.sleep(wait)
    return None


# ── Synthetic fallback ───────────────────────────────────────────────────────
def generate_synthetic_trends(keywords, start='2022-01-01', end='2024-12-31'):
    """
    Generate realistic Google-Trends-like data when the API is blocked.

    Method:
    -------
    - Base: annual seasonality (sine wave peaking in Oct-Dec for India e-comm).
    - Spikes during known Indian festive / sale periods (Diwali, Republic-Day,
      Amazon Great Indian Festival, Flipkart Big Billion Days).
    - Smooth random walk component so each keyword has unique but correlated
      search patterns.
    - Values are scaled 0-100 (same as real Google Trends).
    """
    print("\n  Generating synthetic Google Trends data (realistic fallback)...")
    print("  NOTE: This is synthetic but follows real Indian e-commerce")
    print("        seasonal patterns for academic demonstration.\n")

    dates = pd.date_range(start=start, end=end, freq='W-SUN')
    n = len(dates)
    np.random.seed(2024)

    trends = {}
    for i, kw in enumerate(keywords):
        # 1. Annual seasonality - peak around week 42 (mid-Oct, Diwali)
        week_of_year = dates.isocalendar().week.astype(int)
        seasonality = 20 * np.sin(2 * np.pi * (week_of_year - 42) / 52) + 50

        # 2. Festive spikes
        spikes = np.zeros(n)
        for j, d in enumerate(dates):
            w = d.isocalendar().week
            m = d.month
            # Diwali season (Oct-Nov)
            if m in (10, 11) and 40 <= w <= 46:
                spikes[j] += np.random.uniform(15, 30)
            # Amazon Great Indian Festival / BBD (Sep-end)
            if m == 9 and w >= 39:
                spikes[j] += np.random.uniform(10, 20)
            # Republic Day / New Year sales
            if m == 1 and w <= 5:
                spikes[j] += np.random.uniform(5, 15)
            # Mid-year sale (Jun-Jul)
            if m in (6, 7) and 24 <= w <= 28:
                spikes[j] += np.random.uniform(5, 12)

        # 3. Smooth random walk (each keyword slightly different)
        walk = np.cumsum(np.random.normal(0, 1.5, n))
        walk = walk - walk.min()
        walk = walk / (walk.max() + 1e-9) * 15  # 0-15 range

        # 4. Keyword-specific popularity offset (first keyword most popular)
        popularity = [1.0, 0.85, 0.70, 0.55, 0.60][i]

        raw = (seasonality + spikes + walk) * popularity
        # 5. Scale to 0-100
        raw = (raw - raw.min()) / (raw.max() - raw.min() + 1e-9) * 100
        raw = np.round(raw).astype(int)
        raw = np.clip(raw, 0, 100)

        trends[kw] = raw

    df = pd.DataFrame(trends, index=dates)
    df.index.name = 'date'
    return df


# ── Lag features ─────────────────────────────────────────────────────────────
def create_lagged_features(df, lags=(1, 2, 3, 4)):
    out = df.copy()
    for col in df.columns:
        for lag in lags:
            out[f'{col}_lag{lag}'] = df[col].shift(lag)
    return out


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("GOOGLE TRENDS DATA FETCHER - E-COMMERCE FORECASTING")
    print("=" * 70)

    # --- Try live API first ---
    print("\n[1/3] Attempting live Google Trends API fetch ...")
    trends_df = fetch_trends_live(KEYWORDS, TIMEFRAME, geo=GEO,
                                  retries=2, pause=5)

    if trends_df is not None:
        print(f"\n  Live data fetched: {len(trends_df)} weeks")
        source = "LIVE"
    else:
        # --- Fallback to synthetic ---
        print("\n[1/3] Live fetch failed (429 rate-limit). Using synthetic fallback.")
        trends_df = generate_synthetic_trends(KEYWORDS,
                                              start='2022-01-01',
                                              end='2024-12-31')
        source = "SYNTHETIC"

    # --- Preview ---
    print(f"\nSource: {source}")
    print(f"Date range: {trends_df.index.min()} to {trends_df.index.max()}")
    print(f"Weeks: {len(trends_df)}")
    print(f"\nPreview:\n{trends_df.head()}")
    print(f"\nStatistics:\n{trends_df.describe().round(1)}")

    # --- Lagged version ---
    print("\n[2/3] Creating lagged features (1-4 weeks) ...")
    trends_lagged = create_lagged_features(trends_df)

    # --- Save ---
    print(f"\n[3/3] Saving ...")
    trends_df.to_csv(OUTPUT_FILE_BASE)
    print(f"  Base data  -> {OUTPUT_FILE_BASE}")
    trends_lagged.to_csv(OUTPUT_FILE)
    print(f"  With lags  -> {OUTPUT_FILE}")

    print("\n" + "=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Review  data/google_trends/  folder")
    print("2. Merge with sales data: notebooks/01_data_preparation.ipynb")
    print("3. Key insight: search interest LEADS sales by 1-3 weeks")
    if source == "SYNTHETIC":
        print("\nNote: Data is synthetic. When Google Trends API works,")
        print("      re-run this script to replace with real data.")
    print("=" * 70)


if __name__ == "__main__":
    main()
