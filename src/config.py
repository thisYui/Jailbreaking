from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


ATTACK_TYPES = ["none", "role_play", "obfuscation", "multi_turn_simulation", "injection_style"]
ATTACK_PROFILES = ["knowledge", "company", "hazardous", "generic"]
DEFENSE_TYPES = ["no_defense", "input_filter", "output_moderation", "defense_in_depth"]
RUN_MODES = ["simulator", "google_api", "web_manual"]

ALLOWED_CATEGORIES = {"benign", "harmful", "borderline"}
ALLOWED_EXPECTED_BEHAVIORS = {"answer", "refuse"}
FINAL_LABELS = {
    "safe_answer",
    "safe_refusal",
    "unsafe_compliance",
    "blocked_by_input_guard",
    "blocked_by_output_guard",
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
REPORT_TABLE_DIR = PROJECT_ROOT / "reports" / "tables"
REPORT_FIGURE_DIR = PROJECT_ROOT / "reports" / "figures"

INPUT_CSV = DATA_DIR / "prompts.csv"
WEB_MANUAL_RESPONSES_CSV = DATA_DIR / "web_manual_responses.csv"
ATTACKED_PROMPTS_CSV = OUTPUT_DIR / "attacked_prompts.csv"
DETAILED_RESULTS_CSV = OUTPUT_DIR / "detailed_results.csv"
RAW_LOGS_JSONL = OUTPUT_DIR / "raw_logs.jsonl"
GOOGLE_API_RAW_RESPONSES_JSONL = OUTPUT_DIR / "google_api_raw_responses.jsonl"
WEB_MANUAL_EXPORT_CSV = OUTPUT_DIR / "web_manual_export.csv"
EXPERIMENT_SUMMARY_CSV = REPORT_TABLE_DIR / "experiment_summary.csv"
ATTACK_SUMMARY_CSV = REPORT_TABLE_DIR / "attack_summary.csv"
DEFENSE_SUMMARY_CSV = REPORT_TABLE_DIR / "defense_summary.csv"
PROFILE_SUMMARY_CSV = REPORT_TABLE_DIR / "profile_summary.csv"
ERROR_CASES_CSV = REPORT_TABLE_DIR / "error_cases.csv"


def ensure_dirs() -> None:
    for path in (DATA_DIR, OUTPUT_DIR, REPORT_TABLE_DIR, REPORT_FIGURE_DIR):
        path.mkdir(parents=True, exist_ok=True)


def load_env() -> bool:
    return load_dotenv(PROJECT_ROOT / ".env")


def get_run_mode_from_args_or_env(default: str = "simulator") -> str:
    mode = os.getenv("RUN_MODE", default)
    if mode not in RUN_MODES:
        raise ValueError(f"Invalid RUN_MODE '{mode}'. Expected one of: {', '.join(RUN_MODES)}")
    return mode
