"""TalentProof Protocol - Sovereign 2-Way Developer Proof & Recruiter Escrow Kernel."""

__version__ = "1.0.0"
__author__ = "Aamir Zameer [Az.] <https://github.com/Amz34>"

from talentproof.core.attestation import generate_dev_proof, DevProof
from talentproof.core.matcher import match_candidate_to_job, MatchResult
from talentproof.core.escrow_contract import create_milestone_contract, MilestoneContract
from talentproof.core.anti_spam import evaluate_submission_authenticity

__all__ = [
    "generate_dev_proof",
    "DevProof",
    "match_candidate_to_job",
    "MatchResult",
    "create_milestone_contract",
    "MilestoneContract",
    "evaluate_submission_authenticity",
]
