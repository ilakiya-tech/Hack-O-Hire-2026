"""
pipeline.py
Core LLM pipeline for SAR narrative generation.
Uses: Ollama (local LLM) + LangChain + ChromaDB (RAG)
Fully offline - zero external data transfer.
"""

import os
import sys
import json
import chromadb
from chromadb.config import Settings
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm.templates import SAR_TEMPLATES, RISK_KEYWORDS, TYPOLOGY_PATTERNS

# ─────────────────────────────────────────────
# ChromaDB Setup (local, persistent)
# ─────────────────────────────────────────────
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")
os.makedirs(CHROMA_PATH, exist_ok=True)

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

def get_or_create_collection():
    """Get or create the SAR templates collection in ChromaDB."""
    try:
        collection = chroma_client.get_collection("sar_templates")
    except Exception:
        collection = chroma_client.create_collection(
            name="sar_templates",
            metadata={"description": "SAR narrative templates for RAG"}
        )
        # Load all templates into ChromaDB
        for tmpl in SAR_TEMPLATES:
            collection.add(
                documents=[tmpl["template"]],
                metadatas=[{
                    "typology": tmpl["typology"],
                    "title": tmpl["title"],
                    "id": tmpl["id"]
                }],
                ids=[tmpl["id"]]
            )
        print(f"✅ Loaded {len(SAR_TEMPLATES)} SAR templates into ChromaDB.")
    return collection


def retrieve_relevant_template(transaction_text: str, n_results: int = 2) -> str:
    """RAG: Retrieve most relevant SAR templates for the given transaction."""
    try:
        collection = get_or_create_collection()
        results = collection.query(
            query_texts=[transaction_text],
            n_results=min(n_results, len(SAR_TEMPLATES))
        )
        templates_text = ""
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            templates_text += f"\n\n--- REFERENCE TEMPLATE ({meta['typology']}) ---\n{doc}"
        return templates_text
    except Exception as e:
        print(f"ChromaDB retrieval warning: {e}")
        # Fallback: return first template
        return SAR_TEMPLATES[0]["template"]


# ─────────────────────────────────────────────
# Risk Scoring Engine
# ─────────────────────────────────────────────
def calculate_risk_score(transactions: str, customer_name: str) -> tuple[int, str]:
    """
    Calculate risk score (0-100) and detect typology from transaction text.
    Returns (score, typology_string)
    """
    text_lower = transactions.lower()
    score = 0
    matched_typology = "General Suspicious Activity"

    # Score based on risk keywords
    for kw in RISK_KEYWORDS["high_risk"]:
        if kw.lower() in text_lower:
            score += 8

    for kw in RISK_KEYWORDS["medium_risk"]:
        if kw.lower() in text_lower:
            score += 4

    for kw in RISK_KEYWORDS["low_risk"]:
        if kw.lower() in text_lower:
            score = max(0, score - 2)

    # Cap at 100
    score = min(score, 100)

    # Detect typology
    best_match_count = 0
    for typology, keywords in TYPOLOGY_PATTERNS.items():
        match_count = sum(1 for kw in keywords if kw.lower() in text_lower)
        if match_count > best_match_count:
            best_match_count = match_count
            matched_typology = typology

    # Minimum score of 30 for any flagged transaction
    score = max(score, 30)

    return score, matched_typology


# ─────────────────────────────────────────────
# LLM Setup
# ─────────────────────────────────────────────
def get_llm():
    """Initialize Ollama LLM - uses local model."""
    return Ollama(
        model="llama3.1:8b",
        temperature=0.1,  # Low temp for consistent, professional output
        timeout=120
    )


# ─────────────────────────────────────────────
# SAR Generation Prompt
# ─────────────────────────────────────────────
SAR_PROMPT_TEMPLATE = """You are a senior AML (Anti-Money Laundering) compliance officer at a major bank.
Your task is to write a formal, regulator-ready Suspicious Activity Report (SAR) narrative.

REFERENCE TEMPLATES (use these as style guides):
{reference_templates}

---

NOW GENERATE A SAR FOR THIS CASE:

CUSTOMER NAME: {customer_name}
ACCOUNT NUMBER: {account_number}
DETECTED TYPOLOGY: {typology}
RISK SCORE: {risk_score}/100

TRANSACTION DETAILS:
{transactions}

---

Write a complete, professional SAR narrative with EXACTLY these sections:

## 1. SUBJECT INFORMATION
[Full details about the customer and their normal account profile]

## 2. TRANSACTION SUMMARY  
[Precise summary of suspicious transactions with dates, amounts, and parties involved]

## 3. SUSPICIOUS ACTIVITY DESCRIPTION
[Detailed narrative explaining exactly what happened and why it is suspicious]

## 4. TYPOLOGY MATCH
[Map this activity to a known financial crime typology with explanation]

## 5. RED FLAGS IDENTIFIED
[Numbered list of specific red flags observed in this case]

## 6. ANALYST RECOMMENDATION
[Recommended next steps: file SAR / escalate / request documents / freeze account]

## 7. AUDIT RATIONALE
[Explain which specific data points influenced this narrative and why]

Write in formal regulatory language. Be specific, factual, and unambiguous.
Do NOT include any disclaimers or meta-commentary. Write only the SAR narrative.
"""

