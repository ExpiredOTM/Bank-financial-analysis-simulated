import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

# Seed for reproducibility
np.random.seed(42)
random.seed(42)
fake = Faker()

# -----------------------------
# Configuration & Parameters
# -----------------------------
SNAPSHOT_DATE = pd.Timestamp("2024-06-30")
# Simulate over this many years backward from snapshot
YEARS = 5

# Currency universe (majority USD & GBP)
CURRENCIES = [
    "USD", "GBP", "JPY", "CAD", "EUR", "CHF", "AUD", "SEK", "HKD", "NZD"
]

# Jurisdictions and their relative size (sum to 1.0)
JURISDICTIONS = {
    "BM": 0.415,  # Bermuda
    "KY": 0.35,  # Cayman Islands
    "GU": 0.125, # Guernsey
    "JE": 0.11, # Jersey
}

# Balance-sheet driven aggregates (figures in thousands of USD)
TOTAL_DEPOSITS = 12_815_815  # Total deposits
TOTAL_LOANS    = 4_585_468   # Gross loan book (before ACL)
TOTAL_SECURITIES = 5_168_449 # Investment in securities (proxy for market-risk positions)

# Scenarios & settings
N_MARKET_POSITIONS = 1000  # per position, valuations will be monthly over 5 years (~60k rows)
N_CREDIT_LOANS     = 6000  # 10× bigger loan book granularity
N_LIQUIDITY_CASHFLOWS = YEARS * 1000  # 5 000 rows of cash-flows
N_TRANSACTIONS = YEARS * 50_000       # 250 000 transaction rows

# Helper functions
# ----------------

def random_choice_weighted(choices, weights):
    return random.choices(list(choices), weights=weights, k=1)[0]


def scale_amounts(raw_weights, target_total):
    """Scale a numpy array of positive numbers so that it sums exactly to target_total."""
    scaled = raw_weights / raw_weights.sum() * target_total
    return np.round(scaled, 2)  # round to cents (thousands of USD)

# -------------------------------------------------
# 1. Market-Risk Dataset (position-level exposures)
# -------------------------------------------------

def generate_market_risk_dataset():
    instruments = [
        "US_Treasury_Bond", "S&P500_Futures", "EURUSD_FX_Forward", "GBPUSD_FX_Forward",
        "Corporate_Bond_AAA", "Corporate_Bond_BBB", "InterestRateSwap_USD", "InterestRateSwap_EUR",
        "NASDAQ_Options", "Gold_Futures",
    ]
    instrument_types = {
        "US_Treasury_Bond": "Bond",
        "Corporate_Bond_AAA": "Bond",
        "Corporate_Bond_BBB": "Bond",
        "S&P500_Futures": "Equity Future",
        "NASDAQ_Options": "Equity Option",
        "EURUSD_FX_Forward": "FX Forward",
        "GBPUSD_FX_Forward": "FX Forward",
        "InterestRateSwap_USD": "IRS",
        "InterestRateSwap_EUR": "IRS",
        "Gold_Futures": "Commodity Future",
    }
    currencies = CURRENCIES  # use expanded currency list

    # Generate base notionals then scale
    raw_notional = np.random.lognormal(mean=7, sigma=0.5, size=N_MARKET_POSITIONS)
    notionals = scale_amounts(raw_notional, TOTAL_SECURITIES)

    # Monthly valuation dates for the past YEARS
    date_range = pd.date_range(end=SNAPSHOT_DATE, periods=YEARS * 12 + 1, freq="M")

    records = []
    base_attrs = []  # store static attributes for each position
    for i in range(N_MARKET_POSITIONS):
        instr = random.choice(instruments)
        base_attrs.append({
            "PositionID": f"MRK{i:05d}",
            "Jurisdiction": random_choice_weighted(JURISDICTIONS.keys(), JURISDICTIONS.values()),
            "Instrument": instr,
            "InstrumentType": instrument_types[instr],
            "Notional(USDk)": round(notionals[i], 2),
            "Currency": random.choice(currencies),
        })

    # Produce valuations across each month
    for date in date_range:
        for idx, attr in enumerate(base_attrs):
            notional = attr["Notional(USDk)"]
            mv_factor = np.random.normal(loc=1.0, scale=0.03)
            mv = notional * mv_factor
            var_1d_99 = notional * np.random.uniform(0.001, 0.012)
            stress_loss = notional * np.random.uniform(0.006, 0.035)

            records.append({
                **attr,
                "MarketValue(USDk)": round(mv, 2),
                "DailyPnL(USDk)": round(np.random.normal(0, var_1d_99 / 2), 2),
                "VaR_1d_99(USDk)": round(var_1d_99, 2),
                "StressLoss_99(USDk)": round(stress_loss, 2),
                "Delta": round(np.random.uniform(-1, 1), 4),
                "Gamma": round(np.random.uniform(0, 0.5), 4),
                "Vega": round(np.random.uniform(0, 1), 4),
                "DV01": round(np.random.uniform(-0.5, 0.5), 4),
                "ValuationDate": date.date(),
            })

    df_market = pd.DataFrame(records)
    return df_market

