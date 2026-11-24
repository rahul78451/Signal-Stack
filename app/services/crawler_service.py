import uuid
import hashlib
import logging
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from app.database import get_connection

logger = logging.getLogger("SignalStack.Crawler")

class CrawlerService:
    def crawl_sources_for_company(self, company_id: str) -> Dict[str, Any]:
        """Crawl all active approved sources for the company, extract new signals, deduplicate."""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sources WHERE company_id = ? AND is_active = 1 AND is_approved = 1", (company_id,))
        sources = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT name, website FROM companies WHERE id = ?", (company_id,))
        company = cursor.fetchone()
        company_name = company["name"] if company else "Company"

        new_signals_count = 0
        crawled_sources_count = 0
        failed_sources = []

        for src in sources:
            source_id = src["id"]
            url = src["url"]
            cat = src["category"]
            src_type = src["source_type"]

            # Skip internal mock files
            if url.startswith("internal://"):
                continue

            try:
                items = self._fetch_feed_or_page(url, src_type)
                crawled_sources_count += 1

                for item in items:
                    title = item.get("title", "").strip()
                    item_url = item.get("url", url).strip()
                    snippet = item.get("snippet", title).strip()
                    pub_date = item.get("pub_date", datetime.utcnow().strftime("%Y-%m-%d"))

                    if not title or len(title) < 5:
                        continue

                    # Deduplication via SHA-256 hash of title + url
                    content_hash = hashlib.sha256(f"{title}_{item_url}".encode("utf-8")).hexdigest()

                    cursor.execute("SELECT id FROM signals WHERE content_hash = ?", (content_hash,))
                    if not cursor.fetchone():
                        sig_id = str(uuid.uuid4())
                        cursor.execute("""
                            INSERT INTO signals (
                                id, company_id, source_id, title, url,
                                raw_content, evidence_snippet, publication_date, category, content_hash
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            sig_id, company_id, source_id, title, item_url,
                            snippet, snippet[:500], pub_date, cat, content_hash
                        ))
                        new_signals_count += 1

                # Update source healthy status
                cursor.execute("""
                    UPDATE sources
                    SET last_crawled_at = CURRENT_TIMESTAMP, last_status = 'healthy', health_score = 100
                    WHERE id = ?
                """, (source_id,))

            except Exception as e:
                logger.warning(f"Failed to crawl {url}: {e}")
                failed_sources.append({"source": src["name"], "url": url, "error": str(e)})
                cursor.execute("""
                    UPDATE sources
                    SET last_crawled_at = CURRENT_TIMESTAMP,
                        last_status = CASE WHEN health_score <= 40 THEN 'dead' ELSE 'warning' END,
                        health_score = MAX(0, health_score - 20)
                    WHERE id = ?
                """, (source_id,))

        conn.commit()
        conn.close()

        return {
            "company_id": company_id,
            "crawled_sources": crawled_sources_count,
            "new_signals_collected": new_signals_count,
            "failed_sources": failed_sources
        }

    def _fetch_feed_or_page(self, url: str, source_type: str) -> List[Dict[str, Any]]:
        """Fetch RSS feed, Google News, or HTML page."""
        items = []
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SignalStack/1.0 (Business Intelligence Engine)"}
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                content = resp.read().decode("utf-8", errors="ignore")

                if "<rss" in content.lower() or "<feed" in content.lower() or "<xml" in content.lower():
                    items = self._parse_rss_xml(content)
                else:
                    items = self._parse_html_page(content, url)
        except Exception as e:
            # Re-raise to trigger error tracking
            raise e

        return items

    def _parse_rss_xml(self, xml_content: str) -> List[Dict[str, Any]]:
        items = []
        try:
            root = ET.fromstring(xml_content)
            # Standard RSS channel -> item
            for item in root.findall(".//item")[:15]:
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                desc = item.findtext("description", "")
                pub_date = item.findtext("pubDate", "")

                # Clean HTML from description
                soup = BeautifulSoup(desc, "html.parser")
                clean_desc = soup.get_text(separator=" ", strip=True)

                items.append({
                    "title": title,
                    "url": link,
                    "snippet": clean_desc or title,
                    "pub_date": pub_date
                })

            # Atom feed entry -> title, link, summary
            if not items:
                for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry")[:15]:
                    title = entry.findtext("{http://www.w3.org/2005/Atom}title", "")
                    link_el = entry.find("{http://www.w3.org/2005/Atom}link")
                    link = link_el.attrib.get("href", "") if link_el is not None else ""
                    summary = entry.findtext("{http://www.w3.org/2005/Atom}summary", "")
                    pub_date = entry.findtext("{http://www.w3.org/2005/Atom}updated", "")

                    items.append({
                        "title": title,
                        "url": link,
                        "snippet": summary or title,
                        "pub_date": pub_date
                    })
        except Exception as e:
            logger.debug(f"XML parse error: {e}")
        return items

    def _parse_html_page(self, html_content: str, base_url: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, "html.parser")
        items = []

        # Extract articles or headlines
        articles = soup.find_all(["article", "h2", "h3"])[:10]
        for a in articles:
            title = a.get_text(strip=True)
            link = base_url
            link_tag = a.find("a") if hasattr(a, "find") else None
            if link_tag and link_tag.get("href"):
                link = link_tag["href"]
                if not link.startswith("http"):
                    link = base_url.rstrip("/") + "/" + link.lstrip("/")

            if len(title) > 20:
                items.append({
                    "title": title,
                    "url": link,
                    "snippet": title,
                    "pub_date": datetime.utcnow().strftime("%Y-%m-%d")
                })
        return items

crawler_service = CrawlerService()
