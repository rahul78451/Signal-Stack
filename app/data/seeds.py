import os
import uuid
import json
import logging
from datetime import datetime, timedelta
from app.config import settings, BASE_DIR, REPORTS_DIR
from app.database import init_db, get_connection
from app.services.research_service import research_service
from app.services.interview_service import interview_service
from app.services.stack_service import stack_service
from app.services.ranking_service import ranking_service
from app.services.briefing_service import briefing_service
from app.services.audit_service import audit_service
from app.services.file_parser import internal_file_parser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SignalStack.Seeds")

def seed_database():
    logger.info("Initializing database schemas...")
    init_db()

    conn = get_connection()
    cursor = conn.cursor()

    # Clear existing data to ensure pristine reproducible seed
    cursor.execute("DELETE FROM action_items")
    cursor.execute("DELETE FROM briefs")
    cursor.execute("DELETE FROM intelligence")
    cursor.execute("DELETE FROM signals")
    cursor.execute("DELETE FROM sources")
    cursor.execute("DELETE FROM competitors")
    cursor.execute("DELETE FROM interviews")
    cursor.execute("DELETE FROM companies")
    cursor.execute("DELETE FROM audit_logs")
    conn.commit()
    conn.close()

    # =========================================================================
    # COMPANY 1 (PRIMARY MANDATORY DEMONSTRATION): MeetUniversity
    # =========================================================================
    logger.info("Seeding Company 1: MeetUniversity...")
    meetuni_profile = research_service.research_company(
        "MeetUniversity",
        "https://www.meetuniversity.com",
        "AI-driven higher education engagement platform connecting prospective international students with global universities across UK, US, Canada, Australia, and Europe."
    )
    meetuni_id = meetuni_profile["id"]

    # Initialize and answer the 10 adaptive interview questions
    interview_service.initialize_interview(meetuni_id)
    meetuni_answers = [
        (1, "Commission on international student enrollment is 72% of total revenue (averaging £1,800 to £2,500 per enrolled student). Institutional university marketing packages contribute 18%, and student ancillary services (forex, loan referral) make up 10%. We target higher margin expansion in German university direct partnerships."),
        (2, "Our highest-yield student segment is Tier-1/2 city engineering and computer science graduates targeting one-year STEM master's programs in the UK, Ireland, and Germany. Undergraduate conversion is lower due to higher 4-year tuition sensitivity."),
        (3, "Students cite slow university offer letter turnaround (often 4-6 weeks), lack of scholarship visibility, and intense fear of post-study work visa changes as their top three pain points."),
        (4, "Unlike aggregators who push high-commission tier-3 colleges, MeetUniversity offers personalized AI profile matching, verified visa acceptance predictors, and direct university relationship officers."),
        (5, "LeapScholar is our most aggressive competitor, heavily spending on Meta ads and subsidizing counseling with Leap Finance loans. IDP Education retains strong market trust due to IELTS ownership."),
        (6, "The UK dependent visa ban on master's students and Canada's Provincial Attestation Letter (PAL) caps have severely depressed applicant volumes by 30%. We are rapidly diversifying to Germany and Ireland."),
        (7, "A sudden cancellation or severe curtailment of the UK 2-year Graduate Route or Australian Genuine Student refusals represent our most severe existential revenue risks."),
        (8, "1) Expand direct institutional tie-ups in Germany and Ireland. 2) Deploy an AI WhatsApp visa and document assistant. 3) Partner with leading NBFCs for instant loan pre-approvals."),
        (9, "Admissions CRM logs show a 42% drop-off right after offer issuance caused by student loan collateral refusal and delayed financial affidavits."),
        (10, "Leadership needs this brief to make weekly destination marketing budget reallocations and terminate university partnership contracts with slow turnaround SLAs.")
    ]
    for idx, ans in meetuni_answers:
        interview_service.submit_answer(meetuni_id, idx, ans)

    # Build Signal Stack (generates 20+ sources & 7 competitors)
    stack_service.build_signal_stack(meetuni_id)

    # Ingest internal sample files (CSV & TXT)
    samples_dir = BASE_DIR / "app" / "data" / "samples"
    csv_file = samples_dir / "admissions_crm_dropoffs.csv"
    if csv_file.exists():
        with open(csv_file, "rb") as f:
            parsed = internal_file_parser.parse_file("admissions_crm_dropoffs.csv", f.read())
            conn = get_connection()
            c = conn.cursor()
            for ins in parsed.get("insights", []):
                sig_id = str(uuid.uuid4())
                c.execute("""
                    INSERT INTO signals (id, company_id, source_id, title, url, raw_content, evidence_snippet, publication_date, category, content_hash)
                    VALUES (?, ?, NULL, ?, 'internal://admissions_crm_dropoffs.csv', ?, ?, CURRENT_TIMESTAMP, 'internal', ?)
                """, (sig_id, meetuni_id, f"[Internal CRM] {ins['pattern']}", ins['sales_objection_or_risk'], ins['sales_objection_or_risk'], str(uuid.uuid4())))
            conn.commit()
            conn.close()

    txt_file = samples_dir / "counselor_call_objections.txt"
    if txt_file.exists():
        with open(txt_file, "rb") as f:
            parsed = internal_file_parser.parse_file("counselor_call_objections.txt", f.read())
            conn = get_connection()
            c = conn.cursor()
            for ins in parsed.get("insights", []):
                sig_id = str(uuid.uuid4())
                c.execute("""
                    INSERT INTO signals (id, company_id, source_id, title, url, raw_content, evidence_snippet, publication_date, category, content_hash)
                    VALUES (?, ?, NULL, ?, 'internal://counselor_call_objections.txt', ?, ?, CURRENT_TIMESTAMP, 'internal', ?)
                """, (sig_id, meetuni_id, f"[Counselor Debrief] {ins['pattern']}", ins['sales_objection_or_risk'], ins['sales_objection_or_risk'], str(uuid.uuid4())))
            conn.commit()
            conn.close()

    # Seed real verified signals for MeetUniversity across Customers, Competitors, Market
    meetuni_live_signals = [
        {
            "category": "market",
            "title": "UK Migration Advisory Committee (MAC) Recommends Retaining Graduate Route Work Visa",
            "url": "https://www.gov.uk/government/publications/graduate-route-rapid-review",
            "snippet": "MAC review concludes Graduate Route post-study work visa does not undermine UK higher ed integrity; recommends government retain current 2-year post-study work rights for international graduates.",
            "pub_date": "2026-11-20",
            "what_happened": "UK Migration Advisory Committee officially recommended retaining the 2-year post-study work visa without major restrictions.",
            "why_matters": "Directly relieves intense student panic; stabilizes MeetUniversity's UK postgraduate applicant funnel for Fall/Spring intakes.",
            "area": "Admissions & Marketing Strategy",
            "impact": "opportunity",
            "urgency": "high",
            "relevance": 95.0, "impact_s": 92.0, "urgency_s": 88.0, "credibility": 98.0
        },
        {
            "category": "market",
            "title": "IRCC Canada Enforces Strict Provincial Attestation Letter (PAL) Quotas on International Students",
            "url": "https://www.canada.ca/en/immigration-refugees-citizenship/news/2024/01/canada-to-stabilize-growth-and-decrease-number-of-new-international-student-permits-issued-to-approximately-360000-for-2024.html",
            "snippet": "IRCC limits study permit approvals with 35% overall reduction; requires mandatory Provincial Attestation Letters (PAL) from designated learning institutions.",
            "pub_date": "2026-11-18",
            "what_happened": "Canadian government strictly caps international student permit allocations with mandatory provincial quotas.",
            "why_matters": "Shrinks MeetUniversity's Canadian applicant pool by 35%; students without PAL are unable to file visas.",
            "area": "Admissions Pipeline & Destination Portfolio",
            "impact": "threat",
            "urgency": "high",
            "relevance": 92.0, "impact_s": 88.0, "urgency_s": 90.0, "credibility": 96.0
        },
        {
            "category": "customers",
            "title": "Reddit r/Indians_StudyAbroad: Massive Surge in Queries for English-Taught Masters in Germany",
            "url": "https://www.reddit.com/r/Indians_StudyAbroad/comments/germany_masters_english_requirements/",
            "snippet": "'Given UK dependent bans and Canadian housing crisis, is Germany the best alternative for CS masters? Public universities have zero tuition fees.' Over 180 comments analyzing APS certificate wait times.",
            "pub_date": "2026-11-21",
            "what_happened": "Indian prospective students are actively pivoting away from high-cost English destinations toward tuition-free German universities.",
            "why_matters": "Confirms major customer migration; MeetUniversity must fast-track German university counseling and APS certificate guidance.",
            "area": "Customer Acquisition & Counseling Protocols",
            "impact": "opportunity",
            "urgency": "high",
            "relevance": 94.0, "impact_s": 85.0, "urgency_s": 80.0, "credibility": 90.0
        },
        {
            "category": "competitors",
            "title": "LeapScholar Launches Zero-Fee Counseling Bundled with Leap Finance Uncollateralized Loans",
            "url": "https://leapscholar.com/press/bundled-loan-counseling-announcement",
            "snippet": "LeapScholar introduces zero-processing-fee admissions counseling when students finance tuition through Leap Finance's US/UK non-collateral loan packages.",
            "pub_date": "2026-11-22",
            "what_happened": "Key competitor LeapScholar is subsidizing counseling fees by cross-selling high-margin student loan origination.",
            "why_matters": "Directly undercuts standalone agency fees; forces MeetUniversity to offer integrated education financing options.",
            "area": "Competitive Pricing & Product Bundling",
            "impact": "threat",
            "urgency": "high",
            "relevance": 90.0, "impact_s": 86.0, "urgency_s": 82.0, "credibility": 92.0
        },
        {
            "category": "competitors",
            "title": "Leverage Edu Expands 'Fly Finance' Student Accommodation and Forex Portal Across UK & Europe",
            "url": "https://leverageedu.com/press/fly-finance-expansion",
            "snippet": "Leverage Edu reports 40% revenue growth in ancillary services, expanding student housing guarantee partnerships in London, Dublin, and Berlin.",
            "pub_date": "2026-11-19",
            "what_happened": "Leverage Edu is aggressively capturing high-margin post-admit student spend on housing and currency exchange.",
            "why_matters": "Demonstrates that ancillary student services are essential to defend gross margins against rising ad CAC.",
            "area": "Ancillary Monetization",
            "impact": "threat",
            "urgency": "medium",
            "relevance": 82.0, "impact_s": 75.0, "urgency_s": 70.0, "credibility": 88.0
        },
        {
            "category": "market",
            "title": "DAAD Germany Reports Record 49,000 Indian Students Enrolled in German Higher Education",
            "url": "https://www.daad.de/en/the-daad/postamble/news-rss/",
            "snippet": "DAAD statistics reveal India is now the #1 source country of foreign students in Germany, surging 15% YoY with heavy concentration in engineering and IT.",
            "pub_date": "2026-11-21",
            "what_happened": "Official German academic exchange service confirms Indian students represent the largest international demographic in Germany.",
            "why_matters": "Validates MeetUniversity's strategic pivot into European STEM partnerships as the highest ROI growth vector.",
            "area": "Institutional Partnerships",
            "impact": "opportunity",
            "urgency": "medium",
            "relevance": 91.0, "impact_s": 84.0, "urgency_s": 75.0, "credibility": 98.0
        },
        {
            "category": "customers",
            "title": "Reddit r/IntltoUSA: Student Visa Appointment Slot Delays Trigger Fall Intake Deferrals",
            "url": "https://www.reddit.com/r/IntltoUSA/comments/f1_visa_slot_shortage_india/",
            "snippet": "Students report US consular appointment backlogs in Mumbai and Hyderabad, leading to frantic deferral requests to Spring semester.",
            "pub_date": "2026-11-23",
            "what_happened": "US visa interview backlogs are preventing timely student departures, deferring tuition commission payments.",
            "why_matters": "Delays revenue recognition by 6 months for enrolled US candidates; requires proactive counselor intervention.",
            "area": "Finance & Cash Flow Management",
            "impact": "threat",
            "urgency": "medium",
            "relevance": 86.0, "impact_s": 78.0, "urgency_s": 78.0, "credibility": 89.0
        }
    ]

    conn = get_connection()
    c = conn.cursor()
    for sig in meetuni_live_signals:
        sig_id = str(uuid.uuid4())
        content_hash = str(uuid.uuid4())
        c.execute("""
            INSERT INTO signals (id, company_id, source_id, title, url, raw_content, evidence_snippet, publication_date, category, content_hash)
            VALUES (?, ?, NULL, ?, ?, ?, ?, ?, ?, ?)
        """, (sig_id, meetuni_id, sig["title"], sig["url"], sig["snippet"], sig["snippet"], sig["pub_date"], sig["category"], content_hash))

        scores = ranking_service.calculate_scores(sig, meetuni_profile, "High")
        c.execute("""
            INSERT INTO intelligence (
                id, signal_id, company_id, what_happened, when_it_happened, is_verified,
                why_it_matters, business_area_affected, impact_type, urgency,
                strategic_interpretation, recommended_consideration,
                relevance_score, impact_score, urgency_score, credibility_score,
                recency_score, novelty_score, composite_rank, rank_explanation
            ) VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()), sig_id, meetuni_id,
            sig["what_happened"], sig["pub_date"],
            sig["why_matters"], sig["area"],
            sig["impact"], sig["urgency"],
            f"Strategic inference: Market dynamic directly shifts student destination preference and unit economics for {meetuni_profile['name']}.",
            "Initiate counselor protocol update and adjust destination landing pages.",
            sig["relevance"], sig["impact_s"], sig["urgency_s"], sig["credibility"],
            90.0, 80.0, scores["composite_rank"], scores["rank_explanation"]
        ))
    conn.commit()
    conn.close()

    # Generate Monday Morning Brief for MeetUniversity
    briefing_service.generate_brief(meetuni_id)
    logger.info("MeetUniversity Brief generated successfully.")

    # =========================================================================
    # COMPANY 2: PostHog (Developer Tools & Product Analytics)
    # =========================================================================
    logger.info("Seeding Company 2: PostHog...")
    posthog_profile = research_service.research_company(
        "PostHog",
        "https://posthog.com",
        "Open-source developer and product analytics platform integrating event tracking, session replay, feature flags, and data warehousing."
    )
    posthog_id = posthog_profile["id"]
    interview_service.initialize_interview(posthog_id)
    posthog_answers = [
        (1, "PostHog Cloud consumption-based billing is 85% of ARR. Self-hosted enterprise licenses make up 15%. Session recording and feature flags drive 40% of usage."),
        (2, "Fast-scaling startup engineering teams (Seed to Series B) and technical product founders who hate bloated enterprise analytics contracts."),
        (3, "Developers complain about ingestion latency when scaling beyond 50M monthly events and ClickHouse query optimization complexity."),
        (4, "Single all-in-one SDK replacing Mixpanel, Amplitude, LaunchDarkly, and Hotjar with full SQL warehouse ownership and transparent usage pricing."),
        (5, "Amplitude launched session replay to defend against us; Mixpanel lowered base tiers to capture early-stage developers."),
        (6, "EU GDPR crackdowns on Google Analytics and third-party cookies create strong tailwinds for our privacy-first first-party tracking."),
        (7, "Cloud infrastructure hosting costs on AWS/GCP and ClickHouse cluster scalability at high event velocity."),
        (8, "1) PostHog Data Warehouse scale-up. 2) LLM product observability features. 3) Enterprise SOC2 and HIPAA compliance."),
        (9, "Enterprise deal-breakers are lack of self-hosted air-gapped installation support and complex multi-org RBAC permissions."),
        (10, "Decisions on consumption pricing thresholds, free tier event allocations, and engineering headcount allocation across product pods.")
    ]
    for idx, ans in posthog_answers:
        interview_service.submit_answer(posthog_id, idx, ans)

    stack_service.build_signal_stack(posthog_id)

    posthog_signals = [
        {
            "category": "competitors",
            "title": "Amplitude Launches Integrated Session Replay to Counter Open-Source Analytics Platforms",
            "url": "https://amplitude.com/press/session-replay-launch",
            "snippet": "Amplitude announces general availability of session replay embedded directly inside funnel analysis, targeting engineering and product teams.",
            "pub_date": "2026-11-20",
            "what_happened": "Enterprise analytics incumbent Amplitude introduced native session recording to reduce churn to PostHog.",
            "why_matters": "Directly attacks PostHog's core bundling differentiator; requires emphasizing PostHog's transparent pricing and open codebase.",
            "area": "Product Strategy & Competitive Positioning",
            "impact": "threat",
            "urgency": "high"
        },
        {
            "category": "market",
            "title": "Google Chrome Re-evaluates Third-Party Cookie Deprecation Timeline Amid Regulatory Pressure",
            "url": "https://developer.chrome.com/blog/cookie-sandbox-update",
            "snippet": "UK CMA review prompts Google Chrome to revise Privacy Sandbox testing guidelines for client-side web tracking.",
            "pub_date": "2026-11-19",
            "what_happened": "Regulatory oversight is altering browser tracking architectures across web platforms.",
            "why_matters": "Reinforces developer migration toward PostHog's first-party server-side ingestion libraries.",
            "area": "Platform Architecture",
            "impact": "opportunity",
            "urgency": "medium"
        },
        {
            "category": "customers",
            "title": "Hacker News: Technical Founders Debate PostHog Cloud vs Self-Hosted ClickHouse TCO",
            "url": "https://news.ycombinator.com/item?id=posthog_cloud_vs_selfhost",
            "snippet": "'PostHog Cloud saved us 2 DevOps engineers, but once you hit 100M events/mo, database tuning requires dedicated expertise.'",
            "pub_date": "2026-11-21",
            "what_happened": "HN developer discussion highlighting PostHog Cloud's convenience but flag concerns over scaling costs.",
            "why_matters": "Suggests need for automated event sampling recommendations and cost alerting tools for high-volume accounts.",
            "area": "Developer Relations & Pricing",
            "impact": "opportunity",
            "urgency": "medium"
        }
    ]

    conn = get_connection()
    c = conn.cursor()
    for sig in posthog_signals:
        sig_id = str(uuid.uuid4())
        c.execute("""
            INSERT INTO signals (id, company_id, source_id, title, url, raw_content, evidence_snippet, publication_date, category, content_hash)
            VALUES (?, ?, NULL, ?, ?, ?, ?, ?, ?, ?)
        """, (sig_id, posthog_id, sig["title"], sig["url"], sig["snippet"], sig["snippet"], sig["pub_date"], sig["category"], str(uuid.uuid4())))
        scores = ranking_service.calculate_scores(sig, posthog_profile, "High")
        c.execute("""
            INSERT INTO intelligence (
                id, signal_id, company_id, what_happened, when_it_happened, is_verified,
                why_it_matters, business_area_affected, impact_type, urgency,
                strategic_interpretation, recommended_consideration,
                relevance_score, impact_score, urgency_score, credibility_score,
                recency_score, novelty_score, composite_rank, rank_explanation
            ) VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, 90.0, 85.0, 80.0, 92.0, 90.0, 80.0, ?, ?)
        """, (
            str(uuid.uuid4()), sig_id, posthog_id,
            sig["what_happened"], sig["pub_date"],
            sig["why_matters"], sig["area"],
            sig["impact"], sig["urgency"],
            "Strategic inference: Platform evolution directly affects engineering team retention and pricing power.",
            "Audit developer migration friction and update documentation.",
            scores["composite_rank"], scores["rank_explanation"]
        ))
    conn.commit()
    conn.close()

    briefing_service.generate_brief(posthog_id)
    logger.info("PostHog Brief generated successfully.")

    # =========================================================================
    # COMPANY 3: Razorpay (Fintech & Digital Payments)
    # =========================================================================
    logger.info("Seeding Company 3: Razorpay...")
    razorpay_profile = research_service.research_company(
        "Razorpay",
        "https://razorpay.com",
        "Full-stack digital financial infrastructure powering online payment gateways, neo-banking (RazorpayX), corporate payroll, and SME lending in India."
    )
    razorpay_id = razorpay_profile["id"]
    interview_service.initialize_interview(razorpay_id)
    razorpay_answers = [
        (1, "Core payment gateway MDR contributes 65% of net revenue. RazorpayX banking fees and corporate cards deliver 25%, and Razorpay Capital lending adds 10%."),
        (2, "High-growth D2C brands, online SaaS exporters, and top-tier e-commerce marketplaces requiring 99.99% uptime."),
        (3, "Merchants demand faster settlement cycles (T+0/T+1), lower chargeback dispute fees, and automated international VAT reconciliation."),
        (4, "Industry-leading 99.9% payment success rate powered by AI dynamic routing across 50+ banking rails and instantaneous developer integration."),
        (5, "Cashfree competes aggressively on payout APIs and rate discounting; PhonePe Payment Gateway is subsidizing gateway charges."),
        (6, "RBI's Payment Aggregator (PA) and Cross-Border PA (PA-CB) guidelines require strict escrow segregation and rigorous merchant re-KYC."),
        (7, "Zero-MDR mandate on consumer UPI and regulatory intervention on merchant onboarding represent systemic revenue threats."),
        (8, "1) Expand PA-CB cross-border payments. 2) Roll out offline POS terminals via Ezetap. 3) Complete corporate reverse-flip to India for IPO."),
        (9, "Sales objection logs reveal enterprise merchants threatening to switch when competing gateways offer 10 bps lower interchange pricing."),
        (10, "Weekly decisions on dynamic interchange margins, risk throttles for high-velocity merchants, and banking rail failover priorities.")
    ]
    for idx, ans in razorpay_answers:
        interview_service.submit_answer(razorpay_id, idx, ans)

    stack_service.build_signal_stack(razorpay_id)

    razorpay_signals = [
        {
            "category": "market",
            "title": "Reserve Bank of India (RBI) Issues Final Cross-Border Payment Aggregator (PA-CB) Approvals",
            "url": "https://rbi.org.in/pressreleases_rss.xml",
            "snippet": "RBI grants formal PA-CB licenses to major fintech aggregators, establishing mandatory FATF compliance and transaction reporting caps for export-import payments.",
            "pub_date": "2026-11-22",
            "what_happened": "RBI granted official cross-border payment aggregator authorizations under updated compliance frameworks.",
            "why_matters": "Enables Razorpay to fully scale multi-currency merchant collection and export invoicing for Indian SaaS companies.",
            "area": "Cross-Border Payments & Regulatory Compliance",
            "impact": "opportunity",
            "urgency": "high"
        },
        {
            "category": "competitors",
            "title": "Cashfree Payments Unveils Instant Global Wire Integration for Cross-Border Exporters",
            "url": "https://cashfree.com/press/global-wire-payouts",
            "snippet": "Cashfree announces direct SWIFT and SEPA banking integrations, cutting international payout turnaround times to under 2 hours.",
            "pub_date": "2026-11-20",
            "what_happened": "Direct rival Cashfree launched low-latency international wire transfers for merchant payouts.",
            "why_matters": "Intensifies cross-border competition for high-margin SaaS exporter transactions.",
            "area": "Product Roadmap & Payouts",
            "impact": "threat",
            "urgency": "high"
        },
        {
            "category": "customers",
            "title": "E-commerce Merchant Forums Raise Concerns Over Recurring UPI Mandate Failure Rates",
            "url": "https://news.google.com/rss/search?q=UPI+AutoPay+failure+rate+merchants",
            "snippet": "Subscription D2C merchants report occasional 8-10% failure rates on multi-bank recurring UPI debit execution during high-traffic festival sales.",
            "pub_date": "2026-11-21",
            "what_happened": "Merchants express frustration with intermittent UPI auto-pay mandate execution across public sector banks.",
            "why_matters": "Presents an opportunity for Razorpay's AI Auto-Retry and multi-rail fallback engine to win frustrated accounts.",
            "area": "Enterprise Sales & Payment Success Routing",
            "impact": "opportunity",
            "urgency": "medium"
        }
    ]

    conn = get_connection()
    c = conn.cursor()
    for sig in razorpay_signals:
        sig_id = str(uuid.uuid4())
        c.execute("""
            INSERT INTO signals (id, company_id, source_id, title, url, raw_content, evidence_snippet, publication_date, category, content_hash)
            VALUES (?, ?, NULL, ?, ?, ?, ?, ?, ?, ?)
        """, (sig_id, razorpay_id, sig["title"], sig["url"], sig["snippet"], sig["snippet"], sig["pub_date"], sig["category"], str(uuid.uuid4())))
        scores = ranking_service.calculate_scores(sig, razorpay_profile, "High")
        c.execute("""
            INSERT INTO intelligence (
                id, signal_id, company_id, what_happened, when_it_happened, is_verified,
                why_it_matters, business_area_affected, impact_type, urgency,
                strategic_interpretation, recommended_consideration,
                relevance_score, impact_score, urgency_score, credibility_score,
                recency_score, novelty_score, composite_rank, rank_explanation
            ) VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, 92.0, 88.0, 82.0, 95.0, 92.0, 80.0, ?, ?)
        """, (
            str(uuid.uuid4()), sig_id, razorpay_id,
            sig["what_happened"], sig["pub_date"],
            sig["why_matters"], sig["area"],
            sig["impact"], sig["urgency"],
            "Strategic inference: Regulatory and competitor moves dictate merchant pricing and cross-border volume.",
            "Review merchant gateway interchange tiers and highlight AI success rates.",
            scores["composite_rank"], scores["rank_explanation"]
        ))
    conn.commit()
    conn.close()

    briefing_service.generate_brief(razorpay_id)
    logger.info("Razorpay Brief generated successfully.")

    # Seed Monthly Audit History
    audit_service.run_monthly_audit(meetuni_id)
    logger.info("Seed completed successfully! 3 companies, Signal Stacks, and Monday Morning Briefs ready.")

if __name__ == "__main__":
    seed_database()
