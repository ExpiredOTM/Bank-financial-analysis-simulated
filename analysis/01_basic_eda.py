"""Stage 1 – Basic Exploratory Data Analysis (EDA).
Produces summary statistics and sanity-check plots for all datasets.
"""

from pathlib import Path
import pandas as pd
import seaborn as sns
import plot_style  # apply corporate theme
import matplotlib.pyplot as plt

from data_loading import load, OUTPUT_DIR

sns.set(style="ticks", context="talk")


def summarize(df: pd.DataFrame, name: str):
    print(f"\n=== {name.upper()} ===")
    print(df.head())
    print(df.describe(include="all").transpose())


def main():
    market = load("market")
    credit = load("credit")
    liquidity = load("liquidity")
    tx = load("tx")

    summarize(market, "market")
    summarize(credit, "credit")
    summarize(liquidity, "liquidity")
    summarize(tx, "transactions")

    # Example plot: distribution of credit ratings
    plt.figure(figsize=(8,5))
    sns.countplot(x="Rating", data=credit, order=sorted(credit["Rating"].unique()))
    plt.title("Loan count by rating")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "eda_rating_distribution.png")
    plt.close()

    # Example plot: monthly notional by currency (market risk)
    monthly_notional = market.groupby(["Currency", pd.Grouper(key="ValuationDate", freq="M")])["Notional(USDk)"].sum().reset_index()
    plt.figure(figsize=(10,6))
    sns.lineplot(data=monthly_notional, x="ValuationDate", y="Notional(USDk)", hue="Currency")
    plt.title("Monthly Notional Exposure by Currency")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "eda_monthly_notional.png")


if __name__ == "__main__":
    main() 