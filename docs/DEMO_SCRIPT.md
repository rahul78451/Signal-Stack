# Signal Stack — Screen-Recorded Demonstration Script
**Video Target Duration:** 6–9 minutes  
**Format:** Screen recording with voiceover / walkthrough  
**Primary Company Target:** MeetUniversity (https://www.meetuniversity.com)  

---

## 🎬 Timestamp Walkthrough

### 0:00 – 1:00 | Introduction & The Problem
- **Visual:** Open Dashboard at `http://localhost:8000`. Show the header: "SIGNAL STACK — Executive v1.0".
- **Script:**
  > "Welcome to the demonstration of Signal Stack, an AI-powered corporate intelligence and Monday Morning Brief engine built for executive leadership. Businesses operate in environments of continuous change: customers raise objections on forums, rivals alter pricing, and regulations shift overnight. Most founders track this manually across dozens of tabs. Signal Stack transforms raw noise into a continuous, structured intelligence layer."

### 1:00 – 2:15 | Company Setup & Initial Research (Facts vs Assumptions)
- **Visual:** Click on the active company dropdown, showing **MeetUniversity** (`https://www.meetuniversity.com`).
- **Highlight:** Show the **Verified Facts vs Strategic Assumptions** cards.
- **Script:**
  > "Here is MeetUniversity. When a company is registered, Signal Stack automatically crawls its web presence and extracts a structured company profile. Notice our strict distinction: on the left are strictly Verified Facts extracted from official records—such as partnerships with over 1,000 international universities. On the right are Strategic Assumptions—such as vulnerability to UK and Canadian student visa bans and high reliance on commissions. Below, we see the highest-value customer segments, revenue streams, and strategic priorities."

### 2:15 – 3:30 | Adaptive 10-Question Founder Interview
- **Visual:** Click on the **Adaptive AI Interview** tab in the sidebar. Show the progress bar (10/10 completed) and the interactive active question card.
- **Highlight:** Point out the dynamic questions, the confidentiality skip option, and the transcript where past answers can be edited at any time.
- **Script:**
  > "Next is the Adaptive AI Interview. Rather than asking generic questions, Signal Stack generates 10 tailored questions exploring primary business lines, customer unmet needs, key competitors, and regulatory headwinds. Founders can answer one question at a time, skip confidential financial questions without breaking flow, and edit answers later. Notice Q6 directly addresses the UK dependent visa ban and Canadian PAL caps, and Q10 clarifies the exact decisions leadership needs to make every Monday."

### 3:30 – 4:45 | Signal Stack & Competitor Intelligence (4 Categories)
- **Visual:** Navigate to **Signal Stack & Rivals** tab.
- **Highlight:** 
  1. Show the **Competitors Table** (7 competitors: LeapScholar, Leverage Edu, IDP Education, Shiksha, Yocket, ApplyBoard, CollegeDekho) with threat levels and reasons why they matter.
  2. Show the **4 Signal Stack Categories**: Customers (Reddit, forums), Competitors (launches, blogs), Market (UK Home Office, IRCC Canada, DAAD Germany), and Internal Intelligence.
  3. Show the **Justification** on every single source card!
- **Script:**
  > "Signal Stack creates four intelligence categories. Every single source must be justified: here in Customers, Reddit r/Indians_StudyAbroad is included because students discuss visa delays and agency trust. In Competitors, we track 7 rivals—explaining why LeapScholar's loan bundling and Leverage Edu's accommodation portal matter. In Market, we monitor direct government visa regulators. In Internal, we ingest CRM logs and call transcripts."

### 4:45 – 5:30 | Source Manager & Internal Document Upload
- **Visual:** Navigate to **Source Manager & Upload** tab.
- **Highlight:** Drag-and-drop / upload `admissions_crm_dropoffs.csv` or show the 20+ active approved sources with health scores.
- **Script:**
  > "In the Source Manager, leadership can approve discovered feeds, add custom sources with mandatory justifications, and ingest internal business files (CSV, Excel, PDF, TXT). Here we ingest internal admissions CRM drop-offs, extracting recurring student objections regarding loan collateral and visa affidavit delays."

### 5:30 – 6:45 | Intelligence Feed & 9-Dimension Assessment
- **Visual:** Navigate to **Intelligence Feed** tab.
- **Highlight:** Show real crawled signals filterable by Category, Impact (Opportunity, Threat, Neutral), and Urgency (High, Medium, Low).
- **Script:**
  > "Collecting news is not enough; the system must analyze what developments mean for the business. Every signal is assessed across 9 executive dimensions: What happened, When, Why it matters, Business area affected, Impact classification, Urgency, and Strategic Interpretation vs Verified Evidence. Notice the multi-factor ranking score—here, the MAC Graduate Route retention ranks 88/100 because of its direct revenue impact."

### 6:45 – 7:45 | Monday Morning Executive Brief (10 Required Sections)
- **Visual:** Switch to **Monday Morning Brief** tab.
- **Highlight:** Walk through all 10 required sections:
  1. Executive Summary (Top 5 developments).
  2. Customer Signals (Quotes, sentiment).
  3. Competitor Intelligence.
  4. Market Intelligence.
  5. Internal Business Intelligence.
  6. Actionable Opportunities (>= 3 with next steps).
  7. Risks & Emerging Threats.
  8. Prioritized Actions for This Week (with interactive status checkboxes).
  9. What We Should Watch (early indicators).
  10. Source Appendix (traceable links, snippet, verification).
- **Script:**
  > "This is the final executive deliverable: the Monday Morning Brief. It prioritizes decision-relevant intelligence: the top 5 developments, student sentiment from Reddit, competitor loan bundling moves, regulatory shifts, internal sales objections, three actionable opportunities—like fast-tracking German university STEM pipelines—and prioritized P0/P1 actions with owners. Leaders can check off actions as they complete them or copy the brief as Markdown."

### 7:45 – 8:30 | Stress Test: Business Context Pivot
- **Visual:** Click "Test Context Pivot" button. Show modal.
- **Action:** Click "Re-Assess Signal Stack" with the pivot context: *Pivoting to Germany/Ireland STEM and AI Visa Copilot due to UK/Canada caps*.
- **Highlight:** Show the system automatically flag declining UK/Canada sources, recommend new German (DAAD, Reddit Germany) and Irish sources, and explain the strategic shift.
- **Script:**
  > "Now for the stress test. What happens when business priorities pivot? We submit a strategic change: MeetUniversity expanding to Germany and Ireland due to UK visa bans. Instantly, Signal Stack re-evaluates source relevance, flags declining undergraduate UK forums, adds DAAD Germany and Education in Ireland portals, and explains how intelligence monitoring has shifted."

### 8:30 – 9:00 | Multi-Company Reusability & Automation
- **Visual:** Switch active company in the top dropdown to **PostHog**, then to **Razorpay**. Show that interview questions, competitors, sources, and briefs completely differ. Then show the **Automation & Audit** tab with background cron status.
- **Script:**
  > "Signal Stack is fully reusable. Switching to PostHog instantly loads developer analytics competitors like Amplitude, cookie deprecation market signals, and custom interview questions. Switching to Razorpay loads RBI Payment Aggregator directives and Cashfree rival analysis. Finally, under Automation, both Process A (Weekly Briefs) and Process B (Monthly Health Audits) run as background automated daemons. Signal Stack turns any company into a continuously monitored, intelligent business."
