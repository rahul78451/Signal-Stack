# Signal Stack — Technical Architecture Documentation
**System:** Company Intelligence & Executive Briefing Engine  
**Version:** 1.0.0 Production  
**Target:** Executive Briefing, Source Monitoring, and Strategic Decision Intelligence  

---

## 1. System Overview & Problem Statement
Modern executive leadership operates under continuous environmental flux: customers discuss unvarnished pain points on Reddit, competitors launch stealth pricing changes, destination visa regulations shift overnight, and internal CRM data records chronic deal-breaker objections. Founders typically track these manually through newsletters and disconnected tabs.

**Signal Stack** transforms raw external noise and internal logs into a continuous, structured corporate intelligence layer. The architecture unifies:
1. Automated Website Research & Distinction between Verified Facts vs Assumptions.
2. An Adaptive 10-Question Founder Interview Engine.
3. A 4-Category Signal Stack with Justified Sources.
4. A Multi-Format Crawler Engine with SHA-256 Deduplication.
5. An Intelligence Analysis Engine assessing 9 Executive Dimensions.
6. A Multi-Factor Ranking Formulation separating reliability from strategic relevance.
7. A 10-Section Monday Morning Executive Brief with Action Tracking.
8. Background Automation for Weekly Brief Generation and Monthly Health Audits.

