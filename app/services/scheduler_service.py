import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.config import settings
from app.database import get_connection
from app.services.crawler_service import crawler_service
from app.services.briefing_service import briefing_service
from app.services.audit_service import audit_service
from app.services.research_service import research_service

logger = logging.getLogger("SignalStack.Scheduler")

class SchedulerService:
    def __init__(self):
        self.is_running = False
        self._thread = None
        self.last_weekly_brief_run = None
        self.last_monthly_audit_run = None
        self.next_weekly_brief_run = None
        self.next_monthly_audit_run = None
        self.execution_logs = []

    def start(self):
        """Start the background scheduler thread."""
        if self.is_running:
            return

        self.is_running = True
        self.next_weekly_brief_run = (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S UTC")
        self.next_monthly_audit_run = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S UTC")

        self._thread = threading.Thread(target=self._scheduler_loop, daemon=True, name="SignalStack-Scheduler")
        self._thread.start()
        logger.info("SignalStack Background Automation Scheduler started.")

    def stop(self):
        self.is_running = False

    def _scheduler_loop(self):
        """Periodic loop checking schedule triggers."""
        while self.is_running:
            try:
                # Sleep in short intervals to allow clean shutdown
                time.sleep(60)
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")

    def trigger_weekly_brief_job(self, company_id: str = None) -> Dict[str, Any]:
        """Run weekly crawl, intelligence synthesis, and brief generation."""
        start_time = datetime.utcnow()
        companies = research_service.list_companies()
        if company_id:
            companies = [c for c in companies if c["id"] == company_id]

        results = []
        for c in companies:
            cid = c["id"]
            name = c["name"]
            try:
                crawl_res = crawler_service.crawl_sources_for_company(cid)
                brief_res = briefing_service.generate_brief(cid)
                results.append({
                    "company_id": cid,
                    "company_name": name,
                    "status": "success",
                    "signals_collected": crawl_res.get("new_signals_collected", 0),
                    "brief_id": brief_res.get("id")
                })
            except Exception as e:
                logger.error(f"Weekly brief failed for {name}: {e}")
                results.append({
                    "company_id": cid,
                    "company_name": name,
                    "status": "failed",
                    "error": str(e)
                })

        self.last_weekly_brief_run = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        self.next_weekly_brief_run = (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S UTC")

        log_entry = {
            "timestamp": self.last_weekly_brief_run,
            "job": "Weekly Intelligence Brief",
            "companies_processed": len(companies),
            "results": results
        }
        self.execution_logs.insert(0, log_entry)
        if len(self.execution_logs) > 50:
            self.execution_logs.pop()

        return log_entry

    def trigger_monthly_audit_job(self, company_id: str = None) -> Dict[str, Any]:
        """Run monthly signal stack audit."""
        audit_res = audit_service.run_monthly_audit(company_id)
        self.last_monthly_audit_run = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        self.next_monthly_audit_run = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S UTC")

        log_entry = {
            "timestamp": self.last_monthly_audit_run,
            "job": "Monthly Signal Stack Audit",
            "status": audit_res.get("status"),
            "summary": audit_res.get("summary")
        }
        self.execution_logs.insert(0, log_entry)
        return audit_res

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "briefing_time": settings.briefing_time,
            "timezone": settings.timezone,
            "monitoring_frequency_hours": settings.monitoring_frequency_hours,
            "audit_frequency_days": settings.audit_frequency_days,
            "last_weekly_brief_run": self.last_weekly_brief_run or "Manual / Pending initial run",
            "next_weekly_brief_run": self.next_weekly_brief_run or "Calculated upon startup",
            "last_monthly_audit_run": self.last_monthly_audit_run or "Manual / Pending initial run",
            "next_monthly_audit_run": self.next_monthly_audit_run or "Calculated upon startup",
            "recent_logs": self.execution_logs[:10]
        }

scheduler_service = SchedulerService()
