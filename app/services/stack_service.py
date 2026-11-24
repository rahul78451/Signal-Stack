import uuid
import json
import logging
from typing import Dict, Any, List, Optional
from app.database import get_connection
from app.services.ai_service import ai_service
from app.services.research_service import research_service

logger = logging.getLogger("SignalStack.Stack")

class StackService:
    def build_signal_stack(self, company_id: str) -> Dict[str, Any]:
        """Generate and persist the 4 categories of Signal Stack + Competitors."""
        company = research_service.get_company(company_id)
        if not company:
            raise ValueError(f"Company {company_id} not found.")

        conn = get_connection()
        cursor = conn.cursor()

        # Fetch founder interview answers if available
        cursor.execute("SELECT question_text, answer_text, is_skipped FROM interviews WHERE company_id = ?", (company_id,))
        answers = [dict(r) for r in cursor.fetchall()]

        # Generate stack from AI engine
        stack_data = ai_service.generate_signal_stack(company["name"], company, answers)

        # Insert Competitors
        competitors = stack_data.get("competitors", [])
        for comp in competitors:
            # Check if competitor exists
            cursor.execute("SELECT id FROM competitors WHERE company_id = ? AND LOWER(name) = ?", (company_id, comp["name"].lower()))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO competitors (
                        id, company_id, name, website, relationship,
                        core_offerings, pricing_model, positioning, threat_level,
                        reason_it_matters
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()), company_id, comp.get("name", "Competitor"),
                    comp.get("website", "https://example.com"),
                    comp.get("relationship", "Direct"),
                    comp.get("core_offerings", ""),
                    comp.get("pricing_model", "Subscription / Commission"),
                    comp.get("positioning", ""),
                    comp.get("threat_level", "Medium"),
                    comp.get("reason_it_matters", "Competes directly for target audience.")
                ))

        # Insert Sources
        sources = stack_data.get("sources", [])
        for src in sources:
            cursor.execute("SELECT id FROM sources WHERE company_id = ? AND LOWER(url) = ?", (company_id, src["url"].lower()))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO sources (
                        id, company_id, category, name, url,
                        source_type, reason_for_inclusion, credibility_tier,
                        recency_expectation, is_approved, is_active, last_status, health_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, 'healthy', 100)
                """, (
                    str(uuid.uuid4()), company_id,
                    src.get("category", "market"),
                    src.get("name", "Source"),
                    src.get("url", ""),
                    src.get("source_type", "rss"),
                    src.get("reason_for_inclusion", "Specific monitoring rationale."),
                    src.get("credibility_tier", "High"),
                    src.get("recency_expectation", "Daily")
                ))

        conn.commit()
        conn.close()

        return self.get_stack(company_id)

    def get_stack(self, company_id: str) -> Dict[str, Any]:
        """Retrieve the Signal Stack grouped by category and competitors."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sources WHERE company_id = ? ORDER BY created_at ASC", (company_id,))
        source_rows = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM competitors WHERE company_id = ? ORDER BY threat_level DESC", (company_id,))
        comp_rows = [dict(r) for r in cursor.fetchall()]

        conn.close()

        grouped_sources = {
            "customers": [],
            "competitors": [],
            "market": [],
            "internal": []
        }
        for s in source_rows:
            cat = s.get("category", "market").lower()
            if cat in grouped_sources:
                grouped_sources[cat].append(s)
            else:
                grouped_sources["market"].append(s)

        return {
            "company_id": company_id,
            "total_sources": len(source_rows),
            "approved_sources": sum(1 for s in source_rows if s.get("is_approved")),
            "active_sources": sum(1 for s in source_rows if s.get("is_active")),
            "categories": grouped_sources,
            "competitors": comp_rows
        }

    def add_custom_source(self, company_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Manually add a justified source to the company's Signal Stack."""
        conn = get_connection()
        cursor = conn.cursor()
        src_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO sources (
                id, company_id, category, name, url,
                source_type, reason_for_inclusion, credibility_tier,
                recency_expectation, is_approved, is_active, last_status, health_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, 'healthy', 100)
        """, (
            src_id, company_id,
            data.get("category", "market"),
            data.get("name", "Custom Source"),
            data.get("url", ""),
            data.get("source_type", "rss"),
            data.get("reason_for_inclusion", "Explicitly added by user."),
            data.get("credibility_tier", "High"),
            data.get("recency_expectation", "Daily")
        ))

        conn.commit()
        conn.close()
        return {"id": src_id, "status": "added"}

    def remove_source(self, source_id: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sources WHERE id = ?", (source_id,))
        conn.commit()
        conn.close()
        return True

    def toggle_source_active(self, source_id: str) -> Dict[str, Any]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT is_active FROM sources WHERE id = ?", (source_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return {"error": "Not found"}

        new_val = 0 if row["is_active"] else 1
        cursor.execute("UPDATE sources SET is_active = ? WHERE id = ?", (new_val, source_id))
        conn.commit()
        conn.close()
        return {"id": source_id, "is_active": bool(new_val)}

    def reassess_for_context_change(self, company_id: str, new_context: str) -> Dict[str, Any]:
        """Re-assess stack on business context change (Stress test requirement)."""
        company = research_service.get_company(company_id)
        if not company:
            raise ValueError("Company not found")

        current_stack = self.get_stack(company_id)
        all_sources = []
        for cat_list in current_stack["categories"].values():
            all_sources.extend(cat_list)

        reassessment = ai_service.reassess_stack_on_context_change(company["name"], all_sources, new_context)

        # Update company context notes in database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE companies SET context_notes = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (
            f"STRATEGIC PIVOT / REVISED CONTEXT: {new_context}", company_id
        ))

        # Add newly recommended sources
        for rec in reassessment.get("recommended_new_sources", []):
            cursor.execute("SELECT id FROM sources WHERE company_id = ? AND LOWER(name) = ?", (company_id, rec["name"].lower()))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO sources (
                        id, company_id, category, name, url,
                        source_type, reason_for_inclusion, credibility_tier,
                        recency_expectation, is_approved, is_active, last_status, health_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'High', 'Daily', 1, 1, 'healthy', 100)
                """, (
                    str(uuid.uuid4()), company_id,
                    rec.get("category", "market"),
                    rec.get("name", "New Source"),
                    rec.get("url", "https://news.google.com"),
                    rec.get("source_type", "rss"),
                    rec.get("reason_for_inclusion", "Added following strategic context pivot.")
                ))

        # Flag deprecated sources
        for dep in reassessment.get("sources_to_deprecate", []):
            name_pattern = f"%{dep.get('source_name', '').strip()}%"
            cursor.execute("""
                UPDATE sources SET is_active = 0, health_score = 40, last_status = 'declining_relevance',
                reason_for_inclusion = reason_for_inclusion || ' [DEPRECATED: Declining relevance after strategic pivot]'
                WHERE company_id = ? AND name LIKE ?
            """, (company_id, name_pattern))

        conn.commit()
        conn.close()

        reassessment["updated_stack"] = self.get_stack(company_id)
        return reassessment

stack_service = StackService()