# -------------------------------------------------
# 2. Credit-Risk Dataset (loan / counterparty)
# -------------------------------------------------

RATINGS = ["AAA", "AA", "A", "BBB", "BB", "B"]
RATING_PD = {  # illustrative annual PDs
    "AAA": 0.0001, "AA": 0.0005, "A": 0.001, "BBB": 0.005, "BB": 0.02, "B": 0.05,
}
LGD_BY_COLLATERAL = {
    "RealEstate": 0.25,
    "Securities": 0.35,
    "Guarantee": 0.45,
    "Unsecured": 0.6,
}
SECTORS = [
    "RealEstate", "Hospitality", "Shipping", "InvestmentHoldCo", "PrivateWealth", "Retail", "Energy", "Technology",
]
COLLATERAL_TYPES = list(LGD_BY_COLLATERAL.keys())


def generate_credit_risk_dataset():
    raw_outstandings = np.random.lognormal(mean=6, sigma=0.7, size=N_CREDIT_LOANS)
    outstandings = scale_amounts(raw_outstandings, TOTAL_LOANS)

    loans = []
    for i in range(N_CREDIT_LOANS):
        rating = random_choice_weighted(RATINGS, [5,10,20,30,20,15])  # skew conservative
        collateral = random_choice_weighted(COLLATERAL_TYPES, [40, 25, 20, 15])
        prob_default = RATING_PD[rating]
        lgd = LGD_BY_COLLATERAL[collateral]
        ead = outstandings[i] * np.random.uniform(1.0, 1.05)  # small undrawn amount
        # Random origination within last 5 years and maturity 1-10 years from origination
        origination_date = SNAPSHOT_DATE - timedelta(days=random.randint(0, YEARS*365))
        maturity = origination_date + timedelta(days=int(np.random.uniform(365, 3650)))
        
        loans.append({
            "LoanID": f"LON{i:05d}",
            "Jurisdiction": random_choice_weighted(JURISDICTIONS.keys(), JURISDICTIONS.values()),
            "Borrower": fake.company(),
            "Sector": random.choice(SECTORS),
            "OriginalAmount(USDk)": round(outstandings[i] * np.random.uniform(1.0, 1.3), 2),
            "OutstandingAmount(USDk)": round(outstandings[i], 2),
            "EAD(USDk)": round(ead,2),
            "Rating": rating,
            "PD": round(prob_default, 5),
            "LGD": round(lgd, 2),
            "InterestRate(%)": round(np.random.uniform(3, 9), 2),
            "OriginationDate": origination_date.date(),
            "MaturityDate": maturity.date(),
            "Stage": random_choice_weighted([1,2,3], [85, 12, 3]),
            "DaysPastDue": random.choice([0,0,0,0,30,60,90]),
            "DefaultFlag": 0,
        })

    df_credit = pd.DataFrame(loans)
    return df_credit

# -------------------------------------------------
# 3. Liquidity-Risk Dataset (cash-flow ladder)
# -------------------------------------------------

TIME_BUCKETS = [
    "<2d", "2-7d", "8-30d", "31-90d", "91-180d", "181-365d", ">1y",
]
LCR_WEIGHTS = {
    "<2d": 1.0, "2-7d": 1.0, "8-30d": 1.0,
    "31-90d": 0.5, "91-180d": 0.5, "181-365d": 0.25, ">1y": 0.0,
}
PRODUCTS = [
    "RetailDeposit", "CorporateDeposit", "LoanRepayment", "SecurityMaturity", "DerivativesCF", "CommitmentDraw",
]


