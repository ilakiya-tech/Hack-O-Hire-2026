"""
database.py
SQLite database setup and all CRUD operations for SAR Generator.
Uses SQLAlchemy for ORM - zero external DB setup needed.
"""

from sqlalchemy import create_engine, text
import datetime
import json
import os

# SQLite DB file in project root
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "sar_cases.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


def init_db():
    """Create all tables if they don't exist."""
    with engine.connect() as conn:
        # Cases table - stores every SAR case
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS cases (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name   TEXT NOT NULL,
                account_number  TEXT NOT NULL,
                transactions    TEXT NOT NULL,
                sar_narrative   TEXT,
                status          TEXT DEFAULT 'DRAFT',
                analyst_name    TEXT,
                created_at      TEXT,
                approved_at     TEXT,
                approved_by     TEXT,
                edited_narrative TEXT,
                risk_score      INTEGER DEFAULT 0,
                typology        TEXT
            )
        """))

        # Audit log - every action on every case
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id     INTEGER NOT NULL,
                action      TEXT NOT NULL,
                analyst     TEXT,
                detail      TEXT,
                timestamp   TEXT,
                data_used   TEXT
            )
        """))

        # SAR templates loaded into ChromaDB reference
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sar_templates (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT,
                typology    TEXT,
                template    TEXT,
                created_at  TEXT
            )
        """))
        conn.commit()
    print("✅ Database initialized successfully.")


def save_case(data: dict, sar_text: str, risk_score: int = 0, typology: str = "") -> int:
    """Save a new SAR case and return the case ID."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            INSERT INTO cases 
                (customer_name, account_number, transactions, sar_narrative,
                 status, analyst_name, created_at, risk_score, typology)
            VALUES 
                (:cn, :an, :tx, :sar, 'DRAFT', :analyst, :ts, :rs, :typo)
        """), {
            "cn": data.get("customer_name", ""),
            "an": data.get("account_number", ""),
            "tx": data.get("transactions", ""),
            "sar": sar_text,
            "analyst": data.get("analyst_name", "Unknown"),
            "ts": str(datetime.datetime.now()),
            "rs": risk_score,
            "typo": typology
        })
        conn.commit()
        return result.lastrowid


def save_audit(case_id: int, action: str, analyst: str, detail: str = "", data_used: str = ""):
    """Log every action taken on a case."""
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO audit_log (case_id, action, analyst, detail, timestamp, data_used)
            VALUES (:ci, :ac, :an, :dt, :ts, :du)
        """), {
            "ci": case_id,
            "ac": action,
            "an": analyst,
            "dt": detail,
            "ts": str(datetime.datetime.now()),
            "du": data_used
        })
        conn.commit()


def approve_case(case_id: int, analyst: str, edited_text: str):
    """Mark a case as approved with the final narrative."""
    with engine.connect() as conn:
        conn.execute(text("""
            UPDATE cases 
            SET status='APPROVED', approved_by=:analyst,
                approved_at=:ts, edited_narrative=:et
            WHERE id=:id
        """), {
            "analyst": analyst,
            "ts": str(datetime.datetime.now()),
            "et": edited_text,
            "id": case_id
        })
        conn.commit()


def get_audit_trail(case_id: int) -> list:
    """Fetch full audit trail for a case."""
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT * FROM audit_log WHERE case_id=:id ORDER BY timestamp ASC
        """), {"id": case_id}).fetchall()
        return [dict(r._mapping) for r in rows]


def get_case(case_id: int) -> dict:
    """Fetch a single case by ID."""
    with engine.connect() as conn:
        row = conn.execute(text(
            "SELECT * FROM cases WHERE id=:id"), {"id": case_id}).fetchone()
        return dict(row._mapping) if row else {}


def get_all_cases() -> list:
    """Fetch all cases ordered by newest first."""
    with engine.connect() as conn:
        rows = conn.execute(text(
            "SELECT * FROM cases ORDER BY created_at DESC")).fetchall()
        return [dict(r._mapping) for r in rows]


def get_stats() -> dict:
    """Dashboard stats."""
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM cases")).scalar()
        approved = conn.execute(text(
            "SELECT COUNT(*) FROM cases WHERE status='APPROVED'")).scalar()
        draft = conn.execute(text(
            "SELECT COUNT(*) FROM cases WHERE status='DRAFT'")).scalar()
        high_risk = conn.execute(text(
            "SELECT COUNT(*) FROM cases WHERE risk_score >= 70")).scalar()
        return {
            "total_cases": total,
            "approved": approved,
            "draft": draft,
            "high_risk": high_risk
        }


# Initialize DB on import
init_db()
