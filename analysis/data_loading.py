"""Common data-loading utilities for simulated offshore-bank risk datasets.

Centralizes CSV reading logic and creates a single source of truth for file
paths, output directory, and basic date parsing.
"""

from pathlib import Path
from typing import Literal, Dict

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT  # root contains generated CSVs
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

FILES: Dict[str, Path] = {
    "market": DATA_DIR / "market_risk_positions.csv",
    "credit": DATA_DIR / "credit_risk_loans.csv",
    "liquidity": DATA_DIR / "liquidity_risk_cashflows.csv",
    "tx": DATA_DIR / "customer_transactions.csv",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check(tag: str) -> Path:
    p = FILES[tag]
    if not p.exists():
        raise FileNotFoundError(p)
    return p


def _dt(series: pd.Series):
    return pd.to_datetime(series, errors="coerce")

# ---------------------------------------------------------------------------
# Loader functions
# ---------------------------------------------------------------------------

def load_market(parse_dates=True):
    df = pd.read_csv(_check("market"))
    if parse_dates:
        df["ValuationDate"] = _dt(df["ValuationDate"])
    return df


def load_credit(parse_dates=True):
    df = pd.read_csv(_check("credit"))
    if parse_dates:
        df["OriginationDate"] = _dt(df["OriginationDate"])
        df["MaturityDate"] = _dt(df["MaturityDate"])
    return df


def load_liquidity(parse_dates=True):
    df = pd.read_csv(_check("liquidity"))
    if parse_dates:
        df["Date"] = _dt(df["Date"])
    return df


def load_tx(parse_dates=True):
    df = pd.read_csv(_check("tx"))
    if parse_dates:
        df["DateTime"] = _dt(df["DateTime"])
    return df

LOADERS = {
    "market": load_market,
    "credit": load_credit,
    "liquidity": load_liquidity,
    "tx": load_tx,
}


def load(tag: Literal["market", "credit", "liquidity", "tx"], **kw):
    return LOADERS[tag](**kw) 