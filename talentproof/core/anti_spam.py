"""anti_spam.py - Anti-AI-Spam & Submission Authenticity Filter."""

import re
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class AuthenticityReport:
    candidate_identifier: str
    is_authentic: bool
    confidence_score: float             # 0.0 (likely bot/spam) to 1.0 (verified human signal)
    flags: List[str]
    verdict: str


# Hallucinated template buzzwords common in bot applications
CLICHE_PHRASES = [
    r"\bi am writing to express my strong interest\b",
    r"\bi am a seasoned developer with a passion\b",
    r"\bi am excited to apply for this opportunity\b",
    r"\bi am a fast learner\b",
    r"\bi have extensive experience in all aspects\b",
    r"\bharnessing the power of\b",
    r"\bin today's fast-paced digital world\b",
    r"\bas an ai language model\b",
]


def evaluate_submission_authenticity(text: str, github_url: str = "") -> AuthenticityReport:
    """Evaluates an application or proposal text against spam and automated bot patterns.
    Rewards verifiable GitHub links, concrete metric statements, and concise directness.
    """
    clean_text = text.lower()
    flags = []
    score = 1.0

    # 1. Check for AI buzzword cliches
    matched_cliches = 0
    for p in CLICHE_PHRASES:
        if re.search(p, clean_text):
            matched_cliches += 1
            flags.append(f"Generic template pattern detected: '{p.replace(r'\\b', '')}'")

    if matched_cliches >= 2:
        score -= 0.35 * matched_cliches

    # 2. Check for real repository or portfolio links
    has_gh = bool(re.search(r"github\.com/[a-zA-Z0-9.\-_]+", clean_text)) or bool(github_url)
    if not has_gh:
        score -= 0.40
        flags.append("Missing verifiable GitHub repository or code artifact link.")
    else:
        flags.append("Verified GitHub profile / code link attached (+40% trust).")

    # 3. Check for substantive technical details vs vague filler
    tech_signals = len(re.findall(r"\b(api|sql|docker|k8s|python|rust|go|react|node|cache|redis|latency|aws|gcp|oci|ci/cd|test)\b", clean_text))
    if tech_signals >= 3:
        score += 0.15
        flags.append(f"Concrete technical architecture terminology verified ({tech_signals} signals).")
    elif tech_signals == 0:
        score -= 0.25
        flags.append("Zero concrete architecture or technology stack mentions.")

    score = max(0.05, min(1.0, score))
    authentic = score >= 0.70

    verdict = "VERIFIED_AUTHENTIC" if authentic else ("SUSPECTED_AI_SPAM" if score < 0.45 else "NEEDS_MANUAL_REVIEW")

    return AuthenticityReport(
        candidate_identifier=github_url or "Anonymous Applicant",
        is_authentic=authentic,
        confidence_score=round(score, 2),
        flags=flags,
        verdict=verdict,
    )