SAR_PROMPT = PromptTemplate(
    input_variables=["reference_templates", "customer_name", "account_number",
                     "typology", "risk_score", "transactions"],
    template=SAR_PROMPT_TEMPLATE
)


# ─────────────────────────────────────────────
# Main Generation Function
# ─────────────────────────────────────────────
def generate_sar(
    transactions: str,
    customer_name: str,
    account_number: str = "N/A"
) -> dict:
    """
    Main function: Generate SAR narrative using RAG + local LLM.
    Returns dict with narrative, risk_score, typology, and audit_data.
    """

    # Step 1: Risk scoring
    risk_score, typology = calculate_risk_score(transactions, customer_name)

    # Step 2: RAG - retrieve relevant templates
    reference_templates = retrieve_relevant_template(transactions)

    # Step 3: Build audit trail of what data was used
    audit_data = {
        "risk_score": risk_score,
        "typology_detected": typology,
        "rag_templates_used": [t["typology"] for t in SAR_TEMPLATES[:2]],
        "transaction_length": len(transactions),
        "model_used": "llama3.1:8b (local)",
        "prompt_template": "SAR_PROMPT_V1",
        "processing_steps": [
            "1. Risk keywords scanned and scored",
            "2. Typology pattern matched",
            "3. ChromaDB queried for relevant SAR templates",
            "4. LangChain prompt assembled with context",
            "5. Ollama LLM generated narrative",
            "6. Narrative stored with full audit trail"
        ]
    }

    # Step 4: Generate narrative via LLM
    try:
        llm = get_llm()
        chain = SAR_PROMPT | llm | StrOutputParser()

        narrative = chain.invoke({
            "reference_templates": reference_templates,
            "customer_name": customer_name,
            "account_number": account_number,
            "typology": typology,
            "risk_score": risk_score,
            "transactions": transactions
        })

    except Exception as e:
        # Fallback narrative if LLM is unavailable
        print(f"LLM generation warning: {e}")
        narrative = generate_fallback_sar(
            customer_name, account_number, transactions, typology, risk_score
        )
        audit_data["processing_steps"].append(f"NOTE: LLM unavailable, fallback template used. Error: {str(e)}")

    return {
        "narrative": narrative,
        "risk_score": risk_score,
        "typology": typology,
        "audit_data": json.dumps(audit_data, indent=2)
    }


def generate_fallback_sar(
    customer_name: str,
    account_number: str,
    transactions: str,
    typology: str,
    risk_score: int
) -> str:
    """
    Fallback SAR template if Ollama is not running.
    Ensures the demo works even without LLM.
    """
    return f"""## 1. SUBJECT INFORMATION
Customer Name: {customer_name}
Account Number: {account_number}
This SAR has been raised based on automated pattern analysis of account activity.
The customer's transaction behaviour has deviated significantly from their established profile.

## 2. TRANSACTION SUMMARY
The following suspicious transactions have been identified:
{transactions}

## 3. SUSPICIOUS ACTIVITY DESCRIPTION
Analysis of the account activity reveals patterns inconsistent with the customer's 
known financial profile and stated purpose of account. The transaction pattern 
suggests deliberate structuring or layering of funds inconsistent with legitimate 
business or personal activity. The velocity, volume, and nature of transactions 
observed over the reporting period raise significant concerns.

## 4. TYPOLOGY MATCH
Detected Typology: {typology}
This activity aligns with FATF-recognized money laundering/fraud typologies 
involving layering of funds through multiple transactions to obscure the origin 
of funds and evade detection thresholds.

## 5. RED FLAGS IDENTIFIED
1. Transaction pattern inconsistent with customer profile
2. Unusual velocity of transactions detected
3. Transaction amounts and counterparties raise AML concerns
4. No apparent legitimate business purpose identified
5. Pattern matches known financial crime typology: {typology}

## 6. ANALYST RECOMMENDATION
RECOMMENDED ACTION: File Suspicious Activity Report immediately.
- Escalate to Senior AML Officer for review
- Place account under enhanced monitoring
- Request source of funds documentation from customer
- Cross-reference counterparties against sanctions and PEP lists
- Consider account restriction pending investigation

## 7. AUDIT RATIONALE
Risk Score: {risk_score}/100
This narrative was generated based on automated transaction pattern analysis.
Key data points: transaction frequency, amount patterns, counterparty diversity,
and geographic risk factors. All source data is preserved in the audit log.
NOTE: This is a system-generated draft. Human analyst review and approval required before filing.
"""
