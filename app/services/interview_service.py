import uuid
import json
import logging
from typing import Dict, Any, List, Optional
from app.database import get_connection
from app.services.ai_service import ai_service
from app.services.research_service import research_service

logger = logging.getLogger("SignalStack.Interview")

class InterviewService:
    def initialize_interview(self, company_id: str) -> List[Dict[str, Any]]:
        """Generate and store the 10-question adaptive interview for a company."""
        company = research_service.get_company(company_id)
        if not company:
            raise ValueError(f"Company {company_id} not found.")

        conn = get_connection()
        cursor = conn.cursor()

        # Check if questions already initialized
        cursor.execute("SELECT * FROM interviews WHERE company_id = ? ORDER BY question_index ASC", (company_id,))
        existing = cursor.fetchall()
        if existing and len(existing) >= 10:
            conn.close()
            return [dict(r) for r in existing]

        # Generate fresh tailored questions
        questions = ai_service.generate_interview_questions(company["name"], company)

        # Clear any partial records
        cursor.execute("DELETE FROM interviews WHERE company_id = ?", (company_id,))

        saved_records = []
        for q in questions[:10]:
            q_id = str(uuid.uuid4())
            idx = q.get("question_index", len(saved_records) + 1)
            text = q.get("question_text", "")
            cat = q.get("context_category", "General")
            hint = q.get("follow_up_hint", "")

            cursor.execute("""
                INSERT INTO interviews (
                    id, company_id, question_index, question_text,
                    context_category, answer_text, is_skipped, follow_up_notes
                ) VALUES (?, ?, ?, ?, ?, '', 0, ?)
            """, (q_id, company_id, idx, text, cat, hint))

            saved_records.append({
                "id": q_id,
                "company_id": company_id,
                "question_index": idx,
                "question_text": text,
                "context_category": cat,
                "answer_text": "",
                "is_skipped": False,
                "follow_up_notes": hint
            })

        conn.commit()
        conn.close()
        return saved_records

    def get_interview_state(self, company_id: str) -> Dict[str, Any]:
        """Return the complete interview state: progress, answers, current question."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM interviews WHERE company_id = ? ORDER BY question_index ASC", (company_id,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        if not rows:
            rows = self.initialize_interview(company_id)

        answered_count = sum(1 for r in rows if r.get("answer_text") or r.get("is_skipped"))
        current_question = None
        for r in rows:
            if not r.get("answer_text") and not r.get("is_skipped"):
                current_question = r
                break

        return {
            "company_id": company_id,
            "total_questions": len(rows),
            "answered_count": answered_count,
            "is_completed": answered_count >= len(rows),
            "current_question": current_question,
            "questions": rows
        }

    def submit_answer(self, company_id: str, question_index: int, answer_text: str, is_skipped: bool = False) -> Dict[str, Any]:
        """Record the answer or skip flag, generate follow-up memory if applicable."""
        conn = get_connection()
        cursor = conn.cursor()

        # Update answer
        cursor.execute("""
            UPDATE interviews
            SET answer_text = ?, is_skipped = ?, updated_at = CURRENT_TIMESTAMP
            WHERE company_id = ? AND question_index = ?
        """, (answer_text, 1 if is_skipped else 0, company_id, question_index))

        conn.commit()
        conn.close()

        # Re-fetch state
        return self.get_interview_state(company_id)

    def edit_answer(self, company_id: str, question_index: int, new_answer: str) -> Dict[str, Any]:
        """Allows the founder to edit or update any answer at any time."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE interviews
            SET answer_text = ?, is_skipped = 0, updated_at = CURRENT_TIMESTAMP
            WHERE company_id = ? AND question_index = ?
        """, (new_answer, company_id, question_index))
        conn.commit()
        conn.close()
        return self.get_interview_state(company_id)

interview_service = InterviewService()
