from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# --- Company Schemas ---
class CompanyCreate(BaseModel):
    name: str
    website: str
    industry: Optional[str] = None
    context_notes: Optional[str] = None

class CompanyProfile(BaseModel):
    id: str
    name: str
    website: str
    industry: str
    description: str
    verified_facts: List[str] = []
    assumptions: List[str] = []
    target_customers: List[str] = []
    value_propositions: List[str] = []
    revenue_streams: List[str] = []
    growth_priorities: List[str] = []
    context_notes: Optional[str] = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    verified_facts: Optional[List[str]] = None
    assumptions: Optional[List[str]] = None
    target_customers: Optional[List[str]] = None
    value_propositions: Optional[List[str]] = None
    revenue_streams: Optional[List[str]] = None
    growth_priorities: Optional[List[str]] = None
    context_notes: Optional[str] = None

# --- Interview Schemas ---
class InterviewQuestion(BaseModel):
    id: str
    company_id: str
    question_index: int
    question_text: str
    context_category: str
    answer_text: str = ""
    is_skipped: bool = False
    follow_up_notes: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class AnswerSubmission(BaseModel):
    question_index: int
    answer_text: str
    is_skipped: bool = False

# --- Source & Competitor Schemas ---
class SourceItem(BaseModel):
    id: str
    company_id: str
    category: str # 'customers', 'competitors', 'market', 'internal'
    name: str
    url: str
    source_type: str # 'rss', 'web_page', 'google_news', 'reddit_forum', 'regulatory', 'internal_file'
    reason_for_inclusion: str
    credibility_tier: str = "High"
    recency_expectation: str = "Daily"
    is_approved: bool = True
    is_active: bool = True
    last_crawled_at: Optional[str] = None
    last_status: str = "healthy"
    health_score: int = 100
    duplicate_of_id: Optional[str] = None
    created_at: Optional[str] = None

class SourceCreate(BaseModel):
    category: str
    name: str
    url: str
    source_type: str
    reason_for_inclusion: str
    credibility_tier: str = "High"
    recency_expectation: str = "Daily"

class CompetitorItem(BaseModel):
    id: str
    company_id: str
    name: str
    website: str
    relationship: str = "Direct"
    core_offerings: Optional[str] = ""
    pricing_model: Optional[str] = ""
    positioning: Optional[str] = ""
    threat_level: str = "Medium"
    reason_it_matters: str
    created_at: Optional[str] = None

# --- Signal & Intelligence Schemas ---
class SignalItem(BaseModel):
    id: str
    company_id: str
    source_id: Optional[str] = None
    title: str
    url: str
    raw_content: Optional[str] = None
    evidence_snippet: str
    publication_date: Optional[str] = None
    discovered_at: Optional[str] = None
    category: str

class IntelligenceItem(BaseModel):
    id: str
    signal_id: str
    company_id: str
    what_happened: str
    when_it_happened: str
    is_verified: bool
    why_it_matters: str
    business_area_affected: str
    impact_type: str # 'opportunity', 'threat', 'neutral'
    urgency: str # 'high', 'medium', 'low'
    strategic_interpretation: str
    recommended_consideration: str
    relevance_score: float = 50.0
    impact_score: float = 50.0
    urgency_score: float = 50.0
    credibility_score: float = 50.0
    recency_score: float = 50.0
    novelty_score: float = 50.0
    composite_rank: float = 50.0
    rank_explanation: Optional[str] = None
    created_at: Optional[str] = None
    # Joined signal fields for UI
    title: Optional[str] = None
    url: Optional[str] = None
    evidence_snippet: Optional[str] = None
    category: Optional[str] = None
    source_name: Optional[str] = None

# --- Brief Schemas ---
class MondayBriefItem(BaseModel):
    id: str
    company_id: str
    brief_title: str
    generation_date: str
    period_label: str
    executive_summary: List[Dict[str, Any]] = []
    customer_signals: List[Dict[str, Any]] = []
    competitor_signals: List[Dict[str, Any]] = []
    market_signals: List[Dict[str, Any]] = []
    internal_signals: List[Dict[str, Any]] = []
    opportunities: List[Dict[str, Any]] = []
    risks_threats: List[Dict[str, Any]] = []
    recommended_actions: List[Dict[str, Any]] = []
    what_to_watch: List[Dict[str, Any]] = []
    source_appendix: List[Dict[str, Any]] = []
    markdown_content: str
    json_content: str
    is_published: bool = True
    created_at: Optional[str] = None

class ActionItemModel(BaseModel):
    id: str
    brief_id: str
    company_id: str
    action_text: str
    priority: str
    reason: str
    suggested_owner: str
    status: str
    updated_at: Optional[str] = None

class AuditReportModel(BaseModel):
    id: str
    company_id: Optional[str] = None
    run_date: str
    run_type: str
    status: str
    dead_urls_count: int
    inactive_sources_count: int
    declining_relevance_count: int
    newly_discovered_count: int
    report_details: Dict[str, Any] = {}
    failure_reason: Optional[str] = None
