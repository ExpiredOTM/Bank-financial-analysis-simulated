"""Stage 5 – Integrated Risk Dashboard (Economic Capital & RAROC).

Aggregates risk across credit, market, and liquidity books to produce a simple
ICAAP-style economic capital (EC) assessment and risk-adjusted return on
capital (RAROC).

Assumptions (illustrative):
• Credit EC = Unexpected Loss @ 99.9% quantile ≈ 3 × Expected Loss
• Market EC = 10-day 99% VaR multiplied by regulatory factor 3.3
• Liquidity EC proxy = Net 30-day outflows (near-term) × stress factor 1.25
• Income proxy = Net interest margin 2.5% of average loans + average daily P&L (market)

Outputs
=======
• `ec_breakdown.csv` – component EC values
• `raroc_summary.csv` – income, EC, RAROC
• Bar-plot of EC components (`ec_components.png`)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plot_style

from data_loading import load, OUTPUT_DIR

sns.set(style="whitegrid")


# ---------------------------------------------------------------------------
# Credit Risk EC
# ---------------------------------------------------------------------------

def credit_economic_capital() -> float:
    credit = load("credit")
    credit["EL"] = credit["PD"] * credit["LGD"] * credit["EAD(USDk)"]
    total_el = credit["EL"].sum()
    ec_credit = 3.0 * total_el  # simple multiplier
    return ec_credit


# ---------------------------------------------------------------------------
# Market Risk EC
# ---------------------------------------------------------------------------

def market_economic_capital() -> float:
    mrk = load("market")
    # Aggregate 1-day VaR across portfolio daily then pick latest date
    latest = mrk["ValuationDate"].max()
    latest_df = mrk[mrk["ValuationDate"] == latest]
    daily_var = latest_df["VaR_1d_99(USDk)"].sum()
    ten_day_var = daily_var * np.sqrt(10)
    ec_market = ten_day_var * 3.3  # reg scaling
    return ec_market


# ---------------------------------------------------------------------------
# Liquidity Risk EC
# ---------------------------------------------------------------------------

def liquidity_economic_capital() -> float:
    lr = load("liquidity")
    # Use near-term weighted outflows minus inflows as stress proxy
    near_buckets = ["<2d", "2-7d", "8-30d"]
    inflow = (lr[(lr["InflowOutflow"] == "Inflow") & (lr["TimeBucket"].isin(near_buckets))]["Amount(USDk)"] * lr["LCR_Weight"]).sum()
    outflow = (lr[(lr["InflowOutflow"] == "Outflow") & (lr["TimeBucket"].isin(near_buckets))]["Amount(USDk)"] * lr["LCR_Weight"]).abs().sum()
    net = max(outflow - inflow, 0)
    ec_liquidity = net * 1.25  # stress factor
    return ec_liquidity


# ---------------------------------------------------------------------------
# Income proxy
# ---------------------------------------------------------------------------

def income_proxy() -> float:
    credit = load("credit")
    mrk = load("market")

    nim = 0.025 * credit["OutstandingAmount(USDk)"].sum()
    pnl_market = mrk["DailyPnL(USDk)"].mean() * 260  # annualize mean daily P&L

    return nim + pnl_market


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

def build_dashboard():
    ec_credit = credit_economic_capital()
    ec_market = market_economic_capital()
    ec_liq = liquidity_economic_capital()

    ec_dict = {
        "CreditEC(USDk)": ec_credit,
        "MarketEC(USDk)": ec_market,
        "LiquidityEC(USDk)": ec_liq,
    }
    total_ec = sum(ec_dict.values())

    income = income_proxy()
    raroc = income / total_ec if total_ec else float("inf")

    # Save outputs
    pd.Series(ec_dict).to_csv(OUTPUT_DIR / "ec_breakdown.csv")
    pd.Series({"Income(USDk)": income, "TotalEC(USDk)": total_ec, "RAROC": raroc}).to_csv(OUTPUT_DIR / "raroc_summary.csv")

    # Plot EC components
    plt.figure(figsize=(8,5))
    sns.barplot(x=list(ec_dict.keys()), y=list(ec_dict.values()), palette="Blues_d")
    plt.title("Economic Capital Components")
    plt.ylabel("USDk")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "ec_components.png")
    plt.close()

    print("\nEconomic Capital Breakdown (USDk):", ec_dict)
    print(f"Income (USDk): {income:,.0f}  Total EC (USDk): {total_ec:,.0f}  -> RAROC: {raroc:.2%}")


if __name__ == "__main__":
    build_dashboard() 