def generate_liquidity_risk_dataset():
    # Positive amounts = inflow, negative = outflow
    raw_cash = np.random.normal(loc=0, scale=TOTAL_DEPOSITS/20, size=N_LIQUIDITY_CASHFLOWS)
    # Rescale so that total ≈ - total deposits * small negative (assuming more outflows)
    rescale = (-TOTAL_DEPOSITS * 0.05) / raw_cash.sum()
    cash_amounts = raw_cash * rescale

    rows = []
    for i in range(N_LIQUIDITY_CASHFLOWS):
        bucket = random.choice(TIME_BUCKETS)
        amount = cash_amounts[i]
        rows.append({
            "CF_ID": f"CF{i:04d}",
            "Jurisdiction": random_choice_weighted(JURISDICTIONS.keys(), JURISDICTIONS.values()),
            "Product": random.choice(PRODUCTS),
            "InflowOutflow": "Inflow" if amount > 0 else "Outflow",
            "Amount(USDk)": round(amount, 2),
            "TimeBucket": bucket,
            "LCR_Weight": LCR_WEIGHTS[bucket],
            "NSFR_Weight": np.random.uniform(0.0, 1.0),
            "Date": (SNAPSHOT_DATE - timedelta(days=random.randint(0, YEARS*365))).date(),
        })

    df_liquidity = pd.DataFrame(rows)
    return df_liquidity

# -------------------------------------------------
# 4. Transaction Dataset (customer activity)
# -------------------------------------------------

CUSTOMER_CLASSES = ["corporate", "treasury", "retail", "private", "other"]

# Weights favoring USD & GBP (75% total) and skew customer classes toward corporate
CURRENCY_WEIGHTS = [0.5, 0.25] + [0.05]*8  # 50% USD, 25% GBP, 5% each remaining
CLASS_WEIGHTS = [0.35, 0.25, 0.2, 0.15, 0.05]


def generate_transaction_dataset():
    """Create customer transaction ledger with amounts in native currency and USD equivalent."""
    # Generate random transaction amounts in native currency
    raw_amts = np.random.lognormal(mean=5, sigma=0.9, size=N_TRANSACTIONS)  # native currency thousands

    records = []
    for i in range(N_TRANSACTIONS):
        tx_id = f"TX{i:06d}"
        currency = random_choice_weighted(CURRENCIES, CURRENCY_WEIGHTS)
        # Simple FX rate mapping to USD (rough spot approximations)
        fx_rates = {
            "USD": 1.00, "GBP": 1.26, "JPY": 0.0065, "CAD": 0.74, "EUR": 1.08,
            "CHF": 1.10, "AUD": 0.67, "SEK": 0.095, "HKD": 0.13, "NZD": 0.61,
        }
        amt_native = raw_amts[i]
        amt_usd = amt_native * fx_rates[currency]
        customer_class = random_choice_weighted(CUSTOMER_CLASSES, CLASS_WEIGHTS)

        records.append({
            "TransactionID": tx_id,
            "DateTime": (SNAPSHOT_DATE - timedelta(days=random.randint(0, YEARS*365)) + timedelta(hours=random.randint(0,23), minutes=random.randint(0,59))).isoformat(),
            "Jurisdiction": random_choice_weighted(JURISDICTIONS.keys(), JURISDICTIONS.values()),
            "CustomerID": f"CUST{random.randint(10000, 99999)}",
            "CustomerName": fake.company(),
            "CustomerClass": customer_class,
            "Currency": currency,
            "AmountNative(000)": round(amt_native, 2),
            "FXRateToUSD": fx_rates[currency],
            "AmountUSD(000)": round(amt_usd, 2),
        })

    df_tx = pd.DataFrame(records)
    return df_tx

# -----------------------------
# Main: generate & save CSVs
# -----------------------------

def main():
    df_market = generate_market_risk_dataset()
    df_credit = generate_credit_risk_dataset()
    df_liquidity = generate_liquidity_risk_dataset()
    df_tx = generate_transaction_dataset()

    df_market.to_csv("market_risk_positions.csv", index=False)
    df_credit.to_csv("credit_risk_loans.csv", index=False)
    df_liquidity.to_csv("liquidity_risk_cashflows.csv", index=False)
    df_tx.to_csv("customer_transactions.csv", index=False)

    print("Datasets created:")
    print(" - market_risk_positions.csv (", len(df_market), "rows)")
    print(" - credit_risk_loans.csv (", len(df_credit), "rows)")
    print(" - liquidity_risk_cashflows.csv (", len(df_liquidity), "rows)")
    print(" - customer_transactions.csv (", len(df_tx), "rows)")


if __name__ == "__main__":
    main() 