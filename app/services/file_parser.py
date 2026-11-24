import os
import re
import csv
import io
import fitz # PyMuPDF
import pandas as pd
from typing import Dict, Any, List

class InternalFileParser:
    """Parses internal business documents (CSV, Excel, PDF, TXT) to extract customer signals."""

    def parse_file(self, filename: str, content_bytes: bytes) -> Dict[str, Any]:
        ext = os.path.splitext(filename)[1].lower()
        extracted_text = ""
        insights = []

        if ext == ".csv":
            extracted_text, insights = self._parse_csv(content_bytes)
        elif ext in [".xlsx", ".xls"]:
            extracted_text, insights = self._parse_excel(content_bytes)
        elif ext == ".pdf":
            extracted_text, insights = self._parse_pdf(content_bytes)
        elif ext in [".txt", ".log", ".json"]:
            extracted_text, insights = self._parse_text(content_bytes)
        else:
            extracted_text = content_bytes.decode("utf-8", errors="ignore")[:5000]
            insights = [{"pattern": "Unstructured Internal Input", "source_data": filename, "sales_objection_or_risk": extracted_text[:300], "action": "Review manually"}]

        return {
            "filename": filename,
            "char_count": len(extracted_text),
            "sample_content": extracted_text[:1000],
            "insights": insights
        }

    def _parse_csv(self, content_bytes: bytes) -> tuple:
        text_stream = io.StringIO(content_bytes.decode("utf-8", errors="ignore"))
        reader = csv.DictReader(text_stream)
        rows = list(reader)

        insights = []
        full_text = []
        for r in rows[:100]:
            full_text.append(" | ".join([f"{k}: {v}" for k, v in r.items() if v]))
            # Heuristics for common CRM drop-off / objection columns
            objection = r.get("objection") or r.get("lost_reason") or r.get("drop_reason") or r.get("notes") or r.get("feedback")
            lead = r.get("lead_name") or r.get("student_id") or r.get("deal_id") or "Lead"
            if objection:
                insights.append({
                    "pattern": f"Recorded Drop/Objection: {lead}",
                    "source_data": "Internal CSV CRM export",
                    "sales_objection_or_risk": str(objection).strip(),
                    "action": "Address friction point in sales / counseling protocol"
                })

        if not insights and rows:
            insights.append({
                "pattern": f"Parsed {len(rows)} structured CRM records",
                "source_data": "CSV Export",
                "sales_objection_or_risk": f"Total rows: {len(rows)}. Columns: {list(rows[0].keys()) if rows else []}",
                "action": "Analyze stage-by-stage drop-off conversion rates"
            })

        return "\n".join(full_text[:50]), insights[:10]

    def _parse_excel(self, content_bytes: bytes) -> tuple:
        df = pd.read_excel(io.BytesIO(content_bytes))
        insights = []
        full_text = []

        cols = [str(c).lower() for c in df.columns]
        for idx, row in df.head(50).iterrows():
            row_dict = row.to_dict()
            full_text.append(str(row_dict))
            for k, v in row_dict.items():
                if any(kw in str(k).lower() for kw in ["reason", "objection", "churn", "feedback", "issue"]) and pd.notna(v):
                    insights.append({
                        "pattern": f"Excel Record #{idx + 1} ({k})",
                        "source_data": "Internal Excel Report",
                        "sales_objection_or_risk": str(v),
                        "action": "Investigate root cause in operational flow"
                    })

        return "\n".join(full_text[:30]), insights[:10]

    def _parse_pdf(self, content_bytes: bytes) -> tuple:
        doc = fitz.open(stream=content_bytes, filetype="pdf")
        text_pages = []
        for i in range(min(len(doc), 10)):
            text_pages.append(doc[i].get_text())

        full_text = "\n".join(text_pages)
        insights = self._extract_text_insights(full_text, "Internal PDF Document")
        return full_text[:4000], insights

    def _parse_text(self, content_bytes: bytes) -> tuple:
        full_text = content_bytes.decode("utf-8", errors="ignore")
        insights = self._extract_text_insights(full_text, "Sales & Support Transcripts")
        return full_text[:4000], insights

    def _extract_text_insights(self, text: str, source_label: str) -> List[Dict[str, Any]]:
        insights = []
        lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 20]

        patterns = [
            (r"(objection|complaint|refused|rejected|too expensive|can't afford|delay|unclear|dropped|switch)", "Customer Objection / Lost Deal"),
            (r"(feature request|need|wish|missing|should add|integrate|dashboard)", "Product / Service Request"),
            (r"(risk|warning|competitor|leaving for|went with)", "Competitor Risk / Flight")
        ]

        for line in lines:
            for regex, category in patterns:
                if re.search(regex, line, re.IGNORECASE):
                    insights.append({
                        "pattern": category,
                        "source_data": source_label,
                        "sales_objection_or_risk": line[:250],
                        "action": "Incorporate feedback into counselor training or product roadmap"
                    })
                    break
            if len(insights) >= 8:
                break

        return insights

internal_file_parser = InternalFileParser()
