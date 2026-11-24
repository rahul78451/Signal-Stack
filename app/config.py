import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
DOCS_DIR = BASE_DIR / "docs"

# Ensure runtime directories exist
DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
DOCS_DIR.mkdir(exist_ok=True)

class Settings(BaseModel):
    app_name: str = "Signal Stack — Company Intelligence & Executive Briefing Engine"
    version: str = "1.0.0"
    gemini_api_key: str = os.environ.get("GEMINI_API_KEY", "")
    host: str = os.environ.get("HOST", "0.0.0.0")
    port: int = int(os.environ.get("PORT", "8000"))
    db_path: str = str(DATA_DIR / "signal_stack.db")
    briefing_time: str = os.environ.get("DEFAULT_BRIEFING_TIME", "08:00")
    timezone: str = os.environ.get("DEFAULT_TIMEZONE", "Asia/Kolkata")
    monitoring_frequency_hours: int = int(os.environ.get("MONITORING_FREQUENCY_HOURS", "24"))
    audit_frequency_days: int = int(os.environ.get("AUDIT_FREQUENCY_DAYS", "30"))

settings = Settings()
