from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from config import EXPERIMENT_SUMMARY_CSV, PROFILE_SUMMARY_CSV, REPORT_FIGURE_DIR, ensure_dirs


def _labels(df: pd.DataFrame) -> list[str]:
    return (df["run_mode"] + "\n" + df["defense_type"]).tolist()


def bar_chart(df: pd.DataFrame, metric: str, ylabel: str, output_name: str) -> None:
    label_map = {
        "no_defense": "No defense",
        "input_filter": "Input filter",
        "output_moderation": "Output moderation",
        "defense_in_depth": "Defense in depth",
    }

    plot_df = df.copy()
    plot_df["label"] = plot_df["defense_type"].map(label_map).fillna(plot_df["defense_type"])

    fig, ax = plt.subplots(figsize=(8, 4.8))

    bars = ax.bar(plot_df["label"], plot_df[metric], edgecolor="black", linewidth=0.8)

    for bar, value in zip(bars, plot_df[metric]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.005,
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    ax.set_title("Attack success rate by defense strategy", fontsize=14, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, max(0.16, plot_df[metric].max() * 1.25))
    ax.tick_params(axis="x", rotation=15)
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    plt.tight_layout()
    fig.savefig(REPORT_FIGURE_DIR / output_name, dpi=200, bbox_inches="tight")
    plt.close(fig)


def profile_bar_chart(df: pd.DataFrame, metric: str, ylabel: str, output_name: str) -> None:
    defense_labels = {
        "no_defense": "No defense",
        "input_filter": "Input filter",
        "output_moderation": "Output moderation",
        "defense_in_depth": "Defense in depth",
    }

    profile_labels = {
        "knowledge": "Knowledge",
        "company": "Company",
        "hazardous": "Hazardous",
    }

    plot_df = df.copy()
    plot_df["attack_profile_label"] = (
        plot_df["attack_profile"]
        .map(profile_labels)
        .fillna(plot_df["attack_profile"].astype(str).str.replace("_", " ").str.title())
    )
    plot_df["defense_label"] = (
        plot_df["defense_type"]
        .map(defense_labels)
        .fillna(plot_df["defense_type"].astype(str).str.replace("_", " ").str.title())
    )

    pivot = plot_df.pivot_table(
        index="attack_profile_label",
        columns="defense_label",
        values=metric,
        aggfunc="mean",
    )

    defense_order = [
        "No defense",
        "Input filter",
        "Output moderation",
        "Defense in depth",
    ]
    pivot = pivot[[col for col in defense_order if col in pivot.columns]]

    profile_order = ["Knowledge", "Company", "Hazardous"]
    pivot = pivot.reindex([idx for idx in profile_order if idx in pivot.index])

    fig, ax = plt.subplots(figsize=(9.5, 5.2))

    bars = pivot.plot(
        kind="bar",
        ax=ax,
        width=0.78,
        edgecolor="black",
        linewidth=0.7,
    )

    ax.set_title(f"{ylabel} by attack profile and defense strategy", fontsize=13, fontweight="bold")
    ax.set_xlabel("Attack profile")
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=0)
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    max_value = float(plot_df[metric].max())
    if max_value <= 0.2:
        ax.set_ylim(0, max(0.08, max_value * 1.35))
    elif max_value <= 0.6:
        ax.set_ylim(0, max(0.65, max_value * 1.2))
    else:
        ax.set_ylim(0, 1.0)

    for container in ax.containers:
        ax.bar_label(
            container,
            fmt="%.2f",
            fontsize=8,
            padding=2,
        )

    ax.legend(
        title="Defense type",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=2,
        frameon=True,
    )

    plt.tight_layout()
    fig.savefig(REPORT_FIGURE_DIR / output_name, dpi=200, bbox_inches="tight")
    plt.close(fig)

def safety_utility_tradeoff(df: pd.DataFrame) -> None:
    defense_labels = {
        "no_defense": "No defense",
        "input_filter": "Input filter",
        "output_moderation": "Output moderation",
        "input_output": "Input + output",
    }

    defense_markers = {
        "no_defense": "o",
        "input_filter": "s",
        "output_moderation": "^",
        "input_output": "D",
    }

    fig, ax = plt.subplots(figsize=(8, 5.5))

    for defense_type, group in df.groupby("defense_type"):
        label = defense_labels.get(defense_type, defense_type.replace("_", " ").title())
        marker = defense_markers.get(defense_type, "o")

        ax.scatter(
            group["utility_rate"],
            1 - group["asr"],
            s=140,
            marker=marker,
            edgecolor="black",
            linewidth=0.9,
            label=label,
            alpha=0.9,
        )

    ax.set_title("Safety–Utility trade-off by defense strategy")
    ax.set_xlabel("Utility rate")
    ax.set_ylabel("Safety rate (1 - ASR)")

    # Zoom vào vùng có dữ liệu để dễ đọc hơn
    ax.set_xlim(0.38, 0.66)
    ax.set_ylim(0.84, 1.01)

    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend(title="Defense type", loc="lower left", frameon=True)

    plt.tight_layout()
    fig.savefig(REPORT_FIGURE_DIR / "safety_utility_tradeoff.png", dpi=200)
    plt.close(fig)


def main() -> None:
    ensure_dirs()
    df = pd.read_csv(EXPERIMENT_SUMMARY_CSV)
    bar_chart(df, "asr", "Attack success rate", "asr_by_defense.png")
    bar_chart(df, "orr", "Over-refusal rate", "orr_by_defense.png")
    bar_chart(df, "utility_rate", "Utility rate", "utility_by_defense.png")
    safety_utility_tradeoff(df)
    if PROFILE_SUMMARY_CSV.exists():
        profile_df = pd.read_csv(PROFILE_SUMMARY_CSV)
        profile_bar_chart(profile_df, "asr", "Attack success rate", "asr_by_profile.png")
        profile_bar_chart(profile_df, "orr", "Over-refusal rate", "orr_by_profile.png")
    print(f"Wrote figures to {REPORT_FIGURE_DIR}")


if __name__ == "__main__":
    main()
