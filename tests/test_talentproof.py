"""Unit and integration tests for TalentProof Protocol."""

import unittest
from talentproof.core.attestation import generate_dev_proof, compute_proof_hash, render_svg_badge
from talentproof.core.matcher import match_candidate_to_job, JobRequisition
from talentproof.core.escrow_contract import create_milestone_contract, export_contract_markdown
from talentproof.core.anti_spam import evaluate_submission_authenticity


class TestTalentProofProtocol(unittest.TestCase):
    def test_proof_generation_and_hash_integrity(self):
        p = generate_dev_proof("Amz34", total_commits=1200, has_ci_cd=True, has_test_suites=True)
        self.assertEqual(p.developer_handle, "Amz34")
        self.assertGreaterEqual(p.reputation_score, 75.0)
        self.assertGreater(p.fair_market_rate_usd, 2500)
        self.assertTrue(len(p.public_proof_hash) == 64)
        
        # Verify SVG badge renders properly
        svg = render_svg_badge(p)
        self.assertIn("<svg", svg)
        self.assertIn("TalentProof Protocol Verified", svg)
        self.assertIn("@Amz34", svg)

    def test_anti_spam_rejection_of_generic_bots(self):
        bot_text = (
            "Dear Hiring Team, I am writing to express my strong interest in this position. "
            "In today's fast-paced digital world, I am a seasoned developer with a passion."
        )
        report = evaluate_submission_authenticity(bot_text)
        self.assertFalse(report.is_authentic)
        self.assertEqual(report.verdict, "SUSPECTED_AI_SPAM")
        self.assertLess(report.confidence_score, 0.50)

    def test_anti_spam_approval_of_authentic_developer(self):
        dev_text = (
            "Hey! Built production microservices with Python, Redis caching, and Docker. "
            "Check my architecture benchmarks and PRs at github.com/Amz34/hyper-scrape. "
            "Reduced p99 database query latency from 850ms to 42ms."
        )
        report = evaluate_submission_authenticity(dev_text, github_url="https://github.com/Amz34/hyper-scrape")
        self.assertTrue(report.is_authentic)
        self.assertEqual(report.verdict, "VERIFIED_AUTHENTIC")
        self.assertGreaterEqual(report.confidence_score, 0.70)

    def test_bilateral_matching_logic(self):
        proof = generate_dev_proof("Amz34")
        job = JobRequisition(
            requisition_id="REQ-TEST-1",
            title="Senior Systems Architect",
            required_skills={"Python": 0.85, "TypeScript / React": 0.80},
            budget_milestone_usd=5000,
        )
        result = match_candidate_to_job(proof, job)
        self.assertGreaterEqual(result.compatibility_score, 80.0)
        self.assertTrue(result.is_recommended)
        self.assertIn(result.budget_alignment_status, ["OPTIMAL", "WITHIN_RANGE"])

    def test_milestone_escrow_contract(self):
        contract = create_milestone_contract(
            client_name="Global Capital Ventures",
            developer_handle="Amz34",
            project_scope="Deploy sovereign AI agent tool-calling pipeline",
            milestone_specs=[
                {"title": "Architecture Setup", "deliverables": ["IaC scripts"], "payout_usd": 1500},
                {"title": "Production Deployment", "deliverables": ["Docker swarm"], "payout_usd": 2500},
            ]
        )
        self.assertEqual(contract.total_budget_usd, 4000)
        self.assertEqual(len(contract.milestones), 2)
        self.assertTrue(contract.contract_id.startswith("TP-ESCROW-"))
        
        md = export_contract_markdown(contract)
        self.assertIn("# Bilateral Technical Milestone Agreement", md)
        self.assertIn("$4,000 USD", md)


if __name__ == "__main__":
    unittest.main()
