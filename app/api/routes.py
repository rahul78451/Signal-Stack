import uuid
import json
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from app.models.schemas import CompanyCreate, CompanyUpdate, AnswerSubmission, SourceCreate
from app.services.research_service import research_service
from app.services.interview_service import interview_service
from app.services.stack_service import stack_service
from app.services.file_parser import internal_file_parser
from app.services.crawler_service import crawler_service
from app.services.analysis_service import analysis_service
from app.services.briefing_service import briefing_service
from app.services.audit_service import audit_service
from app.services.scheduler_service import scheduler_service
from app.database import get_connection

api_router = APIRouter(prefix="/api")

# --- Company Endpoints ---

@api_router.post("/companies/setup")
def setup_company(payload: CompanyCreate):
    """Setup company and trigger initial research (facts vs assumptions)."""
    try:
        profile = research_service.research_company(payload.name, payload.website, payload.context_notes or "")
        return {"status": "success", "company": profile}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/companies")
def list_companies():
    return research_service.list_companies()

@api_router.get("/companies/{company_id}")
def get_company(company_id: str):
    c = research_service.get_company(company_id)
    if not c:
        raise HTTPException(status_code=404, detail="Company not found")
    return c

@api_router.put("/companies/{company_id}")
def update_company(company_id: str, payload: CompanyUpdate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Company not found")

    updates = []
    params = []
    if payload.name:
        updates.append("name = ?")
        params.append(payload.name)
    if payload.website:
        updates.append("website = ?")
        params.append(payload.website)
    if payload.industry:
        updates.append("industry = ?")
        params.append(payload.industry)
    if payload.description:
        updates.append("description = ?")
        params.append(payload.description)
    if payload.verified_facts is not None:
        updates.append("verified_facts = ?")
        params.append(json.dumps(payload.verified_facts))
    if payload.assumptions is not None:
        updates.append("assumptions = ?")
        params.append(json.dumps(payload.assumptions))
    if payload.target_customers is not None:
        updates.append("target_customers = ?")
        params.append(json.dumps(payload.target_customers))
    if payload.growth_priorities is not None:
        updates.append("growth_priorities = ?")
        params.append(json.dumps(payload.growth_priorities))
    if payload.context_notes is not None:
        updates.append("context_notes = ?")
        params.append(payload.context_notes)

    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(company_id)
        cursor.execute(f"UPDATE companies SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()

    conn.close()
    return research_service.get_company(company_id)

# --- Adaptive Interview Endpoints ---

@api_router.get("/interviews/{company_id}")
def get_interview(company_id: str):
    return interview_service.get_interview_state(company_id)

@api_router.post("/interviews/{company_id}/answer")
def submit_answer(company_id: str, payload: AnswerSubmission):
    return interview_service.submit_answer(company_id, payload.question_index, payload.answer_text, payload.is_skipped)

@api_router.put("/interviews/{company_id}/answer")
def edit_answer(company_id: str, payload: AnswerSubmission):
    return interview_service.edit_answer(company_id, payload.question_index, payload.answer_text)

# --- Signal Stack & Sources Endpoints ---

@api_router.post("/stack/{company_id}/build")
def build_stack(company_id: str):
    try:
        return stack_service.build_signal_stack(company_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/stack/{company_id}")
def get_stack(company_id: str):
    return stack_service.get_stack(company_id)

@api_router.post("/stack/{company_id}/source")
def add_source(company_id: str, payload: SourceCreate):
    return stack_service.add_custom_source(company_id, payload.dict())

@api_router.delete("/stack/source/{source_id}")
def delete_source(source_id: str):
    return {"success": stack_service.remove_source(source_id)}

@api_router.patch("/stack/source/{source_id}/toggle")
def toggle_source(source_id: str):
    return stack_service.toggle_source_active(source_id)

class ContextChangeRequest(BaseModel):
    new_context: str

@api_router.post("/stack/{company_id}/context-change")
def context_change(company_id: str, payload: ContextChangeRequest):
    """Stress test: Reassesses sources and stack on business context change."""
    return stack_service.reassess_for_context_change(company_id, payload.new_context)

# --- Internal Document Upload ---

@api_router.post("/stack/{company_id}/upload-internal")
async def upload_internal_doc(company_id: str, file: UploadFile = File(...)):
    """Upload CSV, Excel, PDF, or TXT internal signals."""
    content = await file.read()
    parsed = internal_file_parser.parse_file(file.filename, content)

    # Insert parsed insights as internal signals
    conn = get_connection()
    cursor = conn.cursor()
    inserted_count = 0
    for ins in parsed.get("insights", []):
        sig_id = str(uuid.uuid4())
        title = f"[Internal {file.filename}] {ins.get('pattern', 'Feedback')}"
        evidence = ins.get("sales_objection_or_risk", "")
        cursor.execute("""
            INSERT INTO signals (
                id, company_id, source_id, title, url,
                raw_content, evidence_snippet, publication_date, category, content_hash
            ) VALUES (?, ?, NULL, ?, ?, ?, ?, CURRENT_TIMESTAMP, 'internal', ?)
        """, (
            sig_id, company_id, title, f"internal://{file.filename}",
            evidence, evidence, str(uuid.uuid4())
        ))
        inserted_count += 1

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "filename": file.filename,
        "signals_created": inserted_count,
        "parsed_preview": parsed
    }

# --- Monitoring, Crawling & Intelligence Feed ---

@api_router.post("/crawler/{company_id}/run")
def run_crawler(company_id: str):
    """Manually crawl active sources and collect new signals."""
    return crawler_service.crawl_sources_for_company(company_id)

@api_router.post("/analysis/{company_id}/run")
def run_analysis(company_id: str):
    """Analyze pending signals into the 9 dimensions and rankings."""
    count = analysis_service.process_unanalyzed_signals(company_id)
    return {"status": "success", "signals_analyzed": count}

@api_router.get("/intelligence/{company_id}/feed")
def get_feed(company_id: str, category: Optional[str] = "all", impact_type: Optional[str] = "all", urgency: Optional[str] = "all"):
    """Chronological intelligence feed filterable by category, impact, urgency."""
    return analysis_service.get_intelligence_feed(company_id, category, impact_type, urgency)

# --- Monday Morning Executive Brief ---

@api_router.post("/briefs/{company_id}/generate")
def generate_brief(company_id: str):
    """Generate and save complete 10-section executive brief."""
    return briefing_service.generate_brief(company_id)

@api_router.get("/briefs/{company_id}/latest")
def get_latest_brief(company_id: str):
    brief = briefing_service.get_latest_brief(company_id)
    if not brief:
        return {"has_brief": False}
    return {"has_brief": True, "brief": brief}

@api_router.get("/briefs/{company_id}/actions")
def get_actions(company_id: str):
    return briefing_service.get_action_items(company_id)

class ActionStatusUpdate(BaseModel):
    status: str # 'pending', 'in_progress', 'completed'

@api_router.patch("/briefs/actions/{action_id}")
def update_action(action_id: str, payload: ActionStatusUpdate):
    return {"success": briefing_service.update_action_status(action_id, payload.status)}

# --- Monthly Audit & Automation Scheduler ---

@api_router.post("/audit/{company_id}/run")
def run_audit(company_id: str):
    return audit_service.run_monthly_audit(company_id)

@api_router.get("/audit/{company_id}/history")
def get_audit_history(company_id: str):
    return audit_service.get_audit_history(company_id)

@api_router.get("/scheduler/status")
def scheduler_status():
    return scheduler_service.get_status()

@api_router.post("/scheduler/trigger-brief")
def trigger_brief():
    return scheduler_service.trigger_weekly_brief_job()

@api_router.post("/scheduler/trigger-audit")
def trigger_audit():
    return scheduler_service.trigger_monthly_audit_job()