```
+-----------------------------------------------------------------------------------------+
|                                    SIGNAL STACK SYSTEM                                  |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|  [Company Input] ----> [Initial Research Engine] ----> [Adaptive 10-Question Interview] |
|                                   |                                     |               |
|                                   v                                     v               |
|                       [Verified Facts vs Assumptions]       [Founder Context Memory]    |
|                                   |                                     |               |
|                                   +------------------+------------------+               |
|                                                      |                                  |
|                                                      v                                  |
|                                    [Signal Stack Builder (4 Categories)]                |
|                                      - Customers (Forums, Reddit, Reviews)              |
|                                      - Competitors (5-10 Rivals, Blogs, Launches)       |
|                                      - Market (Regulators, Policy, Trade Portals)       |
|                                      - Internal (CSV, Excel, PDF, TXT Ingestion)        |
|                                                      |                                  |
|                                                      v                                  |
|                                     [Source Monitoring & Crawler Engine]                |
|                                      - RSS / Atom XML Parser                            |
|                                      - Google News Feed Aggregator                      |
|                                      - Web HTML Article Parser                          |
|                                      - SHA-256 Content Deduplicator                     |
|                                                      |                                  |
|                                                      v                                  |
|                                       [Intelligence Analysis Engine]                    |
|                                      - 9 Executive Dimensions Assessment                |
|                                      - Verified Developments vs Strategic Inference     |
|                                                      |                                  |
|                                                      v                                  |
|                                      [Multi-Dimensional Ranking Engine]                 |
|                                      - Relevance (30%)   - Impact (25%)                 |
|                                      - Urgency (20%)     - Credibility (10%)            |
|                                      - Recency (10%)     - Novelty (5%)                 |
|                                                      |                                  |
|                                                      v                                  |
|                                   [Monday Morning Executive Brief (10 Sec)]             |
|                                      - Top 5 Developments                               |
|                                      - Customer, Rival, Market, Internal Signals        |
|                                      - Actionable Opportunities & Emerging Risks        |
|                                      - Prioritized Weekly Action Items Checklist        |
|                                      - Verifiable Source Evidence Appendix              |
|                                                      |                                  |
|                                                      v                                  |
|                                  [Dual-Process Background Automation]                   |
|                                      - Process A: Weekly Brief Scheduled Runner         |
|                                      - Process B: Monthly Source Health Auditor         |
|                                                                                         |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Core Service Architectures

### 2.1 Company Research & Fact-Assumption Separation
When a company URL is registered, `ResearchService` attempts public HTML extraction (headers, meta descriptions, product copy) using `BeautifulSoup`. 

The core prompt enforces strict epistemological separation:
- **Verified Facts:** Explicitly documented data points (e.g., "Operates recruitment agreements across 1,000+ global universities").
- **Strategic Assumptions:** Inferences regarding margin vulnerability, regulatory exposure, or CAC dynamics (e.g., "Assumed dependency on UK/Canada visa policies accounts for >70% of gross margin").

### 2.2 Adaptive AI Interview Service
The interview engine maintains conversational state across 10 dynamic questions. Rather than using static questionnaires:
- **Dynamic Context Generation:** Questions are generated from the company's verified business lines, target customer profiles, and competitive threats.
- **One Question at a Time:** Employs single-question delivery with memory of prior answers.
- **Confidentiality Skip:** Allows the founder to skip confidential revenue questions without breaking the interview state.
- **Founder Answer Editing:** Founders can revisit and update any response at any point.

### 2.3 The 4-Category Signal Stack & Justification Engine
The system creates four intelligence categories where **every single source must have an operational justification**:
1. **Customers:** Monitors Reddit (e.g., `r/Indians_StudyAbroad`), forums, and customer discussion channels. Focuses on recurring complaints, loan hurdles, visa anxiety, and unmet needs.
2. **Competitors:** Identifies 5–10 competitors (e.g., LeapScholar, Leverage Edu, IDP Education, Yocket, ApplyBoard) and monitors product launches, loan bundling, pricing models, and market positioning.
3. **Market & Regulatory:** Tracks direct regulatory authorities (UK Home Office, IRCC Canada, DAAD Germany, RBI Circulars) and trade journals (The PIE News, ICEF Monitor).
4. **Internal Intelligence:** Ingests CSV CRM exports, Excel sheets, PDF debriefs, and text transcripts. Extracts lost-deal reasons, counselor objections, and SLA delays.

### 2.4 Multi-Source Crawler & Deduplication Engine
`CrawlerService` visits approved sources respecting access terms, timeouts, and rate limits:
- **Feed & Page Fetching:** Supports RSS 2.0, Atom feeds, Google News search feeds, Reddit RSS, and HTML articles.
- **SHA-256 Deduplication:** Generates `hashlib.sha256(f"{title}_{url}".encode("utf-8")).hexdigest()`. Duplicate content hashes are discarded immediately, preventing news fatigue.
- **Health Tracking:** Measures source responsiveness. Dead URLs (404/500) trigger health penalties and status downgrades (`healthy` -> `warning` -> `dead`).

### 2.5 Intelligence Analysis Engine (9 Dimensions)
Collecting raw text is insufficient. `AnalysisService` evaluates 9 executive dimensions for each development:
1. **What happened?** (Factual summary)
2. **When did it happen?** (Timeframe/recency)
3. **What is the source?** (Original publisher)
4. **Is it verified?** (Evidence status)
5. **Why does it matter?** (Direct consequence for revenue or operations)
6. **Which business area is affected?** (Product, Sales, Compliance, Marketing)
7. **Opportunity, Threat, or Neutral?** (Strategic classification)
8. **How urgent is it?** (High, Medium, Low)
9. **What should the company consider doing?** (Tactical recommendation)

**Crucial Architecture Principle:** The system strictly separates *verified developments* (what actually occurred in the world) from *strategic interpretation* (what the development implies for the founder's business model).

---

## 3. Multi-Factor Intelligence Ranking Formulation
To prioritize signals for executive attention, `RankingService` computes a composite score ($0 - 100$):

$$\text{Composite Score} = (R \times 0.30) + (I \times 0.25) + (U \times 0.20) + (C \times 0.10) + (\text{Rec} \times 0.10) + (N \times 0.05)$$

Where:
- $R$ (**Relevance to Company**, Weight: $30\%$): Direct overlap with company name, industry taxonomy, core customer segments, and operating geography.
- $I$ (**Business Impact**, Weight: $25\%$): Severity of financial consequence (e.g., visa bans, zero-fee competitor discounting, policy caps).
- $U$ (**Urgency**, Weight: $20\%$): Action window deadline (immediate legislative implementation vs long-term macro trend).
- $C$ (**Source Credibility**, Weight: $10\%$): Source tiering (Government/Regulatory: 98%, Established Trade Press: 90%, Community/Forums: 75%).
- $\text{Rec}$ (**Recency**, Weight: $10\%$): Freshness within the 7-day monitoring cycle.
- $N$ (**Novelty**, Weight: $5\%$): Emergence of a newly detected pattern vs recurring background noise.

Every signal includes a human-readable **Rank Explanation** justifying why it is prioritized.

---

## 4. Monday Morning Executive Brief Structure
The generated brief fulfills all 10 required executive sections:
1. **Executive Summary:** Top 5 developments leadership must know this morning.
2. **Customer Signals:** Emerging problems, quotes, sentiment, and unmet needs.
3. **Competitor Intelligence:** Competitor moves, evidence, and strategic implications.
4. **Market & Regulatory Intelligence:** Policy, macro, and destination shifts.
5. **Internal Business Intelligence:** CRM objections, lost-deal patterns, and operational friction.
6. **Opportunities Identified:** At least 3 actionable opportunities with evidence, projected impact, next step, and priority.
7. **Risks & Emerging Threats:** Critical negative developments, possible impact, and urgency.
8. **Recommended Actions for This Week:** Prioritized action items ($P0/P1$) with rationale, suggested owner, and status tracking.
9. **What We Should Watch:** Early indicator watchlists with trigger thresholds.
10. **Source Appendix:** Traceable evidence table with original source, direct link, publication date, evidence snippet, and verification status.

---

## 5. Background Automation & Reliability
`SchedulerService` operates a lightweight daemon thread executing two independent processes:
- **Process A (Weekly Executive Brief):** Periodically runs crawl sweeps across active approved sources, parses new items, assesses business impact, generates the Monday brief, and logs the execution.
- **Process B (Monthly Signal Stack Audit):** Checks for dead URLs, identifies duplicate or inactive feeds, detects sources with declining relevance ($<70\%$ health), and persists audit logs to `audit_logs` table.

Both processes support manual on-demand triggers from the dashboard.
