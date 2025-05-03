"""Stage 2 – Market Risk Analysis.

Calculates and visualizes:
1. Back-testing of 1-day 99% VaR using P&L exceedances
2. Stress loss distribution (historical simulation proxy)
3. Risk-factor concentration (currency / instrument type)

Outputs written to the `output/` folder.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plot_style  # corporate theme

from data_loading import load, OUTPUT_DIR

sns.set(style="whitegrid")


def backtest_var(df: pd.DataFrame):
    """Simple VaR back-test counting breaches per day."""
    daily = df.groupby(["ValuationDate"]).agg({
        "DailyPnL(USDk)": "sum",
        "VaR_1d_99(USDk)": "sum",
    }).reset_index()
    daily["Breach"] = daily["DailyPnL(USDk)"] < -daily["VaR_1d_99(USDk)"]

    breaches = daily["Breach"].sum()
    total_days = len(daily)
    ex_post_breach_rate = breaches / total_days
    expected_rate = 0.01

    print(f"Back-test summary: {breaches} breaches out of {total_days} days (rate={ex_post_breach_rate:.3%}, expected 1%).")

    plt.figure(figsize=(10,4))
    plt.plot(daily["ValuationDate"], daily["DailyPnL(USDk)"], label="P&L")
    plt.plot(daily["ValuationDate"], -daily["VaR_1d_99(USDk)"], label="VaR 99%", alpha=0.7)
    plt.scatter(daily.loc[daily["Breach"], "ValuationDate"], daily.loc[daily["Breach"], "DailyPnL(USDk)"], color="red", label="Breaches", zorder=5)
    plt.legend()
    plt.title("Portfolio P&L vs 1-day 99% VaR")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "mr_var_backtest.png")
    plt.close()


def stress_loss_distribution(df: pd.DataFrame):
    """Histogram of stress losses (already simulated)."""
    plt.figure(figsize=(8,5))
    sns.histplot(df["StressLoss_99(USDk)"], bins=50, kde=False)
    plt.title("Distribution of Stress Losses (99th pct)")
    plt.xlabel("Stress Loss 99% (USDk)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "mr_stress_loss_hist.png")
    plt.close()


def risk_factor_concentration(df: pd.DataFrame):
    """Bar charts of notional by instrument type and currency."""
    by_instr = df.groupby("InstrumentType")["Notional(USDk)"].sum().sort_values()
    by_curr = df.groupby("Currency")["Notional(USDk)"].sum().sort_values()

    fig, ax = plt.subplots(1,2, figsize=(12,5))
    by_instr.plot(kind="barh", ax=ax[0])
    ax[0].set_title("Notional by Instrument Type")
    by_curr.plot(kind="barh", ax=ax[1], color="orange")
    ax[1].set_title("Notional by Currency")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "mr_concentration.png")
    plt.close()


def main():
    market = load("market")

    # Focus on latest date portfolio snapshot for concentration, but back-test requires history
    latest_date = market["ValuationDate"].max()
    latest_df = market[market["ValuationDate"] == latest_date]

    backtest_var(market)
    stress_loss_distribution(latest_df)
    risk_factor_concentration(latest_df)


if __name__ == "__main__":
    main() 