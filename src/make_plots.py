from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from config import EXPERIMENT_SUMMARY_CSV, PROFILE_SUMMARY_CSV, REPORT_FIGURE_DIR, ensure_dirs


def _labels(df: pd.DataFrame) -> list[str]:
    return (df["run_mode"] + "\n" + df["defense_type"]).tolist()


def bar_chart(df: pd.DataFrame, metric: str, ylabel: str, output_name: str) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(_labels(df), df[metric])
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, 1)
    ax.tick_params(axis="x", rotation=35)
    plt.tight_layout()
    fig.savefig(REPORT_FIGURE_DIR / output_name, dpi=200)
    plt.close(fig)


def profile_bar_chart(df: pd.DataFrame, metric: str, ylabel: str, output_name: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.2))
    labels = (df["run_mode"] + "\n" + df["attack_profile"] + "\n" + df["defense_type"]).tolist()
    ax.bar(labels, df[metric])
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, 1)
    ax.tick_params(axis="x", rotation=45)
    plt.tight_layout()
    fig.savefig(REPORT_FIGURE_DIR / output_name, dpi=200)
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
