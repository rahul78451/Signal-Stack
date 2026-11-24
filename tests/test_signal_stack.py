import os
import unittest
import json
from app.database import get_connection, init_db
from app.services.research_service import research_service
from app.services.interview_service import interview_service
from app.services.stack_service import stack_service
from app.services.ranking_service import ranking_service
from app.services.briefing_service import briefing_service
from app.services.file_parser import internal_file_parser
from app.services.audit_service import audit_service

class TestSignalStack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_01_database_tables_exist(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r["name"] for r in cursor.fetchall()]
        conn.close()

        required_tables = ["companies", "interviews", "sources", "competitors", "signals", "intelligence", "briefs", "audit_logs", "action_items"]
        for t in required_tables:
            self.assertIn(t, tables, f"Table {t} missing from database")

    def test_02_company_facts_vs_assumptions(self):
        c = research_service.research_company("TestCorp", "https://testcorp.com", "Testing initial research")
        self.assertIn("verified_facts", c)
        self.assertIn("assumptions", c)
        self.assertIsInstance(c["verified_facts"], list)
        self.assertIsInstance(c["assumptions"], list)
        self.assertTrue(len(c["verified_facts"]) > 0)
        self.assertTrue(len(c["assumptions"]) > 0)

    def test_03_adaptive_interview_lifecycle(self):
        c = research_service.research_company("InterviewCo", "https://interviewco.com")
        cid = c["id"]

        # Initialize
        questions = interview_service.initialize_interview(cid)
        self.assertEqual(len(questions), 10, "Should generate exactly 10 questions")

        # Answer Q1
        state = interview_service.submit_answer(cid, 1, "Monetization is SaaS subscription")
        self.assertEqual(state["answered_count"], 1)

        # Skip Q2 (confidentiality)
        state = interview_service.submit_answer(cid, 2, "", is_skipped=True)
        self.assertEqual(state["answered_count"], 2)

        # Edit Q1
        state = interview_service.edit_answer(cid, 1, "Monetization updated: 80% SaaS, 20% Services")
        q1 = next(q for q in state["questions"] if q["question_index"] == 1)
        self.assertIn("80% SaaS", q1["answer_text"])

    def test_04_signal_stack_4_categories_and_justifications(self):
        c = research_service.research_company("StackCo", "https://stackco.com")
        cid = c["id"]
        stack = stack_service.build_signal_stack(cid)

        # Check 4 categories
        cats = stack["categories"]
        for required_cat in ["customers", "competitors", "market", "internal"]:
            self.assertIn(required_cat, cats)

        # Check justifications on all sources
        all_sources = []
        for s_list in cats.values():
            all_sources.extend(s_list)

        self.assertTrue(len(all_sources) > 0)
        for s in all_sources:
            self.assertTrue(len(s.get("reason_for_inclusion", "")) > 5, f"Source {s['name']} missing reason")

    def test_05_internal_document_parsing(self):
        sample_csv = b"lead_id,stage,objection,drop_reason\nL-101,Visa,Bank collateral refused,Loan reject\nL-102,Deposit,Tuition too expensive,Price sensitivity"
        parsed = internal_file_parser.parse_file("crm_test.csv", sample_csv)
        self.assertEqual(parsed["filename"], "crm_test.csv")
        self.assertTrue(len(parsed["insights"]) >= 1)

    def test_06_ranking_formulation(self):
        signal = {
            "title": "Severe Regulatory Ban on Student Visas Enacted This Week",
            "evidence_snippet": "Immediate ban announced on foreign student dependents",
            "category": "market"
        }
        profile = {"name": "MeetUniversity", "industry": "Higher Education Student Recruitment"}
        scores = ranking_service.calculate_scores(signal, profile, "High")

        self.assertIn("composite_rank", scores)
        self.assertIn("rank_explanation", scores)
        # Should be high priority due to ban and urgency keywords
        self.assertGreaterEqual(scores["composite_rank"], 75.0)

    def test_07_stress_test_context_pivot(self):
        c = research_service.research_company("PivotCo", "https://pivotco.com")
        cid = c["id"]
        stack_service.build_signal_stack(cid)

        pivot_result = stack_service.reassess_for_context_change(
            cid,
            "Pivoting from UK undergraduate admissions to German English-taught master's STEM degrees due to UK visa bans."
        )

        self.assertIn("sources_to_deprecate", pivot_result)
        self.assertIn("recommended_new_sources", pivot_result)
        self.assertIn("strategic_impact_explanation", pivot_result)

    def test_08_monthly_source_audit(self):
        audit_res = audit_service.run_monthly_audit()
        self.assertIn("summary", audit_res)
        self.assertIn("total_audited", audit_res["summary"])
        self.assertIn("healthy_count", audit_res["summary"])

if __name__ == "__main__":
    unittest.main()
