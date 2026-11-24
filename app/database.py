import sqlite3
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.config import settings

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS companies (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        website TEXT NOT NULL,
        industry TEXT,
        description TEXT,
        verified_facts TEXT DEFAULT '[]',
        assumptions TEXT DEFAULT '[]',
        target_customers TEXT DEFAULT '[]',
        value_propositions TEXT DEFAULT '[]',
        revenue_streams TEXT DEFAULT '[]',
        growth_priorities TEXT DEFAULT '[]',
        context_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS interviews (
        id TEXT PRIMARY KEY,
        company_id TEXT NOT NULL,
        question_index INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        context_category TEXT NOT NULL,
        answer_text TEXT DEFAULT '',
        is_skipped INTEGER DEFAULT 0,
        follow_up_notes TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS sources (
        id TEXT PRIMARY KEY,
        company_id TEXT NOT NULL,
        category TEXT NOT NULL, -- 'customers', 'competitors', 'market', 'internal'
        name TEXT NOT NULL,
        url TEXT NOT NULL,
        source_type TEXT NOT NULL, -- 'rss', 'web_page', 'google_news', 'reddit_forum', 'regulatory', 'internal_file'
        reason_for_inclusion TEXT NOT NULL,
        credibility_tier TEXT DEFAULT 'High', -- 'High', 'Medium', 'Standard'
        recency_expectation TEXT DEFAULT 'Daily',
        is_approved INTEGER DEFAULT 1,
        is_active INTEGER DEFAULT 1,
        last_crawled_at TIMESTAMP,
        last_status TEXT DEFAULT 'healthy', -- 'healthy', 'dead', 'inactive', 'warning'
        health_score INTEGER DEFAULT 100,
        duplicate_of_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS competitors (
        id TEXT PRIMARY KEY,
        company_id TEXT NOT NULL,
        name TEXT NOT NULL,
        website TEXT NOT NULL,
        relationship TEXT DEFAULT 'Direct', -- 'Direct', 'Substitute', 'Adjacent'
        core_offerings TEXT,
        pricing_model TEXT,
        positioning TEXT,
        threat_level TEXT DEFAULT 'Medium', -- 'High', 'Medium', 'Low'
        reason_it_matters TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS signals (
        id TEXT PRIMARY KEY,
        company_id TEXT NOT NULL,
        source_id TEXT,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        raw_content TEXT,
        evidence_snippet TEXT NOT NULL,
        publication_date TEXT,
        discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        category TEXT NOT NULL,
        content_hash TEXT UNIQUE,
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
        FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS intelligence (
        id TEXT PRIMARY KEY,
        signal_id TEXT NOT NULL,
        company_id TEXT NOT NULL,
        what_happened TEXT NOT NULL,
        when_it_happened TEXT NOT NULL,
        is_verified INTEGER DEFAULT 1,
        why_it_matters TEXT NOT NULL,
        business_area_affected TEXT NOT NULL,
        impact_type TEXT NOT NULL, -- 'opportunity', 'threat', 'neutral'
        urgency TEXT NOT NULL, -- 'high', 'medium', 'low'
        strategic_interpretation TEXT NOT NULL,
        recommended_consideration TEXT NOT NULL,
        relevance_score REAL DEFAULT 50.0,
        impact_score REAL DEFAULT 50.0,
        urgency_score REAL DEFAULT 50.0,
        credibility_score REAL DEFAULT 50.0,
        recency_score REAL DEFAULT 50.0,
        novelty_score REAL DEFAULT 50.0,
        composite_rank REAL DEFAULT 50.0,
        rank_explanation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (signal_id) REFERENCES signals(id) ON DELETE CASCADE,
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS briefs (
        id TEXT PRIMARY KEY,
        company_id TEXT NOT NULL,
        brief_title TEXT NOT NULL,
        generation_date TEXT NOT NULL,
        period_label TEXT NOT NULL,
        executive_summary TEXT DEFAULT '[]',
        customer_signals TEXT DEFAULT '[]',
        competitor_signals TEXT DEFAULT '[]',
        market_signals TEXT DEFAULT '[]',
        internal_signals TEXT DEFAULT '[]',
        opportunities TEXT DEFAULT '[]',
        risks_threats TEXT DEFAULT '[]',
        recommended_actions TEXT DEFAULT '[]',
        what_to_watch TEXT DEFAULT '[]',
        source_appendix TEXT DEFAULT '[]',
        markdown_content TEXT NOT NULL,
        json_content TEXT NOT NULL,
        is_published INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS audit_logs (
        id TEXT PRIMARY KEY,
        company_id TEXT,
        run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        run_type TEXT NOT NULL, -- 'weekly_brief', 'monthly_audit'
        status TEXT NOT NULL, -- 'success', 'warning', 'failed'
        dead_urls_count INTEGER DEFAULT 0,
        inactive_sources_count INTEGER DEFAULT 0,
        declining_relevance_count INTEGER DEFAULT 0,
        newly_discovered_count INTEGER DEFAULT 0,
        report_details TEXT DEFAULT '{}',
        failure_reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS action_items (
        id TEXT PRIMARY KEY,
        brief_id TEXT NOT NULL,
        company_id TEXT NOT NULL,
        action_text TEXT NOT NULL,
        priority TEXT DEFAULT 'Medium', -- 'High', 'Medium', 'Low'
        reason TEXT NOT NULL,
        suggested_owner TEXT NOT NULL,
        status TEXT DEFAULT 'pending', -- 'pending', 'in_progress', 'completed'
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (brief_id) REFERENCES briefs(id) ON DELETE CASCADE,
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_signals_company ON signals(company_id);
    CREATE INDEX IF NOT EXISTS idx_intelligence_company ON intelligence(company_id);
    CREATE INDEX IF NOT EXISTS idx_sources_company ON sources(company_id);
    CREATE INDEX IF NOT EXISTS idx_briefs_company ON briefs(company_id);
    """);

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
