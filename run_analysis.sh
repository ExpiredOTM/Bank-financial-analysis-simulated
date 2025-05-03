#!/usr/bin/env bash
# Run full risk analysis pipeline (macOS, Python 3.11 + R)
set -euo pipefail

# 1. Create virtual environment and install Python dependencies
PY=python3.11
if ! command -v "$PY" &> /dev/null; then
  echo "Error: $PY not found. Please install Python 3.11." >&2
  exit 1
fi

# Create venv if missing
if [ ! -d .venv ]; then
  echo "Creating virtualenv with $PY..."
  $PY -m venv .venv
fi
source .venv/bin/activate

# Upgrade pip and install requirements
pip install --upgrade pip
pip install -r requirements.txt

# 2. Create results directory
RESULTS_DIR="analysis/Analysis Results"
mkdir -p "$RESULTS_DIR"

# 3. Generate synthetic datasets
echo "Generating synthetic datasets..."
python generate_risk_datasets.py

# 4. Run analysis stages 1–5 in Python
echo "Running Python analysis stages..."
python analysis/01_basic_eda.py
python analysis/02_market_risk_analysis.py
python analysis/03_credit_risk_analysis.py
python analysis/04_liquidity_risk_analysis.py
python analysis/05_integrated_risk_dashboard.py

# 5. Run advanced R credit model (stage 6) – non-fatal
echo "Running R credit risk modeling (stage 6)..."
# Allow errors without exiting pipeline
set +e
if command -v Rscript &> /dev/null; then
  # Attempt to install minimal R packages and run; ignore failures
  Rscript -e "required <- c('readr','rstanarm'); installed <- rownames(installed.packages()); to_install <- setdiff(required, installed); if(length(to_install)) install.packages(to_install, repos='https://cloud.r-project.org');"
  # Run model, redirect output to log
  Rscript analysis/06_credit_risk_modeling.R > "$RESULTS_DIR/r_stage6.log" 2>&1 || echo "Stage 6 R modeling failed or logged to r_stage6.log."
else
  echo "Warning: Rscript not found, skipping stage 6." >&2
fi
set -e

# 6. Collate outputs
echo "Collating outputs into $RESULTS_DIR..."
# Move or copy all files from root output/ to results folder
if [ -d output ]; then
  mv output/* "$RESULTS_DIR/"
  rm -rf output
fi

echo "Analysis complete! Results available in '$RESULTS_DIR'." 