# Bank Risk Analysis Framework

A comprehensive simulation and analysis pipeline for offshore bank risk modeling. Includes synthetic data generation and multi-stage risk analysis across credit, market, and liquidity domains.

## Features

- **Synthetic Data**: Realistic, coherent datasets simulating 5 years of activity for an offshore bank with $12.5B in deposits
- **Multi-phase Risk Analysis**:
  - Market Risk: VaR back-testing and concentration analysis
  - Credit Risk: PD/LGD, expected loss, vintage analysis and Bayesian modeling
  - Liquidity Risk: Gap ladder analysis and LCR calculation
  - Integrated Risk: Economic capital and RAROC metrics

## Installation

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

1. Generate synthetic datasets (one-time setup):
   ```bash
   python generate_risk_datasets.py
   ```

2. Run analysis scripts in order:
   ```bash
   cd analysis
   python 01_basic_eda.py                 # Basic stats & plots
   python 02_market_risk_analysis.py      # VaR back-testing
   python 03_credit_risk_analysis.py      # Expected loss
   python 04_liquidity_risk_analysis.py   # Gap ladder
   python 05_integrated_risk_dashboard.py # Economic capital
   ```

3. Run advanced Bayesian R model (optional, requires R + packages):
   ```bash
   Rscript analysis/06_credit_risk_modeling.R
   ```

## Datasets

- `market_risk_positions.csv` (61,000 rows): Trading book positions with P&L, VaR, stress metrics
- `credit_risk_loans.csv` (6,000 rows): Loan portfolio with ratings, sectors, PD/LGD
- `liquidity_risk_cashflows.csv` (5,000 rows): Cash flow ladder with LCR/NSFR weights
- `customer_transactions.csv` (250,000 rows): Customer-level transaction data

## Outputs

All charts and data exports are saved to the `output/` directory.

## Dependencies

- Python: pandas, numpy, matplotlib, seaborn, scikit-learn, scipy
- R (optional): tidyverse, rstanarm, here 