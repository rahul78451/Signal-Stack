import uuid
import json
import logging
from typing import Dict, Any, List
from app.database import get_connection
from app.services.ai_service import ai_service
from app.services.research_service import research_service

logger = logging.getLogger("SignalStack.Analysis")

class AnalysisService:
    def process_unanalyzed_signals(self, company_id: str) -> int:
        """Finds signals that do not have an intelligence record and analyzes them."""
        company = research_service.get_company(company_id)
        if not company:
            return 0

        conn = get_connection()
        cursor = conn.cursor()

        # Find signals lacking intelligence records
        cursor.execute("""
            SELECT s.*, src.name as source_name, src.credibility_tier, src.reason_for_inclusion
            FROM signals s
            LEFT JOIN sources src ON s.source_id = src.id
            WHERE s.company_id = ? AND s.id NOT IN (SELECT signal_id FROM intelligence WHERE company_id = ?)
            ORDER BY s.discovered_at DESC
        """, (company_id, company_id))
        unprocessed = [dict(r) for r in cursor.fetchall()]

        analyzed_count = 0
        for sig in unprocessed:
            sig_id = sig["id"]
            title = sig["title"]
            evidence = sig["evidence_snippet"] or title
            source_info = {
                "name": sig.get("source_name") or "Public Source",
                "category": sig.get("category") or "market",
                "credibility_tier": sig.get("credibility_tier") or "High"
            }

            analysis = ai_service.analyze_signal(company["name"], company, title, evidence, source_info)

            intel_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO intelligence (
                    id, signal_id, company_id, what_happened, when_it_happened,
                    is_verified, why_it_matters, business_area_affected, impact_type,
                    urgency, strategic_interpretation, recommended_consideration,
                    relevance_score, impact_score, urgency_score, credibility_score,
                    recency_score, novelty_score, composite_rank, rank_explanation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                intel_id, sig_id, company_id,
                analysis.get("what_happened", ""),
                analysis.get("when_it_happened", "Recent"),
                1 if analysis.get("is_verified", True) else 0,
                analysis.get("why_it_matters", ""),
                analysis.get("business_area_affected", "General Operations"),
                analysis.get("impact_type", "neutral"),
                analysis.get("urgency", "medium"),
                analysis.get("strategic_interpretation", ""),
                analysis.get("recommended_consideration", ""),
                analysis.get("relevance_score", 50.0),
                analysis.get("impact_score", 50.0),
                analysis.get("urgency_score", 50.0),
                analysis.get("credibility_score", 50.0),
                analysis.get("recency_score", 50.0),
                analysis.get("novelty_score", 50.0),
                analysis.get("composite_rank", 50.0),
                analysis.get("rank_explanation", "Standard priority.")
            ))
            analyzed_count += 1

        conn.commit()
        conn.close()

        return analyzed_count

    def get_intelligence_feed(self, company_id: str, category: str = None, impact_type: str = None, urgency: str = None) -> List[Dict[str, Any]]:
        """Retrieve chronological intelligence feed with multi-factor filters."""
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT i.*, s.title, s.url, s.evidence_snippet, s.publication_date, s.category, src.name as source_name
            FROM intelligence i
            JOIN signals s ON i.signal_id = s.id
            LEFT JOIN sources src ON s.source_id = src.id
            WHERE i.company_id = ?
        """
        params = [company_id]

        if category and category.lower() != "all":
            query += " AND s.category = ?"
            params.append(category.lower())
        if impact_type and impact_type.lower() != "all":
            query += " AND i.impact_type = ?"
            params.append(impact_type.lower())
        if urgency and urgency.lower() != "all":
            query += " AND i.urgency = ?"
            params.append(urgency.lower())

        query += " ORDER BY i.composite_rank DESC, i.created_at DESC"

        cursor.execute(query, params)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

analysis_service = AnalysisService()
