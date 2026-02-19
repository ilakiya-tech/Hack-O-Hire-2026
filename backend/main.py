"""
main.py - FastAPI Backend for SAR Narrative Generator
All endpoints for SAR generation, approval, audit trail, and dashboard stats.
Run with: uvicorn backend.main:app --reload --port 8000
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json

from backend.database import (
    save_case, save_audit, approve_case,
    get_audit_trail, get_case, get_all_cases, get_stats, init_db
)
from llm.pipeline import generate_sar

# ─────────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────────
app = FastAPI(
    title="SAR Narrative Generator API",
    description="AI-powered Suspicious Activity Report generator with audit trail",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init DB on startup
init_db()


# ─────────────────────────────────────────────
# Request / Response Models
# ─────────────────────────────────────────────
class CaseInput(BaseModel):
    customer_name: str
    account_number: str
    transactions: str
    analyst_name: str
    additional_context: Optional[str] = ""


class ApprovalInput(BaseModel):
    case_id: int
    analyst_name: str
    edited_narrative: str


class RejectInput(BaseModel):
    case_id: int
    analyst_name: str
    reason: str


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "SAR Narrative Generator API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": [
            "POST /generate-sar",
            "POST /approve-sar",
            "POST /reject-sar",
            "GET  /audit-trail/{case_id}",
            "GET  /case/{case_id}",
            "GET  /all-cases",
            "GET  /stats"
        ]
    }


@app.post("/generate-sar")
async def generate_sar_endpoint(case_input: CaseInput):
    """
    Main endpoint: Takes transaction data → generates SAR narrative.
    Records full audit trail of what data and reasoning was used.
    """
    try:
        # Combine transactions with any additional context
        full_transaction_text = case_input.transactions
        if case_input.additional_context:
            full_transaction_text += f"\n\nADDITIONAL CONTEXT:\n{case_input.additional_context}"

        # Generate SAR via LLM pipeline
        result = generate_sar(
            transactions=full_transaction_text,
            customer_name=case_input.customer_name,
            account_number=case_input.account_number
        )

        # Save case to database
        case_id = save_case(
            data={
                "customer_name": case_input.customer_name,
                "account_number": case_input.account_number,
                "transactions": full_transaction_text,
                "analyst_name": case_input.analyst_name
            },
            sar_text=result["narrative"],
            risk_score=result["risk_score"],
            typology=result["typology"]
        )

        # Save audit trail entry
        save_audit(
            case_id=case_id,
            action="SAR_GENERATED",
            analyst=case_input.analyst_name,
            detail=f"SAR generated. Risk Score: {result['risk_score']}/100. Typology: {result['typology']}",
            data_used=result["audit_data"]
        )

        return {
            "success": True,
            "case_id": case_id,
            "sar_narrative": result["narrative"],
            "risk_score": result["risk_score"],
            "typology": result["typology"],
            "audit_summary": json.loads(result["audit_data"])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SAR generation failed: {str(e)}")


@app.post("/approve-sar")
async def approve_sar_endpoint(approval: ApprovalInput):
    """
    Analyst approves the SAR (with optional edits).
    Records approval in audit trail.
    """
    try:
        case = get_case(approval.case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        # Save approved case
        approve_case(
            case_id=approval.case_id,
            analyst=approval.analyst_name,
            edited_text=approval.edited_narrative
        )

        # Audit log the approval
        save_audit(
            case_id=approval.case_id,
            action="SAR_APPROVED",
            analyst=approval.analyst_name,
            detail="Analyst reviewed and approved SAR for filing.",
            data_used=json.dumps({
                "original_narrative_length": len(case.get("sar_narrative", "")),
                "final_narrative_length": len(approval.edited_narrative),
                "edits_made": approval.edited_narrative != case.get("sar_narrative", "")
            })
        )

        return {
            "success": True,
            "case_id": approval.case_id,
            "status": "APPROVED",
            "message": "SAR approved and ready for regulatory filing."
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reject-sar")
async def reject_sar_endpoint(reject: RejectInput):
    """Analyst rejects/sends back SAR for revision."""
    try:
        save_audit(
            case_id=reject.case_id,
            action="SAR_REJECTED",
            analyst=reject.analyst_name,
            detail=f"SAR rejected. Reason: {reject.reason}"
        )
        return {
            "success": True,
            "case_id": reject.case_id,
            "status": "REJECTED",
            "message": "SAR sent back for revision."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audit-trail/{case_id}")
async def get_audit_trail_endpoint(case_id: int):
    """
    Fetch complete audit trail for a case.
    Shows every action, timestamp, analyst, and data used.
    """
    trail = get_audit_trail(case_id)
    if not trail:
        raise HTTPException(status_code=404, detail="No audit trail found for this case")
    return {
        "case_id": case_id,
        "total_events": len(trail),
        "audit_trail": trail
    }


@app.get("/case/{case_id}")
async def get_case_endpoint(case_id: int):
    """Fetch a single case by ID."""
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@app.get("/all-cases")
async def get_all_cases_endpoint():
    """Fetch all SAR cases."""
    cases = get_all_cases()
    return {
        "total": len(cases),
        "cases": cases
    }


@app.get("/stats")
async def get_stats_endpoint():
    """Dashboard statistics."""
    return get_stats()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "SAR Generator API"}
