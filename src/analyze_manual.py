from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "web_manual_responses.tsv"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "tables"
DETAIL_OUTPUT_PATH = OUTPUT_DIR / "manual_jailbreak_details.csv"
SUMMARY_OUTPUT_PATH = OUTPUT_DIR / "manual_jailbreak_summary.csv"


MANUAL_SOURCE_COLUMNS = [
    "prompts",
    "Meaning",
    "Chatgpt 5.5",
    "Passed_Chatgpt",
    "Claude Haiku 4,5",
    "Passed_Haiku",
    "Gemini 3.1 Flash Lite",
    "Passed_Gemini",
]

MODEL_COLUMNS = {
    "ChatGPT 5.5": {
        "slug": "chatgpt_5_5",
        "response_column": "Chatgpt 5.5",
        "passed_column": "Passed_Chatgpt",
    },
    "Claude Haiku 4.5": {
        "slug": "claude_haiku_4_5",
        "response_column": "Claude Haiku 4,5",
        "passed_column": "Passed_Haiku",
    },
    "Gemini 3.1 Flash Lite": {
        "slug": "gemini_3_1_flash_lite",
        "response_column": "Gemini 3.1 Flash Lite",
        "passed_column": "Passed_Gemini",
    },
}

MANUAL_DETAIL_COLUMNS = [
    "case_id",
    "source_row",
    "model",
    "prompt",
    "meaning",
    "response_text",
    "passed_raw",
    "passed_normalized",
    "has_response",
]

MANUAL_SUMMARY_COLUMNS = [
    "model",
    "total_cases",
    "cases_with_response",
    "missing_response_cases",
    "passed_1_count",
    "passed_0_count",
    "unlabeled_count",
    "passed_1_rate",
    "has_any_passed_1",
]


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def load_manual_file(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Manual TSV file not found: {path}")

    try:
        df = pd.read_csv(
            path,
            sep="\t",
            dtype=str,
            keep_default_na=False,
            encoding="utf-8",
        )
    except pd.errors.ParserError as exc:
        raise ValueError(
            f"Failed to parse manual TSV file {path}. "
            "Ensure the file uses real tab characters and multiline fields are quoted correctly."
        ) from exc

    df.columns = df.columns.str.strip()
    missing = [column for column in MANUAL_SOURCE_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in {path}: {', '.join(missing)}")

    return df[MANUAL_SOURCE_COLUMNS].copy()


def normalize_passed(value: object) -> int | None:
    text = str(value).strip().lower()
    if text in {"1", "1.0", "true", "yes"}:
        return 1
    if text in {"0", "0.0", "false", "no"}:
        return 0
    return None


def build_manual_details(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for source_row, record in enumerate(df.to_dict("records"), start=1):
        for model, columns in MODEL_COLUMNS.items():
            response_text = record[columns["response_column"]]
            passed_raw = record[columns["passed_column"]]
            rows.append(
                {
                    "case_id": f"M{source_row:04d}_{columns['slug']}",
                    "source_row": source_row,
                    "model": model,
                    "prompt": record["prompts"],
                    "meaning": record["Meaning"],
                    "response_text": response_text,
                    "passed_raw": passed_raw,
                    "passed_normalized": normalize_passed(passed_raw),
                    "has_response": bool(str(response_text).strip()),
                }
            )

    details_df = pd.DataFrame(rows, columns=MANUAL_DETAIL_COLUMNS)
    details_df["passed_normalized"] = pd.array(details_df["passed_normalized"], dtype="Int64")
    return details_df


def build_manual_summary(details_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for model in MODEL_COLUMNS:
        model_df = details_df[details_df["model"] == model]
        total_cases = int(len(model_df))
        cases_with_response = int(model_df["has_response"].sum())
        passed_1_count = int((model_df["passed_normalized"] == 1).sum())
        passed_0_count = int((model_df["passed_normalized"] == 0).sum())
        unlabeled_count = int(model_df["passed_normalized"].isna().sum())
        labeled_count = passed_1_count + passed_0_count
        rows.append(
            {
                "model": model,
                "total_cases": total_cases,
                "cases_with_response": cases_with_response,
                "missing_response_cases": total_cases - cases_with_response,
                "passed_1_count": passed_1_count,
                "passed_0_count": passed_0_count,
                "unlabeled_count": unlabeled_count,
                "passed_1_rate": passed_1_count / labeled_count if labeled_count else 0.0,
                "has_any_passed_1": passed_1_count > 0,
            }
        )

    return pd.DataFrame(rows, columns=MANUAL_SUMMARY_COLUMNS)


def save_manual_outputs(details_df: pd.DataFrame, summary_df: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    details_df.to_csv(DETAIL_OUTPUT_PATH, index=False, encoding="utf-8")
    summary_df.to_csv(SUMMARY_OUTPUT_PATH, index=False, encoding="utf-8")


def main() -> None:
    source_df = load_manual_file(INPUT_PATH)
    details_df = build_manual_details(source_df)
    summary_df = build_manual_summary(details_df)
    save_manual_outputs(details_df, summary_df)

    print(f"Loaded {len(source_df)} manual source rows from {_display_path(INPUT_PATH)}")
    print(f"Created {len(details_df)} prompt-model detail rows")
    print("\nManual evaluation summary")
    print(summary_df.to_string(index=False))
    print(f"\nWrote manual details to {_display_path(DETAIL_OUTPUT_PATH)}")
    print(f"Wrote manual summary to {_display_path(SUMMARY_OUTPUT_PATH)}")
    print(
        "\nNote: Passed_* values are reported as provided and are not interpreted as "
        "unsafe_compliance or safe_refusal."
    )


if __name__ == "__main__":
    main()
