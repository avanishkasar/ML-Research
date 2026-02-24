"""Quick verification script - run to confirm everything works."""
import pandas as pd
import json
import glob

print("=== FINAL FILE VERIFICATION ===\n")

# 1. Raw data
df = pd.read_csv("data/raw/amazon.csv")
print(f"1. amazon.csv: {df.shape[0]} products  OK")

# 2. Synthetic sales
sales = pd.read_csv("data/processed/synthetic_weekly_sales.csv")
print(f"2. synthetic_weekly_sales.csv: {sales.shape}  OK")

# 3. Google Trends
trends_files = glob.glob("data/google_trends/*.csv")
for f in trends_files:
    t = pd.read_csv(f)
    print(f"3. {f}: {t.shape}  OK")

# 4. Merged data
merged = pd.read_csv("data/processed/merged_sales_trends.csv")
print(f"4. merged_sales_trends.csv: {merged.shape}  OK")

# 5. Train/test
train = pd.read_csv("data/processed/train_data.csv")
test = pd.read_csv("data/processed/test_data.csv")
print(f"5. train_data.csv: {train.shape}, test_data.csv: {test.shape}  OK")

# 6. SARIMA results
with open("data/processed/sarima_results.json") as f:
    sr = json.load(f)
print(f"6. SARIMA: RMSE={sr['RMSE']}, MAPE={sr['MAPE']}%  OK")

# 7. XGBoost results
with open("data/processed/xgboost_results.json") as f:
    xr = json.load(f)
print(f"7. XGBoost A: RMSE={xr['model_a']['RMSE']}, B: RMSE={xr['model_b']['RMSE']}  OK")

# 8. Comparison
comp = pd.read_csv("data/processed/model_comparison.csv")
print(f"8. model_comparison.csv: {comp.shape}  OK")
print()
print(comp.to_string(index=False))
print()
print("ALL FILES VERIFIED SUCCESSFULLY!")
