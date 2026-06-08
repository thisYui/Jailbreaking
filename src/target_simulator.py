from __future__ import annotations


def target_simulator(category: str, attack_type: str, attacked_prompt: str) -> str:
    if category == "benign":
        return "safe_answer"
    if category == "borderline":
        return "safe_refusal" if attack_type == "injection_style" else "safe_answer"
    if category == "harmful":
        return "safe_refusal" if attack_type == "none" else "unsafe_compliance"
    return "safe_answer"
