import uuid
import json
import logging
import urllib.request
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from app.database import get_connection
from app.services.ai_service import ai_service

logger = logging.getLogger("SignalStack.Research")

class ResearchService:
    def crawl_website_text(self, url: str) -> str:
        """Fetch and extract visible text from target website respecting timeouts."""
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SignalStack/1.0 (Executive Intelligence Engine; +https://signalstack.internal)"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                soup = BeautifulSoup(html, "html.parser")

                # Remove scripts, styles, navs
                for s in soup(["script", "style", "noscript", "svg"]):
                    s.decompose()

                text = soup.get_text(separator=" ", strip=True)
                return text[:6000]
        except Exception as e:
            logger.warning(f"Could not live-crawl {url}: {e}. Proceeding with domain knowledge & public context.")
            return ""

    def research_company(self, name: str, website: str, context_notes: str = "") -> Dict[str, Any]:
        """Perform initial research, separate facts from assumptions, and persist to database."""
        scraped_text = self.crawl_website_text(website)
        analysis = ai_service.analyze_company_website(name, website, scraped_text)

        company_id = str(uuid.uuid4())
        conn = get_connection()
        cursor = conn.cursor()

        # Check if company with exact name or website exists
        cursor.execute("SELECT id FROM companies WHERE LOWER(name) = ? OR LOWER(website) = ?", (name.lower(), website.lower()))
        existing = cursor.fetchone()
        if existing:
            company_id = existing["id"]
            cursor.execute("""
                UPDATE companies SET
                    name = ?, website = ?, industry = ?, description = ?,
                    verified_facts = ?, assumptions = ?, target_customers = ?,
                    value_propositions = ?, revenue_streams = ?, growth_priorities = ?,
                    context_notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                name, website, analysis.get("industry", ""), analysis.get("description", ""),
                json.dumps(analysis.get("verified_facts", [])),
                json.dumps(analysis.get("assumptions", [])),
                json.dumps(analysis.get("target_customers", [])),
                json.dumps(analysis.get("value_propositions", [])),
                json.dumps(analysis.get("revenue_streams", [])),
                json.dumps(analysis.get("growth_priorities", [])),
                context_notes,
                company_id
            ))
        else:
            cursor.execute("""
                INSERT INTO companies (
                    id, name, website, industry, description,
                    verified_facts, assumptions, target_customers,
                    value_propositions, revenue_streams, growth_priorities,
                    context_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id, name, website, analysis.get("industry", ""), analysis.get("description", ""),
                json.dumps(analysis.get("verified_facts", [])),
                json.dumps(analysis.get("assumptions", [])),
                json.dumps(analysis.get("target_customers", [])),
                json.dumps(analysis.get("value_propositions", [])),
                json.dumps(analysis.get("revenue_streams", [])),
                json.dumps(analysis.get("growth_priorities", [])),
                context_notes
            ))

        conn.commit()
        conn.close()

        analysis["id"] = company_id
        analysis["name"] = name
        analysis["website"] = website
        analysis["context_notes"] = context_notes
        return analysis

    def get_company(self, company_id: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        data = dict(row)
        for key in ["verified_facts", "assumptions", "target_customers", "value_propositions", "revenue_streams", "growth_priorities"]:
            if data.get(key):
                try:
                    data[key] = json.loads(data[key])
                except Exception:
                    data[key] = []
            else:
                data[key] = []
        return data

    def list_companies(self) -> list:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, website, industry, description, created_at FROM companies ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

research_service = ResearchService()
