"""escrow_contract.py - Sovereign Milestone Escrow Contract Generator."""

import hashlib
import json
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


@dataclass
class Milestone:
    index: int
    title: str
    deliverables: List[str]
    acceptance_tests: str
    payout_usd: int
    status: str = "PENDING_RELEASE"  # "PENDING_FUNDING", "LOCKED_IN_ESCROW", "VERIFIED_PASSED", "RELEASED"


@dataclass
class MilestoneContract:
    contract_id: str
    client_name: str
    developer_handle: str
    project_scope: str
    total_budget_usd: int
    milestones: List[Milestone]
    contract_hash: str
    created_at: str


def create_milestone_contract(
    client_name: str,
    developer_handle: str,
    project_scope: str,
    milestone_specs: List[Dict[str, Any]],
) -> MilestoneContract:
    """Generates a tamper-proof bilateral delivery contract.
    Both parties hold cryptographic hashes of deliverables and test acceptance criteria.
    """
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    milestones = []
    total = 0
    for idx, spec in enumerate(milestone_specs, start=1):
        amt = spec.get("payout_usd", 1000)
        total += amt
        milestones.append(
            Milestone(
                index=idx,
                title=spec.get("title", f"Milestone #{idx}"),
                deliverables=spec.get("deliverables", []),
                acceptance_tests=spec.get("acceptance_tests", "pytest && npm test exits 0"),
                payout_usd=amt,
                status="LOCKED_IN_ESCROW",
            )
        )

    cid = hashlib.sha256(f"{client_name}:{developer_handle}:{ts}".encode("utf-8")).hexdigest()[:12]
    c_hash = hashlib.sha256(
        json.dumps([asdict(m) for m in milestones], sort_keys=True).encode("utf-8")
    ).hexdigest()

    return MilestoneContract(
        contract_id=f"TP-ESCROW-{cid.upper()}",
        client_name=client_name,
        developer_handle=developer_handle,
        project_scope=project_scope,
        total_budget_usd=total,
        milestones=milestones,
        contract_hash=c_hash,
        created_at=ts,
    )


def export_contract_markdown(contract: MilestoneContract) -> str:
    """Exports a professional, legally structured technical agreement in Markdown."""
    lines = [
        f"# Bilateral Technical Milestone Agreement (ID: {contract.contract_id})",
        f"**Client / Enterprise Buyer**: {contract.client_name}",
        f"**Lead Software Architect**: @{contract.developer_handle}",
        f"**Total Contract Value**: ${contract.total_budget_usd:,} USD (Milestone-Locked Escrow)",
        f"**Contract Digest SHA-256**: `{contract.contract_hash}`",
        f"**Effective Date**: {contract.created_at}",
        "",
        "---",
        "## 1. Project Purpose & Architecture Scope",
        f"{contract.project_scope}",
        "",
        "## 2. Milestone Verification & Payout Schedule",
    ]

    for m in contract.milestones:
        lines.append(f"### Milestone {m.index}: {m.title} (${m.payout_usd:,} USD)")
        lines.append(f"* **Status**: `{m.status}`")
        lines.append("* **Mandatory Technical Deliverables**:")
        for d in m.deliverables:
            lines.append(f"  - {d}")
        lines.append(f"* **Acceptance Verification Gate**: `{m.acceptance_tests}`")
        lines.append("")

    lines.extend([
        "## 3. Sovereign Escrow Invariant",
        "- Payout releases require deterministic test pass verification and client digital confirmation.",
        "- No arbitrary scope creep permitted after cryptographic hashing without a bilateral addendum.",
        "",
        "---",
        f"*Generated autonomously via TalentProof Protocol Kernel v1.0.0 — https://github.com/Amz34/talentproof-protocol*"
    ])
    return "\n".join(lines)
