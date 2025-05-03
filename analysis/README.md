# Comprehensive Risk Analysis Framework

This folder contains a **layered, end-to-end analysis** of the simulated offshore-bank datasets.

Gradient of sophistication:

| Stage | File | Scope | Level |
|-------|------|-------|-------|
| 0 | `00_data_loading.py` | Common loader utilities | Boiler-plate |
| 1 | `01_basic_eda.py` | Quick sanity checks & descriptive stats | Basic |
| 2 | `02_market_risk_analysis.py` | VaR back-testing, stress P&L, risk-factor sensitivities | Intermediate |
| 3 | `03_credit_risk_analysis.py` | PD/LGD, expected loss waterfall, concentration & vintage analysis | Intermediate |
| 4 | `04_liquidity_risk_analysis.py` | Gap ladder, LCR/NSFR, survival horizon, name-concentration | Intermediate |
| 5 | `05_integrated_risk_dashboard.py` | Economic Capital aggregation, ICAAP-style stress, risk-adjusted return (RAROC) | Advanced |
| 6 | `06_credit_risk_modeling.R` | (R) Bayesian logistic & survival models for default prediction | Advanced |

## Usage

1. Ensure the virtual environment has `pandas`, `numpy`, `scipy`, `matplotlib`, `seaborn`, `scikit-learn`, and `plotly` for Python; and `tidyverse`, `rstanarm` for R.
2. Run each script sequentially or cherry-pick.
3. Outputs are stored in the `output/` sub-folder (auto-created) as CSVs, plots, and HTML dashboards. 