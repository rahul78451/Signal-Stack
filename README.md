# 📡 SignalStack
> **Your company's automated intelligence officer.**  
> It tracks what customers want, what competitors are launching, how regulations are changing, and what your sales team is hearing — then delivers a clean, decision-ready executive briefing every Monday morning.

[![Live Demo](https://img.shields.io/badge/Live%20Deployment-signal--stack--io.onrender.com-FF6B35?style=for-the-badge&logo=render&logoColor=white)](https://signal-stack-io.onrender.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

---

### 🌐 Live Application
👉 **Access Live Deployment:** **[https://signal-stack-io.onrender.com/](https://signal-stack-io.onrender.com/)**  
*(Hosted on Render. Pre-configured with MeetUniversity, PostHog, and Razorpay intelligence stacks).*

---

## 🌟 What is SignalStack?

Most founders and business leaders spend hours manually skimming newsletters, competitor websites, subreddits, and LinkedIn posts just to stay informed. Important shifts get missed, and raw noise gets mistaken for real news.

**SignalStack solves this problem in one simple flow:**
1. **You enter a company name and website.**
2. **SignalStack researches the business** and separates verifiable facts from assumptions.
3. **An adaptive 10-question AI interview** gathers key context (your revenue streams, top customers, biggest risks, and goals).
4. **It builds a custom Signal Stack** monitoring 4 core areas: **Customers**, **Competitors**, **Market & Regulations**, and **Internal Data** (CRM/sales call logs).
5. **Every Monday morning (or on demand),** it synthesizes all signals into an executive-level briefing with clear opportunities, risks, and action items.

---

## 🚀 Quick Start (Up & Running in 2 Minutes)

### 1. Requirements
- Python 3.10+ installed
- Web browser (Chrome, Edge, Safari, Firefox)

### 2. Setup & Installation
Open your terminal in the project directory and run:

```bash
# 1. Install dependencies (takes ~15 seconds)
pip install -r requirements.txt

# 2. Start the application
python main.py
```

### 3. Open in Your Browser
Go to: **[http://localhost:8000](http://localhost:8000)**

That's it! The database comes pre-seeded with 3 realistic companies so you can explore immediately without waiting to crawl websites.

---

## 🧭 Live Demo Companies

You can immediately switch between three pre-built company profiles right from the top bar:

| Company | Industry | Monitored Real-World Problem |
| :--- | :--- | :--- |
| **MeetUniversity** *(Primary Demo)* | EdTech / Study Abroad | UK & Canada student visa policy shifts, commission pressure, IELTS waiver demand |
| **PostHog** | DevTools / Product Analytics | Cookieless analytics privacy changes, Datadog pricing battles, open-source adoption |
| **Razorpay** | Fintech / Payments | RBI payment aggregator compliance, UPI transaction limits, merchant onboarding friction |

---

## 🛠️ How to Use the Dashboard

The dashboard is organized into simple, tab-based workflows:

```
[ Company Profile ] ──> [ AI Interview ] ──> [ Signal Stack ] ──> [ Feed & Brief ]
```

### 1. 🏢 Company & Profile
- View extracted facts (verified from public websites) versus strategic assumptions.
- See key pillars: target customer segments, revenue streams, and growth goals.
- Click **Edit Profile** to tweak anything anytime.

### 2. 💬 Adaptive AI Interview
- Answers 10 dynamic, non-generic business questions tailored to your specific market.
- Remembers earlier answers to ask intelligent follow-ups.
- Confidential questions can be **skipped** with one click.
- Any recorded answer can be edited later.

### 3. 🎯 Signal Stack & Competitors
- View your **5–10 active competitors** with threat levels and strategic justifications.
- Explore your 4 intelligence buckets:
  - **A. Customers:** Where target buyers discuss pain points (Reddit, student forums, user groups).
  - **B. Competitors:** Official blogs, changelogs, pricing changes, and press rooms.
  - **C. Market:** Visa authorities, government policies, and industry regulators.
  - **D. Internal Data:** Objections, drop-off logs, and sales transcripts.
- Every single source includes a **clear reason for inclusion** — no random link spam.

### 4. 📂 Source Manager & Internal Upload
- Add your own RSS feeds or custom intelligence URLs.
- **Upload Internal Files:** Drop in a `.csv`, `.xlsx`, `.pdf`, or `.txt` file (e.g., customer objection notes or lost-deal reasons). The system parses them into verified internal signals.
- Check source health scores and crawl status.

### 5. ⚡ Intelligence Feed
- A ranked, leaderboard-style stream of every development collected.
- Evaluates each event across 9 key questions: *What happened? When? Where? Verified? Why it matters? Impact area? Threat or Opportunity? Urgency? Recommended action?*
- Filter by category, urgency, or impact type.

### 6. ☕ Monday Morning Executive Brief
- The core deliverable for founders and executives.
- Structured into 10 clear sections:
  1. **Executive Summary** (Top 5 crucial developments)
  2. **Customer Signals** (Direct complaints, unmet needs, sentiment shifts)
  3. **Competitor Intelligence** (What rivals changed and what it means)
  4. **Market & Regulatory Intelligence** (Policy changes, macro developments)
  5. **Internal Business Intelligence** (Sales objections, customer friction)
  6. **Opportunities Identified** (At least 3 actionable opportunities with next steps)
  7. **Risks & Threats** (Emerging threats and severity)
  8. **Recommended Actions for This Week** (With interactive checkboxes and owners)
  9. **What We Should Watch** (Early warning triggers to keep an eye on)
  10. **Source Appendix** (Direct links, timestamps, and quotes for full verification)
- Includes a **Copy Markdown** button to paste directly into Slack, Notion, or an executive email.

### 7. 🤖 Automation & Audit
- **Process A (Weekly Brief):** Runs every Monday morning at 08:00 AM automatically.
- **Process B (Monthly Audit):** Automatically checks for broken URLs, duplicate feeds, and sources losing relevance.
- You can manually trigger either process with one click anytime.

---

## 🧪 Special Feature: The Context Pivot Stress Test

What happens when your business strategy suddenly pivots? Does your intelligence stack stay stuck in the past?

**Try the stress test:**
1. Go to the **Signal Stack** tab or click **Change Context** in the bottom left.
2. Enter a pivot (e.g., *"Due to UK visa bans, MeetUniversity is pivoting toward German and Irish university admissions"*).
3. Click **Re-Assess Signal Stack**.
4. Watch the engine automatically deprecate obsolete UK sources and recommend fresh German/European intelligence feeds.

---

## 🔒 100% Free & Resilient by Design ($0.00 / Month)

- **Works Completely Offline:** Built with a dual-engine design. If an API key or internet connection is not present, it seamlessly falls back to high-fidelity, grounded local intelligence.
- **Optional Gemini API:** If you want live web reasoning with Google's Gemini models, simply add your free API key to `.env`:
  ```bash
  GEMINI_API_KEY=your_free_gemini_api_key
  ```
- **Zero Paid Subscriptions:** Runs on Python, FastAPI, SQLite, and vanilla modern web standards.

---

## 📂 Project Structure

```
.
├── main.py                    # Server startup and API router mounts
├── requirements.txt           # Lightweight dependencies
├── app/
│   ├── config.py              # App settings & environment variables
│   ├── database.py            # SQLite database schema (9 clean tables)
│   ├── api/
│   │   └── routes.py          # Clean REST API endpoints
│   ├── models/
│   │   └── schemas.py         # Pydantic data models & request validation
│   ├── services/
│   │   ├── ai_service.py          # Dual AI engine (Gemini + Local Fallback)
│   │   ├── research_service.py    # Company website research & fact extractor
│   │   ├── interview_service.py   # Adaptive 10-question interview engine
│   │   ├── stack_service.py       # 4-category signal stack builder & pivot
│   │   ├── crawler_service.py     # Source crawler with SHA-256 deduplication
│   │   ├── analysis_service.py    # 9-dimension intelligence assessment
│   │   ├── ranking_service.py     # Multi-factor mathematical ranking
│   │   ├── briefing_service.py    # 10-section Monday Morning Brief generator
│   │   ├── file_parser.py         # Internal file parser (.csv, .xlsx, .pdf, .txt)
│   │   ├── audit_service.py       # Monthly dead-link and relevance auditor
│   │   └── scheduler_service.py   # Background automation daemon
│   ├── static/
│   │   ├── index.html         # Responsive executive SPA dashboard
│   │   ├── css/style.css      # Warm light theme & leaderboard styling
│   │   └── js/app.js          # Interactive dashboard controller
│   └── data/
│       ├── seeds.py           # Realistic pre-seeded data for 3 demo companies
│       └── samples/           # Sample internal CSV & TXT files for test uploads
├── docs/                      # Technical architecture, cost statement & tests
├── reports/                   # Exported Markdown executive briefs
└── tests/
    └── test_signal_stack.py   # Full automated unit test suite
```

---

## 🧪 Running the Tests

To verify that all services, database tables, and ranking calculations are working properly:

```bash
python -m unittest discover tests
```
*All 8 tests run in less than half a second.*

---

## 📝 License
Built for educational and evaluation purposes for the **EDXSO AI Engineer Intern Assignment**.
