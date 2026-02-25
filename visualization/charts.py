import matplotlib.pyplot as plt
import numpy as np

def plot_actual_vs_recommended(opt_df, actual_df):
    df = opt_df.copy()
    df["actual"] = actual_df["actual_share"]
    df = df.sort_values("opt_share")

    y = np.arange(len(df))
    fig, ax = plt.subplots(figsize=(10,6))
    ax.barh(y-0.2, df["actual"], height=0.4, label="Actual")
    ax.barh(y+0.2, df["opt_share"], height=0.4, label="Recommended")
    ax.set_yticks(y)
    ax.set_yticklabels(df.index)
    ax.set_xlabel("Share (%)")
    ax.legend()
    plt.tight_layout()
    return fig


def plot_cost_contribution(opt_df):
    df = opt_df.sort_values("cost_rs_per_thm")
    fig, ax = plt.subplots(figsize=(8,6))
    ax.barh(df.index, df["cost_rs_per_thm"])
    ax.set_xlabel("₹ / tHM")
    ax.set_title("Cost Contribution")
    plt.tight_layout()
    return fig


def plot_daily_trend(history_df, col, title):
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(history_df["date"], history_df[col], marker="o")
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel(col)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

def plot_recommended_blend(opt_df):
    """
    Horizontal bar chart of recommended blend (%),
    colored by vendor class (CORE / FLEX / PENALTY)
    """

    # Sort for better readability
    df = opt_df.sort_values("opt_share", ascending=True)

    color_map = {
        "CORE": "#1f77b4",      # blue
        "FLEX": "#2ca02c",      # green
        "PENALTY": "#d62728",   # red
    }

    colors = df["vendor_class"].map(color_map)

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.barh(
        df.index,
        df["opt_share"],
        color=colors
    )

    ax.set_xlabel("Recommended Share (%)")
    ax.set_title("Recommended Blend Mix")

    # Add value labels
    for i, v in enumerate(df["opt_share"]):
        ax.text(v + 0.5, i, f"{v:.1f}%", va="center")

    plt.tight_layout()
    return fig