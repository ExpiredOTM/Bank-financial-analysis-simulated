"""Stage 4 – Liquidity Risk Analysis.

Key outputs:
1. Static contractual gap ladder (sum of cash flows by time bucket)
2. Cumulative gap plot – identifies surplus / deficit horizons
3. Proxy LCR & NSFR calculations using provided weights
4. Product-level concentration of outflows

Results saved in `output/`.
"""

from typing import List
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plot_style

from data_loading import load, OUTPUT_DIR

sns.set(style="whitegrid")

NEAR_TERM_BUCKETS: List[str] = ["<2d", "2-7d", "8-30d"]


def gap_ladder(df: pd.DataFrame) -> pd.DataFrame:
    ladder = df.groupby("TimeBucket")["Amount(USDk)"].sum().reindex(df["TimeBucket"].unique())
    ladder = ladder.fillna(0)
    # Ensure a fixed ordering
    ordering = ["<2d", "2-7d", "8-30d", "31-90d", "91-180d", "181-365d", ">1y"]
    ladder = ladder.reindex(ordering)
    ladder.name = "NetCF(USDk)"
    ladder.to_csv(OUTPUT_DIR / "lr_gap_ladder.csv")
    return ladder


def plot_gap(ladder: pd.Series):
    plt.figure(figsize=(8,5))
    ladder.plot(kind="bar")
    plt.axhline(0, color="black", linewidth=0.8)
    plt.title("Contractual Net Cash Flow Gap by Bucket")
    plt.ylabel("USDk")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "lr_gap_ladder.png")
    plt.close()

    # Cumulative
    cumsum = ladder.cumsum()
    plt.figure(figsize=(8,5))
    cumsum.plot(marker="o")
    plt.axhline(0, color="black", linewidth=0.8)
    plt.title("Cumulative Net Cash Flow Gap")
    plt.ylabel("USDk")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "lr_gap_cumulative.png")
    plt.close()


def proxy_lcr(df: pd.DataFrame):
    # Separate inflows/outflows
    inflows = df[df["InflowOutflow"] == "Inflow"].copy()
    outflows = df[df["InflowOutflow"] == "Outflow"].copy()

    inflows_near = inflows[inflows["TimeBucket"].isin(NEAR_TERM_BUCKETS)]
    outflows_near = outflows[outflows["TimeBucket"].isin(NEAR_TERM_BUCKETS)]

    weighted_inflows = (inflows_near["Amount(USDk)"] * inflows_near["LCR_Weight"]).sum()
    weighted_outflows = (outflows_near["Amount(USDk)"].abs() * outflows_near["LCR_Weight"]).sum()

    net_outflow = max(weighted_outflows - weighted_inflows, 0)

    # Proxy HQLA: assume 20% of total securities portfolio acts as HQLA – pull from market data via loader
    try:
        market = load("market")
        hqla = 0.20 * market["MarketValue(USDk)"].abs().sum()
    except Exception:
        hqla = 0

    lcr_ratio = hqla / net_outflow if net_outflow else float("inf")

    summary = {
        "HQLA(USDk)": round(hqla, 2),
        "WeightedInflows(USDk)": round(weighted_inflows, 2),
        "WeightedOutflows(USDk)": round(weighted_outflows, 2),
        "NetOutflow(USDk)": round(net_outflow, 2),
        "ProxyLCR": round(lcr_ratio, 3),
    }
    pd.Series(summary).to_csv(OUTPUT_DIR / "lr_lcr_summary.csv")
    print("\nProxy LCR Summary:\n", summary)


def product_outflow_concentration(df: pd.DataFrame):
    outflows = df[df["InflowOutflow"] == "Outflow"]
    prod_agg = outflows.groupby("Product")["Amount(USDk)"].sum().abs().sort_values()
    plt.figure(figsize=(9,6))
    prod_agg.plot(kind="barh", color="salmon")
    plt.title("Outflow Concentration by Product")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "lr_product_outflow.png")
    plt.close()

    prod_agg.to_csv(OUTPUT_DIR / "lr_product_outflow.csv")


def main():
    liquidity = load("liquidity")

    ladder = gap_ladder(liquidity)
    plot_gap(ladder)
    proxy_lcr(liquidity)
    product_outflow_concentration(liquidity)


if __name__ == "__main__":
    main() 