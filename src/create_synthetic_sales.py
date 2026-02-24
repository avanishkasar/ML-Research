"""
Transform Amazon Product Catalog into Time-Series Sales Data
-------------------------------------------------------------
Creates synthetic weekly sales data using review_count as a proxy demand indicator

Approach:
1. Filter top product categories (earbuds, cables, accessories)
2. Use rating_count as base demand signal
3. Generate weekly time-series (2022-2024)
4. Add realistic seasonality & noise
5. Correlate with price fluctuations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Configuration
INPUT_FILE = 'data/raw/amazon.csv'
OUTPUT_DIR = 'data/processed'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Date range for synthetic data
START_DATE = '2022-01-01'
END_DATE = '2024-12-31'

# Target categories (focus on electronics accessories)
TARGET_CATEGORIES = [
    'Computers&Accessories|Accessories&Peripherals|Cables&Accessories|Cables|USBCables',
    'Electronics|HomeTheater,TV&Video|Accessories|Cables|HDMICables',
    'Computers&Accessories|NetworkingDevices|NetworkAdapters|WirelessUSBAdapters'
]


def load_amazon_data():
    """Load and initial filtering of Amazon catalog"""
    print(f"Loading {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    print(f"✓ Loaded {len(df):,} products")
    
    # Clean numeric columns (they contain commas e.g. "24,269")
    df['rating_count'] = pd.to_numeric(
        df['rating_count'].astype(str).str.replace(',', ''), errors='coerce'
    ).fillna(0)
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
    
    # Display column info
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nTop categories:")
    print(df['category'].value_counts().head(10))
    
    return df


def extract_price(price_str):
    """Extract numeric price from rupee string"""
    if pd.isna(price_str):
        return None
    # Remove ₹ and commas, convert to float
    return float(str(price_str).replace('₹', '').replace(',', ''))


def create_weekly_timeseries(df, start_date, end_date):
    """
    Create weekly sales time-series from product catalog
    
    Logic:
    - rating_count = cumulative reviews (proxy for total sales)
    - Distribute this across weeks with seasonal patterns
    - Higher ratings → higher weekly units
    - Lower prices → higher demand spikes
    """
    print("\nGenerating weekly time-series...")
    
    # Create date range (weekly frequency)
    date_range = pd.date_range(start=start_date, end=end_date, freq='W')
    
    # Process each category
    all_series = []
    
    for category in TARGET_CATEGORIES:
        cat_data = df[df['category'] == category].copy()
        
        if len(cat_data) == 0:
            continue
        
        # Extract numeric prices
        cat_data['price_numeric'] = cat_data['discounted_price'].apply(extract_price)
        
        # Calculate base demand signal
        # Higher rating_count = more total sales over product lifetime
        cat_data['base_demand'] = cat_data['rating_count'].fillna(0) / 52  # Distribute over ~1 year
        
        # Category average weekly demand
        avg_weekly_demand = cat_data['base_demand'].mean()
        
        if avg_weekly_demand == 0:
            continue
        
        # Generate seasonal pattern
        weeks = len(date_range)
        seasonal_pattern = generate_seasonal_pattern(weeks)
        
        # Add trend component (slight growth over time)
        trend = np.linspace(1.0, 1.15, weeks)  # 15% growth over 3 years
        
        # Combine: base * seasonal * trend + noise
        np.random.seed(42)
        noise = np.random.normal(0, 0.1, weeks)  # 10% random variation
        
        weekly_units = avg_weekly_demand * seasonal_pattern * trend * (1 + noise)
        weekly_units = np.maximum(weekly_units, 0)  # No negative sales
        
        # Create DataFrame
        category_name = category.split('|')[-1]  # Last part of category path
        series_df = pd.DataFrame({
            'Date': date_range,
            'Category': category_name,
            'Units_Sold': weekly_units.astype(int),
            'Avg_Price': cat_data['price_numeric'].mean(),
            'Avg_Rating': cat_data['rating'].mean()
        })
        
        all_series.append(series_df)
        print(f"  ✓ Created {category_name}: {len(series_df)} weeks, avg {weekly_units.mean():.0f} units/week")
    
    # Combine all categories
    combined = pd.concat(all_series, ignore_index=True)
    return combined


def generate_seasonal_pattern(weeks):
    """
    Generate realistic e-commerce seasonal pattern
    
    Peaks:
    - Festive season (Oct-Dec): Diwali, Christmas
    - Republic Day sales (Jan)
    - Mid-year sales (Jun-Jul)
    
    Troughs:
    - Post-festival (Jan-Feb)
    - Summer months (Apr-May)
    """
    # Create base sinusoidal pattern (annual cycle)
    annual_cycle = np.sin(np.linspace(0, 3 * 2 * np.pi, weeks)) * 0.2 + 1.0
    
    # Add festive spikes (Oct-Dec every year)
    festive_spikes = np.zeros(weeks)
    for i in range(weeks):
        week_of_year = (i % 52)
        # Diwali/Christmas spike (weeks 40-52)
        if 40 <= week_of_year <= 52:
            festive_spikes[i] = 0.4
        # Republic Day (week 4)
        elif week_of_year == 4:
            festive_spikes[i] = 0.3
        # Mid-year sales (weeks 24-28)
        elif 24 <= week_of_year <= 28:
            festive_spikes[i] = 0.25
    
    return annual_cycle + festive_spikes


def add_price_variations(df):
    """Add weekly price variations based on demand"""
    # Higher demand weeks → slightly lower prices (sales/discounts)
    # Lower demand weeks → regular prices
    df['Price_Elasticity'] = 1 - (df['Units_Sold'] / df['Units_Sold'].max()) * 0.15
    df['Weekly_Price'] = (df['Avg_Price'] * df['Price_Elasticity']).round(2)
    
    return df


def save_data(df):
    """Save processed data"""
    output_file = f'{OUTPUT_DIR}/synthetic_weekly_sales.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✓ Saved to: {output_file}")
    
    # Display summary
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    print(df.groupby('Category').agg({
        'Units_Sold': ['mean', 'min', 'max'],
        'Weekly_Price': ['mean', 'std'],
        'Avg_Rating': 'first'
    }).round(2))
    
    print(f"\nDate range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"Total weeks: {len(df['Date'].unique())}")
    print(f"Categories: {df['Category'].nunique()}")
    
    return output_file


def main():
    """Main execution"""
    print("="*70)
    print("SYNTHETIC SALES DATA GENERATOR")
    print("="*70)
    
    # Load data
    amazon_df = load_amazon_data()
    
    # Generate time-series
    sales_df = create_weekly_timeseries(amazon_df, START_DATE, END_DATE)
    
    # Add price variations
    sales_df = add_price_variations(sales_df)
    
    # Save
    output = save_data(sales_df)
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print(f"1. Review the data: {output}")
    print("2. Fetch Google Trends: python src/fetch_google_trends.py")
    print("3. Merge datasets: notebooks/01_data_preparation.ipynb")
    print("="*70)


if __name__ == "__main__":
    main()
