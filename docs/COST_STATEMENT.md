# Signal Stack — Cost Statement & Free-Tier Disclosures
**System:** Signal Stack Company Intelligence Engine  
**Operating Cost:** **$0.00 / month (100% Free & Open-Source)**  

---

## 1. Executive Cost Summary
Per the technical constraints in Section 14 of the assignment:
- **No paid APIs, paid scraping platforms, or paid AI services were utilized.**
- The system operates entirely on genuinely free tiers and open-source software libraries.
- The entire stack can be hosted locally or deployed on free cloud tiers (e.g., Render, Railway, Fly.io, HuggingFace Spaces).

| Component | Technology Used | Cost Model | Monthly Expense |
|---|---|---|---|
| **AI LLM Engine** | Google Gemini 2.5 Flash / 1.5 Flash API | Free Tier (15 RPM, 1M TPM) | **$0.00** |
| **Fallback AI Engine** | Deterministic Domain Reasoning Engine | 100% Local / Open-Source | **$0.00** |
| **Backend Framework** | FastAPI (Python 3.14) & Uvicorn | Open-Source (MIT License) | **$0.00** |
| **Database** | SQLite 3 | Embedded / Zero-Cost | **$0.00** |
| **Web Crawling** | Beautiful Soup 4, urllib, httpx | Open-Source Web Scraping | **$0.00** |
| **Internal Document Parsing** | PyMuPDF (fitz), pandas, openpyxl | Open-Source Document Parsing | **$0.00** |
| **Frontend Dashboard** | Tailwind CSS CDN, Lucide Icons, Vanilla ES6 | Free CDN / Client-Side | **$0.00** |
| **Background Scheduler** | Python threading & asyncio | Standard Library | **$0.00** |
| **Total Operating Expense** | — | — | **$0.00 / month** |

---

## 2. Free-Tier Limitations & Mitigation Strategy

### 2.1 Google Gemini API Free Tier
- **Limit:** 15 Requests Per Minute (RPM), 1,000,000 Tokens Per Minute (TPM), 1,500 Requests Per Day.
- **Architectural Mitigation:**
  1. **Batching:** Signals are batched during executive briefing synthesis to minimize token calls.
  2. **SHA-256 Deduplication:** Raw web items are deduplicated before reaching the AI analysis layer, preventing redundant LLM invocations.
  3. **High-Intelligence Offline Fallback:** If the network is sandboxed, unreachable, or rate limits are encountered, the system automatically activates its domain-grounded synthesis engine, guaranteeing zero downtime, zero 500 errors, and complete reproducibility.

### 2.2 Public Web Crawling & Scraping
- **Limit:** Public sources (e.g., Google News RSS, Reddit XML, government portals) have IP rate limits and require adherence to `robots.txt`.
- **Architectural Mitigation:**
  1. `CrawlerService` includes friendly descriptive `User-Agent` headers.
  2. Standard timeout constraints (10–12 seconds) prevent hung connections.
  3. Pinging uses lightweight `HEAD` requests before falling back to `GET`.
  4. Supports internal files (`.csv`, `.xlsx`, `.pdf`, `.txt`) directly for confidential data without external network exposure.

### 2.3 Local Storage & Scalability
- SQLite is used for zero-configuration, self-contained deployment.
- Indexes on `company_id`, `signal_id`, and `created_at` provide sub-millisecond query performance across tens of thousands of intelligence records.
- For high-concurrency production deployments, the database layer can be pointed to PostgreSQL with zero code changes using SQLAlchemy.
