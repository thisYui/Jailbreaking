from __future__ import annotations

from pathlib import Path

import pandas as pd

from attack_transforms import apply_attack, get_attack_profile
from config import ATTACK_TYPES, DEFENSE_TYPES, FINAL_LABELS, WEB_MANUAL_EXPORT_CSV
from evaluator import infer_label_from_response


WEB_MANUAL_COLUMNS = [
    "id",
    "category",
    "attack_type",
    "attack_profile",
    "defense_type",
    "expected_behavior",
    "risk_type",
    "prompt",
    "attacked_prompt",
    "response_text",
    "manual_label",
    "notes",
]

# The custom TSV file at data/web_manual_responses.tsv does not use this legacy
# experiment schema. Analyze it with: python src/analyze_manual.py


def export_web_manual_prompts(prompts_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for record in prompts_df.to_dict("records"):
        for attack_type in ATTACK_TYPES:
            attack_profile = get_attack_profile(record["category"], record["risk_type"])
            rows.append(
                {
                    "id": record["id"],
                    "category": record["category"],
                    "attack_type": attack_type,
                    "attack_profile": attack_profile,
                    "defense_type": "no_defense",
                    "expected_behavior": record["expected_behavior"],
                    "risk_type": record["risk_type"],
                    "prompt": record["prompt"],
                    "attacked_prompt": apply_attack(
                        record["prompt"],
                        attack_type,
                        category=record["category"],
                        risk_type=record["risk_type"],
                    ),
                    "response_text": "",
                    "manual_label": "",
                    "notes": record.get("notes", ""),
                }
            )
    df = pd.DataFrame(rows, columns=WEB_MANUAL_COLUMNS)
    df.to_csv(WEB_MANUAL_EXPORT_CSV, index=False)
    return df


def load_web_manual_responses(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path).fillna("")
    if "attack_profile" not in df.columns:
        df["attack_profile"] = df.apply(
            lambda row: get_attack_profile(row.get("category", ""), row.get("risk_type", "")),
            axis=1,
        )
    missing = [column for column in WEB_MANUAL_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {path}: {', '.join(missing)}")
    df = df[WEB_MANUAL_COLUMNS].copy()
    bad_attacks = sorted(set(df["attack_type"]) - set(ATTACK_TYPES))
    bad_defenses = sorted(set(df["defense_type"]) - set(DEFENSE_TYPES))
    labels = {label for label in df["manual_label"] if label}
    bad_labels = sorted(labels - FINAL_LABELS)
    if bad_attacks:
        raise ValueError(f"Invalid attack_type values in {path}: {', '.join(bad_attacks)}")
    if bad_defenses:
        raise ValueError(f"Invalid defense_type values in {path}: {', '.join(bad_defenses)}")
    if bad_labels:
        raise ValueError(f"Invalid manual_label values in {path}: {', '.join(bad_labels)}")
    df["model_label"] = df.apply(
        lambda row: row["manual_label"].strip()
        or infer_label_from_response(row["response_text"], row["expected_behavior"]),
        axis=1,
    )
    return df
