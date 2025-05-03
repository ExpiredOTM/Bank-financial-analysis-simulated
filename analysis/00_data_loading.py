"""Common data-loading utilities for simulated offshore-bank risk datasets.

This module centralizes all CSV reading logic, including memory-conscious dtype
specification and common pre-processing (e.g. parsing dates).
"""

import os
from pathlib import Path
from typing import Literal, Dict

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT  # CSVs live in repo root for this project
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# File mapping
FILES: Dict[str, Path] = {
    "market": DATA_DIR / "market_risk_positions.csv",
    "credit": DATA_DIR / "credit_risk_loans.csv",
    "liquidity": DATA_DIR / "liquidity_risk_cashflows.csv",
    "tx": DATA_DIR / "customer_transactions.csv",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_file(tag: str) -> Path:
    path = FILES[tag]
    if not path.exists():
        raise FileNotFoundError(f"Expected data file not found: {path}")
    return path


def _date_parser(date_series: pd.Series):
    """Attempt fast ISO parsing."""
    return pd.to_datetime(date_series, errors="coerce")


# ---------------------------------------------------------------------------
# Public loaders
# ---------------------------------------------------------------------------

def load_market_data(parse_dates: bool = True) -> pd.DataFrame:
    """Load market-risk positions with optional date parsing."""
    path = _check_file("market")
    df = pd.read_csv(path)
    if parse_dates:
        df["ValuationDate"] = _date_parser(df["ValuationDate"])
    return df


def load_credit_data(parse_dates: bool = True) -> pd.DataFrame:
    path = _check_file("credit")
    df = pd.read_csv(path)
    if parse_dates:
        df["OriginationDate"] = _date_parser(df["OriginationDate"])
        df["MaturityDate"] = _date_parser(df["MaturityDate"])
    return df


def load_liquidity_data(parse_dates: bool = True) -> pd.DataFrame:
    path = _check_file("liquidity")
    df = pd.read_csv(path)
    if parse_dates:
        df["Date"] = _date_parser(df["Date"])
    return df


def load_transaction_data(parse_dates: bool = True) -> pd.DataFrame:
    path = _check_file("tx")
    df = pd.read_csv(path)
    if parse_dates:
        df["DateTime"] = _date_parser(df["DateTime"])
    return df


# Convenience dictionary
LOADERS = {
    "market": load_market_data,
    "credit": load_credit_data,
    "liquidity": load_liquidity_data,
    "tx": load_transaction_data,
}


def load(tag: Literal["market", "credit", "liquidity", "tx"], **kw) -> pd.DataFrame:
    """Generic loader by tag string."""
    return LOADERS[tag](**kw) 