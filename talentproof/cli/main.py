"""main.py - Interactive CLI for TalentProof Protocol."""

import argparse
import json
import sys
from talentproof.core.attestation import generate_dev_proof, render_svg_badge
from talentproof.core.matcher import match_candidate_to_job, JobRequisition
from talentproof.core.escrow_contract import create_milestone_contract, export_contract_markdown
from talentproof.core.anti_spam import evaluate_submission_authenticity


def run_demo():
    print("=" * 65)
    print("  TALENTPROOF PROTOCOL (Kernel v1.0.0)")
    print("  Decoupled 2-Way Developer Proof & Recruiter Escrow Engine")
    print("=" * 65)

    print("\n[STEP 1] Generating Cryptographic DevProof for @Amz34...")
    proof = generate_dev_proof("Amz34", total_commits=1420, has_ci_cd=True, has_test_suites=True)
    print(f"  • Developer Handle    : @{proof.developer_handle}")
    print(f"  • Composite Trust Index: {proof.reputation_score} / 100")
    print(f"  • Fair Market USD Rate : ${proof.fair_market_rate_usd:,} USD / month")
    print(f"  • Tamper-Evident SHA256: {proof.public_proof_hash}")

    print("\n[STEP 2] Simulating Requisition Rejection of AI-Spam Applicant...")
    spam_text = (
        "Dear Hiring Manager, I am writing to express my strong interest in this opportunity. "
        "In today's fast-paced digital world, I am a seasoned developer with a passion for excellence."
    )
    spam_rep = evaluate_submission_authenticity(spam_text)
    print(f"  • Submission Verdict   : {spam_rep.verdict} (Confidence: {int(spam_rep.confidence_score * 100)}%)")
    print(f"  • Filter Action        : Automatically blocked from recruiter pipeline.")

    print("\n[STEP 3] Simulating Requisition Matching for Enterprise E-Commerce Spec...")
    job = JobRequisition(
        requisition_id="REQ-ECOM-2026",
        title="High-Scale Mobile & Web E-Commerce Storefront",
        required_skills={
            "Python": 0.85,
            "TypeScript / React": 0.85,
            "Cloud Architecture / IaC": 0.80,
        },
        budget_milestone_usd=5000,
    )
    match = match_candidate_to_job(proof, job)
    print(f"  • Compatibility Score  : {match.compatibility_score}%")
    print(f"  • Budget Status        : {match.budget_alignment_status}")
    print(f"  • Recommendation       : {'APPROVED FOR HIRING' if match.is_recommended else 'FLAGGED'}")

    print("\n[STEP 4] Generating Bilateral Milestone Escrow Contract...")
    contract = create_milestone_contract(
        client_name="Apex Retail International",
        developer_handle="Amz34",
        project_scope="Engineer end-to-end multi-channel commerce platform with mobile apps and payment gateway.",
        milestone_specs=[
            {
                "title": "Core Architecture & Data Schema",
                "deliverables": ["Modular backend API", "Postgres schemas", "CI pipeline"],
                "acceptance_tests": "pytest tests/ --cov=85",
                "payout_usd": 2000,
            },
            {
                "title": "Mobile App & Checkout Engine",
                "deliverables": ["Flutter cross-platform app", "Stripe payment integration"],
                "acceptance_tests": "flutter test && npm run test:e2e exits 0",
                "payout_usd": 3000,
            },
        ],
    )
    print(f"  • Contract ID          : {contract.contract_id}")
    print(f"  • Total Escrow Value   : ${contract.total_budget_usd:,} USD")
    print(f"  • Milestone Count      : {len(contract.milestones)}")
    print(f"  • Cryptographic Hash   : {contract.contract_hash}")
    print("\n[SUCCESS] TalentProof kernel execution passed with zero errors.")


def main():
    parser = argparse.ArgumentParser(description="TalentProof Protocol CLI")
    subparsers = parser.add_subparsers(dest="command")

    demo_parser = subparsers.add_parser("demo", help="Run end-to-end interactive simulation")
    
    proof_parser = subparsers.add_parser("proof", help="Generate DevProof for a GitHub handle")
    proof_parser.add_argument("handle", help="GitHub username")
    proof_parser.add_argument("--svg", action="store_true", help="Print SVG badge markup")

    contract_parser = subparsers.add_parser("contract", help="Generate milestone agreement")
    contract_parser.add_argument("--client", required=True, help="Client organization name")
    contract_parser.add_argument("--dev", required=True, help="Developer GitHub handle")
    contract_parser.add_argument("--scope", default="High-scale engineering sprint", help="Project scope")
    contract_parser.add_argument("--budget", type=int, default=3000, help="Total milestone budget in USD")

    subparsers.add_parser("serve", help="Launch local web UI dashboard")

    args = parser.parse_args()

    if args.command == "demo" or not args.command:
        run_demo()
    elif args.command == "proof":
        p = generate_dev_proof(args.handle)
        if args.svg:
            print(render_svg_badge(p))
        else:
            print(json.dumps(p.__dict__, indent=2))
    elif args.command == "contract":
        c = create_milestone_contract(
            client_name=args.client,
            developer_handle=args.dev,
            project_scope=args.scope,
            milestone_specs=[
                {"title": "Initial Delivery Sprint", "deliverables": ["Architecture & API"], "payout_usd": args.budget}
            ]
        )
        print(export_contract_markdown(c))
    elif args.command == "serve":
        from talentproof.web.server import start_web_server
        start_web_server()


if __name__ == "__main__":
    main()
