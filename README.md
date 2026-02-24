# Enhancing E-Commerce Sales Forecasting Using Google Trends
**A Machine Learning Approach for Indian Online Retail**

## Team Members
- Avanish Ravindra Kasar (Roll: 155, Div: B)
- Rupali Pratap Biradar (Roll: 147, Div: B)
- Vrushti Jasmin Zaveri (Roll: 211, Div: B)
- Samyak Amit Sarode (Roll: 173, Div: B)

**Guided by:** DR. R. R. NIKAM

---

## Project Overview
This project enhances e-commerce price/demand forecasting by incorporating Google Trends search data as a leading indicator of customer intent. We compare baseline models (SARIMA) with enhanced models (XGBoost + Google Trends) to demonstrate forecast accuracy improvements.

## Problem Statement
Indian e-commerce demand is dynamic and influenced by multiple factors. Existing forecasting systems struggle to incorporate customer intent signals from web search data, relying solely on historical patterns and resulting in 10-15% prediction errors that cause inventory mismanagement.

## Objectives
1. Design a data pipeline to collect and preprocess historical e-commerce data and Google Trends data
2. Analyze the relationship between consumer search interest patterns and product demand/prices
3. Develop ML/time-series models to forecast trends using combined features
4. Evaluate model performance to assess Google Trends contribution
5. Build an interactive frontend for launch timing and pricing recommendations

## Tech Stack
- **Language:** Python 3.13
- **Data Processing:** Pandas, NumPy
- **ML/Forecasting:** Scikit-learn (SVR, RF), XGBoost, Statsmodels (SARIMA)
- **Google Trends:** pytrends (API wrapper)
- **Visualization:** Matplotlib, Seaborn, Plotly
- **Frontend:** Streamlit
- **Environment:** VS Code, Jupyter Notebook

## Dataset
- **Current:** Amazon tech gadgets product catalog (reviews, ratings, prices)
- **Required:** Time-series sales/demand data + Google Trends data
- **Time Range:** 2022-2024 (recommended)

## Expected Outcomes
- Forecast accuracy comparison (baseline vs. Google Trends-enhanced)
- Feature importance insights showing Google Trends contribution
- Best-performing model identification (SARIMA vs. XGBoost)
- Interactive dashboard for launch timing and optimal pricing recommendations

## SDG Goals
- **SDG 12:** Responsible Consumption - prevent overproduction & waste (40% reduction)
- **SDG 9:** Innovation - democratize advanced analytics for SMEs (500,000+ businesses)
- **SDG 8:** Economic Growth - improve revenue & working capital (3-5% profit increase)

## References
1. Boone, T., Ganeshan, R., Jain, A., & Sanders, N. R. (2018). Forecasting sales in the supply chain: Consumer analytics in the big data era. *POM*.
2. Boone, T., Ganeshan, R., & Hicks, R. L. (2015). Incorporating Google Trends data into sales forecasting. *Foresight*.
3. Ensafi, Y., Alizadeh, S. H., & Khodaee, S. M. (2022). Time-series forecasting of seasonal items sales using machine learning. *IJIMDI*.

## Project Structure
```
research-3.1/
├── data/
│   ├── raw/                  # Original datasets
│   ├── processed/            # Cleaned & merged data
│   └── google_trends/        # Google Trends CSV files
├── notebooks/
│   ├── 01_data_preparation.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_sarima_baseline.ipynb
│   ├── 05_xgboost_with_trends.ipynb
│   └── 06_results_comparison.ipynb
├── src/
│   ├── fetch_google_trends.py
│   ├── data_preprocessing.py
│   └── utils.py
├── frontend/
│   └── launch_optimizer_app.py
├── requirements.txt
└── README.md
```

## Installation
```bash
# Clone repository
git clone https://github.com/avanishkasar/research-3.1.git
cd research-3.1

# Install dependencies
pip install -r requirements.txt
```

## Usage
1. **Fetch Google Trends data:** `python src/fetch_google_trends.py`
2. **Run notebooks sequentially** (01 → 06)
3. **Launch frontend:** `streamlit run frontend/launch_optimizer_app.py`

## Status
🚧 **In Progress** - Building 70% working prototype
