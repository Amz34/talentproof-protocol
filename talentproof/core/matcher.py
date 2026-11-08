"""matcher.py - Deterministic Bilateral Compatibility & Trust Index Engine."""

import math
from dataclasses import dataclass
from typing import Dict, List, Any
from talentproof.core.attestation import DevProof


@dataclass
class JobRequisition:
    requisition_id: str
    title: str
    required_skills: Dict[str, float]  # Skill name -> Minimum weight required (0.0 to 1.0)
    budget_milestone_usd: int
    remote_only: bool = True
    min_reputation_score: float = 75.0


@dataclass
class MatchResult:
    developer_handle: str
    requisition_id: str
    compatibility_score: float          # 0.0 to 100.0%
    budget_alignment_status: str       # "OPTIMAL", "WITHIN_RANGE", "EXCEEDS_BUDGET"
    skill_gap_analysis: Dict[str, str]  # Skill -> "SURPLUS", "MATCH", "DEFICIT"
    is_recommended: bool
    summary_reason: str


def match_candidate_to_job(candidate: DevProof, job: JobRequisition) -> MatchResult:
    """Calculates deterministic matching score between candidate proofs and job specs.
    Eliminates manual recruiter bias and opaque ATS guesswork.
    """
    skill_scores = []
    gaps = {}

    for skill, min_req in job.required_skills.items():
        candidate_val = candidate.verified_skills.get(skill, 0.0)
        # Check partial token match if exact key not found
        if candidate_val == 0.0:
            for c_k, c_v in candidate.verified_skills.items():
                if any(part in c_k.lower() for part in skill.lower().split()):
                    candidate_val = c_v
                    break

        if candidate_val >= min_req + 0.10:
            gaps[skill] = "SURPLUS (Verified Lead Level)"
            skill_scores.append(1.0)
        elif candidate_val >= min_req:
            gaps[skill] = "MATCH (Production Ready)"
            skill_scores.append(1.0)
        elif candidate_val > 0.0:
            deficit_pct = int((min_req - candidate_val) * 100)
            gaps[skill] = f"DEFICIT (-{deficit_pct}% gap)"
            skill_scores.append(candidate_val / min_req)
        else:
            gaps[skill] = "UNVERIFIED"
            skill_scores.append(0.0)

    # Base skill compatibility
    avg_skill_fit = (sum(skill_scores) / max(1, len(skill_scores))) * 100.0

    # Reputation gate
    rep_multiplier = min(1.0, candidate.reputation_score / job.min_reputation_score)
    final_compatibility = round(avg_skill_fit * 0.70 + (rep_multiplier * 30.0), 1)

    # Budget alignment
    if candidate.fair_market_rate_usd <= job.budget_milestone_usd:
        budget_status = "OPTIMAL"
    elif candidate.fair_market_rate_usd <= job.budget_milestone_usd * 1.25:
        budget_status = "WITHIN_RANGE"
    else:
        budget_status = "EXCEEDS_BUDGET"

    recommended = final_compatibility >= 80.0 and budget_status in ("OPTIMAL", "WITHIN_RANGE")

    if recommended:
        summary = (
            f"Candidate @{candidate.developer_handle} exceeds production requirements with {final_compatibility}% "
            f"verified compatibility. Rate alignment is {budget_status}."
        )
    else:
        summary = (
            f"Candidate compatibility is {final_compatibility}%. Review skill gap annotations before milestone assignment."
        )

    return MatchResult(
        developer_handle=candidate.developer_handle,
        requisition_id=job.requisition_id,
        compatibility_score=final_compatibility,
        budget_alignment_status=budget_status,
        skill_gap_analysis=gaps,
        is_recommended=recommended,
        summary_reason=summary,
    )
