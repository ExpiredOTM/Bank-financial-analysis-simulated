"""Stage 3 – Credit Risk Analysis.

Computes expected loss metrics, concentration analysis, and vintage summary for
the simulated loan portfolio.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plot_style  # corporate theme

from data_loading import load, OUTPUT_DIR

sns.set(style="whitegrid")


def compute_expected_loss(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["EL(USDk)"] = df["PD"] * df["LGD"] * df["EAD(USDk)"]
    return df


def el_by_rating(df: pd.DataFrame):
    agg = df.groupby("Rating").agg({
        "EAD(USDk)": "sum",
        "EL(USDk)": "sum",
    }).sort_index()
    agg["EL%"] = agg["EL(USDk)"] / agg["EAD(USDk)"] * 100
    print("\nExpected Loss by Rating:\n", agg)
    agg.to_csv(OUTPUT_DIR / "cr_el_by_rating.csv")

    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(x=agg.index, y="EL(USDk)", data=agg.reset_index(), ax=ax)
    ax.set_title("Expected Loss by Rating")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "cr_el_by_rating.png")
    plt.close()


def sector_concentration(df: pd.DataFrame):
    sector_agg = df.groupby("Sector")["EAD(USDk)"].sum().sort_values()
    plt.figure(figsize=(10,6))
    sector_agg.plot(kind="barh")
    plt.title("EAD by Sector")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "cr_sector_concentration.png")
    plt.close()


def vintage_analysis(df: pd.DataFrame):
    df = df.copy()
    df["OrigYear"] = pd.DatetimeIndex(df["OriginationDate"]).year
    vintage_ead = df.groupby("OrigYear")["EAD(USDk)"].sum()
    plt.figure(figsize=(8,5))
    vintage_ead.plot(kind="bar")
    plt.title("EAD by Vintage (Origination Year)")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "cr_vintage_ead.png")
    plt.close()

    vintage_ead.to_csv(OUTPUT_DIR / "cr_vintage_ead.csv")


def main():
    credit = load("credit")
    credit = compute_expected_loss(credit)

    el_by_rating(credit)
    sector_concentration(credit)
    vintage_analysis(credit)


if __name__ == "__main__":
    main() 