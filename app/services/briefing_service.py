import os
import uuid
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import REPORTS_DIR
from app.database import get_connection
from app.services.ai_service import ai_service
from app.services.research_service import research_service
from app.services.analysis_service import analysis_service

logger = logging.getLogger("SignalStack.Briefing")

class BriefingService:
    def generate_brief(self, company_id: str) -> Dict[str, Any]:
        """Generate the complete 10-section executive Monday Morning Brief."""
        company = research_service.get_company(company_id)
        if not company:
            raise ValueError(f"Company {company_id} not found")

        # Ensure all pending signals are analyzed first
        analysis_service.process_unanalyzed_signals(company_id)

        # Retrieve analyzed signals
        feed = analysis_service.get_intelligence_feed(company_id)

        # Fetch internal file insights if any
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM signals WHERE company_id = ? AND category = 'internal' ORDER BY discovered_at DESC LIMIT 10", (company_id,))
        internal_rows = [dict(r) for r in cursor.fetchall()]
        internal_insights = [
            {"pattern": r["title"], "source_data": "Internal Input", "sales_objection_or_risk": r["evidence_snippet"], "action": "Review"}
            for r in internal_rows
        ]

        # Generate structured brief via AI engine
        brief_data = ai_service.generate_monday_brief(company["name"], company, feed, internal_insights)

        # Normalize key aliases
        comp_items = brief_data.get("competitor_signals") or brief_data.get("competitor_intelligence", [])
        mkt_items = brief_data.get("market_signals") or brief_data.get("market_intelligence", [])
        brief_data["competitor_signals"] = comp_items
        brief_data["competitor_intelligence"] = comp_items
        brief_data["market_signals"] = mkt_items
        brief_data["market_intelligence"] = mkt_items

        brief_id = str(uuid.uuid4())
        gen_date = datetime.utcnow().strftime("%Y-%m-%d")
        period_label = f"Week of {datetime.utcnow().strftime('%B %d, %Y')}"

        # Render Markdown document
        markdown_content = self._render_markdown(company["name"], period_label, brief_data)

        # Persist brief to DB
        cursor.execute("""
            INSERT INTO briefs (
                id, company_id, brief_title, generation_date, period_label,
                executive_summary, customer_signals, competitor_signals,
                market_signals, internal_signals, opportunities, risks_threats,
                recommended_actions, what_to_watch, source_appendix,
                markdown_content, json_content, is_published
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            brief_id, company_id,
            brief_data.get("brief_title", f"Monday Morning Executive Brief — {company['name']}"),
            gen_date, period_label,
            json.dumps(brief_data.get("executive_summary", [])),
            json.dumps(brief_data.get("customer_signals", [])),
            json.dumps(brief_data.get("competitor_signals", [])),
            json.dumps(brief_data.get("market_signals", [])),
            json.dumps(brief_data.get("internal_signals", [])),
            json.dumps(brief_data.get("opportunities", [])),
            json.dumps(brief_data.get("risks_threats", [])),
            json.dumps(brief_data.get("recommended_actions", [])),
            json.dumps(brief_data.get("what_to_watch", [])),
            json.dumps(brief_data.get("source_appendix", [])),
            markdown_content,
            json.dumps(brief_data)
        ))

        # Persist action items for tracking
        for act in brief_data.get("recommended_actions", []):
            cursor.execute("""
                INSERT INTO action_items (
                    id, brief_id, company_id, action_text, priority, reason, suggested_owner, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
            """, (
                str(uuid.uuid4()), brief_id, company_id,
                act.get("action", ""),
                act.get("priority", "P1"),
                act.get("reason", ""),
                act.get("suggested_owner", "Leadership")
            ))

        conn.commit()
        conn.close()

        # Save markdown report file
        safe_name = company["name"].lower().replace(" ", "_")
        report_file = REPORTS_DIR / f"{safe_name}_brief.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        brief_data["id"] = brief_id
        brief_data["markdown_content"] = markdown_content
        return brief_data

    def get_latest_brief(self, company_id: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM briefs WHERE company_id = ? ORDER BY created_at DESC LIMIT 1", (company_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        data = dict(row)
        for key in ["executive_summary", "customer_signals", "competitor_signals", "market_signals", "internal_signals", "opportunities", "risks_threats", "recommended_actions", "what_to_watch", "source_appendix"]:
            if data.get(key):
                try:
                    data[key] = json.loads(data[key])
                except Exception:
                    data[key] = []
        data["competitor_intelligence"] = data.get("competitor_signals", [])
        data["market_intelligence"] = data.get("market_signals", [])
        return data

    def get_action_items(self, company_id: str) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM action_items WHERE company_id = ? ORDER BY priority ASC, updated_at DESC", (company_id,))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def update_action_status(self, action_id: str, new_status: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE action_items SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_status, action_id))
        conn.commit()
        conn.close()
        return True

    def _render_markdown(self, company_name: str, period: str, data: Dict[str, Any]) -> str:
        lines = []
        lines.append(f"# {data.get('brief_title', f'Monday Morning Executive Brief — {company_name}')}")
        lines.append(f"**Period:** {period} | **Prepared for:** Executive Leadership | **Generated by:** Signal Stack AI Engine\n")
        lines.append("---\n")

        # 1. Executive Summary
        lines.append("## 1. Executive Summary — Top 5 Developments")
        for i, item in enumerate(data.get("executive_summary", [])[:5], 1):
            lines.append(f"### {i}. {item.get('headline', 'Headline')}")
            lines.append(f"- **Evidence:** {item.get('evidence', '')}")
            lines.append(f"- **Business Implication:** {item.get('implication', '')}")
            lines.append(f"- **Priority:** `{item.get('priority', 'Medium')}`\n")

        # 2. Customer Signals
        lines.append("## 2. Customer Signals")
        cust_sigs = data.get("customer_signals", [])
        if not cust_sigs:
            lines.append("*No meaningful developments observed in this category during the current monitoring cycle.*\n")
        else:
            for s in cust_sigs:
                lines.append(f"- **Problem / Need:** {s.get('problem', '')}")
                lines.append(f"  - *Quote / Evidence:* \"{s.get('quote_or_evidence', '')}\"")
                lines.append(f"  - *Sentiment:* {s.get('sentiment', 'Neutral')} | *Implication:* {s.get('implication', '')}\n")

        # 3. Competitor Intelligence
        lines.append("## 3. Competitor Intelligence")
        comp_sigs = data.get("competitor_signals", [])
        if not comp_sigs:
            lines.append("*No meaningful developments observed in this category during the current monitoring cycle.*\n")
        else:
            for c in comp_sigs:
                lines.append(f"- **{c.get('competitor', 'Competitor')}:** {c.get('what_changed', '')}")
                lines.append(f"  - *Evidence:* {c.get('evidence', '')}")
                lines.append(f"  - *Why It Matters:* {c.get('why_it_matters', '')}\n")

        # 4. Market Intelligence
        lines.append("## 4. Market & Regulatory Intelligence")
        mkt_sigs = data.get("market_signals", [])
        if not mkt_sigs:
            lines.append("*No meaningful developments observed in this category during the current monitoring cycle.*\n")
        else:
            for m in mkt_sigs:
                lines.append(f"- **{m.get('development', '')}** (`{m.get('category', 'Regulatory')}`)")
                lines.append(f"  - *Evidence:* {m.get('evidence', '')}")
                lines.append(f"  - *Impact on Company:* {m.get('business_impact', '')}\n")

        # 5. Internal Business Intelligence
        lines.append("## 5. Internal Business Intelligence")
        int_sigs = data.get("internal_signals", [])
        if not int_sigs:
            lines.append("*No meaningful developments observed in this category during the current monitoring cycle.*\n")
        else:
            for int_s in int_sigs:
                lines.append(f"- **Pattern:** {int_s.get('pattern', '')} (*Source: {int_s.get('source_data', 'Internal Logs')}*)")
                lines.append(f"  - *Recorded Objection / Friction:* {int_s.get('sales_objection_or_risk', '')}")
                lines.append(f"  - *Operational Action:* {int_s.get('action', '')}\n")

        # 6. Opportunities Identified
        lines.append("## 6. Actionable Opportunities Identified")
        for opp in data.get("opportunities", []):
            lines.append(f"### 💡 {opp.get('opportunity', 'Opportunity')}")
            lines.append(f"- **Evidence:** {opp.get('evidence', '')}")
            lines.append(f"- **Projected Impact:** {opp.get('projected_impact', '')}")
            lines.append(f"- **Recommended Next Step:** {opp.get('recommended_next_step', '')}")
            lines.append(f"- **Priority:** `{opp.get('priority', 'High')}`\n")

        # 7. Risks & Threats
        lines.append("## 7. Risks & Emerging Threats")
        for r in data.get("risks_threats", []):
            lines.append(f"- **Threat:** {r.get('risk', '')} | **Severity:** `{r.get('severity', 'High')}` | **Urgency:** `{r.get('urgency', 'Immediate')}`")
            lines.append(f"  - *Possible Impact:* {r.get('possible_impact', '')}\n")

        # 8. Recommended Actions for This Week
        lines.append("## 8. Prioritized Actions for This Week")
        lines.append("| Priority | Action Item | Reason & Rationale | Suggested Owner |")
        lines.append("|---|---|---|---|")
        for a in data.get("recommended_actions", []):
            lines.append(f"| **{a.get('priority', 'P1')}** | {a.get('action', '')} | {a.get('reason', '')} | `{a.get('suggested_owner', 'Leadership')}` |")
        lines.append("")

        # 9. What We Should Watch
        lines.append("## 9. What We Should Watch (Early Indicators)")
        for w in data.get("what_to_watch", []):
            lines.append(f"- **Trend:** {w.get('trend', '')}")
            lines.append(f"  - *Trigger Threshold:* {w.get('trigger_threshold', '')}")
            lines.append(f"  - *Why Monitor:* {w.get('why_monitor', '')}\n")

        # 10. Source Appendix
        lines.append("## 10. Source Appendix & Verification Details")
        lines.append("| Source Name | Direct URL | Pub Date | Evidence Snippet | Verification |")
        lines.append("|---|---|---|---|---|")
        for s in data.get("source_appendix", [])[:15]:
            snippet = s.get('snippet', '')[:100].replace('\n', ' ') + '...'
            src_lbl = s.get('source') or 'Public Source'
            lines.append(f"| {src_lbl} | [{src_lbl}]({s.get('direct_link', '#')}) | {s.get('pub_date', 'Recent')} | {snippet} | `{s.get('status', 'Verified')}` |")

        return "\n".join(lines)

briefing_service = BriefingService()
