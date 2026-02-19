"""
app.py - Streamlit Frontend for SAR Narrative Generator
Full UI with: Generate SAR | Review & Approve | Audit Trail | Case History | Dashboard
Run with: streamlit run frontend/app.py
"""

import streamlit as st
import requests
import json
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.scenarios import DEMO_SCENARIOS, get_all_scenario_names

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────
API_URL = "http://localhost:8000"
st.set_page_config(
    page_title="SAR Narrative Generator | Barclays AML",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# Custom CSS Styling
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #00AEEF 0%, #003087 100%);
        padding: 20px 30px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
    }
    .main-header h1 { color: white; margin: 0; font-size: 28px; }
    .main-header p  { color: #e0f0ff; margin: 5px 0 0 0; font-size: 14px; }

    /* Risk score badge */
    .risk-high   { background: #ff4444; color: white; padding: 4px 12px; border-radius: 20px; font-weight: bold; }
    .risk-medium { background: #ff8800; color: white; padding: 4px 12px; border-radius: 20px; font-weight: bold; }
    .risk-low    { background: #00aa44; color: white; padding: 4px 12px; border-radius: 20px; font-weight: bold; }

    /* SAR narrative box */
    .sar-box {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-left: 4px solid #003087;
        padding: 20px;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        white-space: pre-wrap;
    }

    /* Status badges */
    .status-draft    { background: #ffc107; color: #333; padding: 3px 10px; border-radius: 4px; font-size: 12px; }
    .status-approved { background: #28a745; color: white; padding: 3px 10px; border-radius: 4px; font-size: 12px; }
    .status-rejected { background: #dc3545; color: white; padding: 3px 10px; border-radius: 4px; font-size: 12px; }

    /* Metric cards */
    .metric-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    .metric-number { font-size: 42px; font-weight: bold; color: #003087; }
    .metric-label  { font-size: 14px; color: #666; margin-top: 5px; }

    /* Audit timeline */
    .audit-event {
        background: #f8f9fa;
        border-left: 3px solid #00AEEF;
        padding: 10px 15px;
        margin: 8px 0;
        border-radius: 0 6px 6px 0;
    }
    .audit-action  { font-weight: bold; color: #003087; }
    .audit-time    { font-size: 12px; color: #888; }
    .audit-analyst { font-size: 13px; color: #555; }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────
def get_risk_color(score: int) -> str:
    if score >= 70: return "🔴"
    if score >= 40: return "🟡"
    return "🟢"

def get_risk_label(score: int) -> str:
    if score >= 70: return "HIGH RISK"
    if score >= 40: return "MEDIUM RISK"
    return "LOW RISK"

def api_call(method: str, endpoint: str, data: dict = None, params: dict = None):
    """Make API call with error handling."""
    try:
        url = f"{API_URL}{endpoint}"
        if method == "POST":
            response = requests.post(url, json=data, timeout=180)
        else:
            response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.ConnectionError:
        return None, "❌ Cannot connect to backend. Make sure FastAPI is running on port 8000."
    except requests.exceptions.Timeout:
        return None, "⏱️ Request timed out. LLM is still generating — please wait a moment and refresh."
    except Exception as e:
        return None, f"API Error: {str(e)}"


# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏦 SAR Narrative Generator</h1>
    <p>AI-Powered Suspicious Activity Report System | AML Compliance Suite | Fully Local & Secure</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Barclays_Logo.svg/320px-Barclays_Logo.svg.png", 
             width=160)
    st.markdown("---")
    st.markdown("### 🔐 Analyst Login")
    analyst_name = st.text_input("Your Name", value="Priya Verma", key="analyst")
    analyst_role = st.selectbox("Role", ["Analyst", "Senior Analyst", "AML Manager", "Compliance Officer"])
    
    st.markdown("---")
    st.markdown("### ⚡ Quick Stats")
    stats_data, err = api_call("GET", "/stats")
    if stats_data:
        st.metric("Total Cases", stats_data.get("total_cases", 0))
        st.metric("Approved SARs", stats_data.get("approved", 0))
        st.metric("Pending Review", stats_data.get("draft", 0))
        st.metric("High Risk Cases", stats_data.get("high_risk", 0))
    else:
        st.warning("Backend not connected")

    st.markdown("---")
    st.markdown("### ℹ️ System Info")
    st.markdown("🤖 **LLM:** Llama 3.1 8B (Local)")
    st.markdown("🔍 **RAG:** ChromaDB")
    st.markdown("🗄️ **DB:** SQLite")
    st.markdown("🔒 **Mode:** Fully Offline")
    st.markdown("📋 **Templates:** 5 Typologies")


# ─────────────────────────────────────────────
# Main Tabs
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Generate SAR",
    "✅ Review & Approve",
    "🔍 Audit Trail",
    "📊 Dashboard"
])


# ═══════════════════════════════════════════
# TAB 1: GENERATE SAR
# ═══════════════════════════════════════════
with tab1:
    st.markdown("### Generate SAR Narrative")
    st.markdown("Enter case details below or load a demo scenario to generate an AI-powered SAR narrative.")

    # Demo scenario loader
    col_demo, col_spacer = st.columns([2, 3])
    with col_demo:
        scenario_names = ["-- Enter manually --"] + get_all_scenario_names()
        selected_scenario = st.selectbox("🎯 Load Demo Scenario", scenario_names)

    # Pre-fill form if demo selected
    prefill = {}
    if selected_scenario != "-- Enter manually --":
        idx = scenario_names.index(selected_scenario) - 1
        prefill = DEMO_SCENARIOS[idx]
        st.success(f"✅ Demo scenario loaded: {selected_scenario}")

    st.markdown("---")

    # Input form
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 📋 Case Details")
        customer_name = st.text_input(
            "Customer Name *",
            value=prefill.get("customer_name", ""),
            placeholder="e.g. Rajesh Kumar Sharma"
        )
        account_number = st.text_input(
            "Account Number *",
            value=prefill.get("account_number", ""),
            placeholder="e.g. SB-4521-8834-2201"
        )
        transactions = st.text_area(
            "Transaction Details *",
            value=prefill.get("transactions", ""),
            height=280,
            placeholder="""Describe the suspicious transactions in detail:
- Dates and amounts
- Counterparties involved
- Transaction types (NEFT/IMPS/Cash/SWIFT)
- Any unusual patterns observed
- Customer profile information"""
        )
        additional_context = st.text_area(
            "Additional Context (optional)",
            value=prefill.get("additional_context", ""),
            height=100,
            placeholder="Any extra context for the analyst..."
        )

    with col2:
        st.markdown("#### 🚀 Generated SAR Narrative")

        generate_btn = st.button(
            "🔍 Generate SAR Narrative",
            type="primary",
            use_container_width=True,
            disabled=not (customer_name and transactions)
        )

        if generate_btn:
            if not customer_name or not transactions:
                st.error("Please fill in Customer Name and Transaction Details.")
            else:
                with st.spinner("🤖 AI is analyzing transactions and generating SAR narrative..."):
                    result, error = api_call("POST", "/generate-sar", {
                        "customer_name": customer_name,
                        "account_number": account_number,
                        "transactions": transactions,
                        "analyst_name": analyst_name,
                        "additional_context": additional_context
                    })

                if error:
                    st.error(error)
                elif result:
                    # Store in session
                    st.session_state.current_case_id = result["case_id"]
                    st.session_state.current_narrative = result["sar_narrative"]
                    st.session_state.current_risk = result["risk_score"]
                    st.session_state.current_typology = result["typology"]
                    st.session_state.current_audit = result.get("audit_summary", {})
                    st.success(f"✅ SAR Generated! Case ID: **#{result['case_id']}**")

        # Display results
        if "current_case_id" in st.session_state:
            risk = st.session_state.current_risk
            typology = st.session_state.current_typology

            # Risk score display
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("Case ID", f"#{st.session_state.current_case_id}")
            with col_r2:
                st.metric(
                    f"Risk Score {get_risk_color(risk)}",
                    f"{risk}/100",
                    delta=get_risk_label(risk)
                )
            with col_r3:
                st.metric("Typology", typology.split(" - ")[-1][:20])

            # Risk gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Risk Score", 'font': {'size': 14}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#ff4444" if risk >= 70 else "#ff8800" if risk >= 40 else "#00aa44"},
                    'steps': [
                        {'range': [0, 40], 'color': "#e8f5e9"},
                        {'range': [40, 70], 'color': "#fff3e0"},
                        {'range': [70, 100], 'color': "#ffebee"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 3},
                        'thickness': 0.8,
                        'value': 70
                    }
                }
            ))
            fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)

            # Narrative preview
            st.markdown("**Generated Narrative Preview:**")
            with st.expander("View Full SAR Narrative", expanded=True):
                st.markdown(st.session_state.current_narrative)

            st.info("👉 Go to **Review & Approve** tab to edit and approve this SAR.")

            # Audit summary
            if st.session_state.current_audit:
                with st.expander("🔍 Generation Audit Summary"):
                    audit = st.session_state.current_audit
                    st.markdown(f"**Model Used:** {audit.get('model_used', 'N/A')}")
                    st.markdown(f"**Typology Detected:** {audit.get('typology_detected', 'N/A')}")
                    st.markdown(f"**Risk Score:** {audit.get('risk_score', 'N/A')}/100")
                    st.markdown("**Processing Steps:**")
                    for step in audit.get("processing_steps", []):
                        st.markdown(f"- {step}")


# ═══════════════════════════════════════════
# TAB 2: REVIEW & APPROVE
# ═══════════════════════════════════════════
with tab2:
    st.markdown("### Review, Edit & Approve SAR")

    col_input, col_action = st.columns([1, 1])

    with col_input:
        # Load by case ID
        if "current_case_id" in st.session_state:
            default_id = st.session_state.current_case_id
        else:
            default_id = 1

        review_case_id = st.number_input("Enter Case ID to Review", min_value=1, value=default_id)
        load_btn = st.button("📂 Load Case", use_container_width=True)

        if load_btn or "current_case_id" in st.session_state:
            cid = review_case_id if load_btn else st.session_state.current_case_id
            case_data, err = api_call("GET", f"/case/{cid}")

            if err:
                st.error(err)
            elif case_data:
                st.session_state.review_case = case_data
                st.success(f"Case #{cid} loaded.")

    with col_action:
        if "review_case" in st.session_state:
            case = st.session_state.review_case
            risk = case.get("risk_score", 0)

            # Case metadata
            st.markdown(f"""
            | Field | Value |
            |-------|-------|
            | **Customer** | {case.get('customer_name', 'N/A')} |
            | **Account** | {case.get('account_number', 'N/A')} |
            | **Typology** | {case.get('typology', 'N/A')} |
            | **Risk Score** | {risk}/100 |
            | **Status** | {case.get('status', 'N/A')} |
            | **Created** | {case.get('created_at', 'N/A')[:16]} |
            """)

    # Full review area
    if "review_case" in st.session_state:
        case = st.session_state.review_case
        st.markdown("---")
        st.markdown("#### ✏️ Edit SAR Narrative Before Approval")
        st.markdown("You can edit the narrative below. All changes are tracked in the audit trail.")

        current_text = case.get("edited_narrative") or case.get("sar_narrative", "")

        edited_narrative = st.text_area(
            "SAR Narrative (editable)",
            value=current_text,
            height=450,
            key="edit_area"
        )

        col_approve, col_reject = st.columns(2)

        with col_approve:
            if st.button("✅ Approve & File SAR", type="primary", use_container_width=True):
                result, err = api_call("POST", "/approve-sar", {
                    "case_id": case["id"],
                    "analyst_name": analyst_name,
                    "edited_narrative": edited_narrative
                })
                if err:
                    st.error(err)
                else:
                    st.success(f"🎉 SAR #{case['id']} **APPROVED** and logged for regulatory filing!")
                    st.balloons()
                    # Clear review cache
                    if "review_case" in st.session_state:
                        del st.session_state.review_case

        with col_reject:
            reject_reason = st.text_input("Rejection reason (if rejecting)")
            if st.button("❌ Reject / Send Back", use_container_width=True):
                if not reject_reason:
                    st.warning("Please provide a rejection reason.")
                else:
                    result, err = api_call("POST", "/reject-sar", {
                        "case_id": case["id"],
                        "analyst_name": analyst_name,
                        "reason": reject_reason
                    })
                    if err:
                        st.error(err)
                    else:
                        st.warning(f"SAR #{case['id']} rejected and returned for revision.")


# ═══════════════════════════════════════════
# TAB 3: AUDIT TRAIL
# ═══════════════════════════════════════════
with tab3:
    st.markdown("### 🔍 Complete Audit Trail")
    st.markdown("Every action, decision, and data point used in SAR generation is recorded here.")

    col_at1, col_at2 = st.columns([1, 3])

    with col_at1:
        if "current_case_id" in st.session_state:
            default_audit_id = st.session_state.current_case_id
        else:
            default_audit_id = 1

        audit_case_id = st.number_input("Case ID", min_value=1, value=default_audit_id, key="audit_id")
        view_audit_btn = st.button("🔍 View Audit Trail", use_container_width=True)

    with col_at2:
        if view_audit_btn:
            audit_data, err = api_call("GET", f"/audit-trail/{audit_case_id}")

            if err:
                st.error(err)
            elif audit_data:
                st.markdown(f"**Case #{audit_case_id}** — {audit_data['total_events']} audit events recorded")
                st.markdown("---")

                for event in audit_data["audit_trail"]:
                    action = event.get("action", "")
                    icon = {"SAR_GENERATED": "🤖", "SAR_APPROVED": "✅", "SAR_REJECTED": "❌"}.get(action, "📋")

                    st.markdown(f"""
<div class="audit-event">
    <span class="audit-action">{icon} {action}</span>
    <span class="audit-time"> — {event.get('timestamp', '')[:19]}</span><br>
    <span class="audit-analyst">👤 Analyst: <b>{event.get('analyst', 'N/A')}</b></span><br>
    <span style="color:#333; font-size:13px;">📝 {event.get('detail', '')}</span>
</div>
""", unsafe_allow_html=True)

                    # Show detailed audit data if available
                    if event.get("data_used"):
                        with st.expander(f"🔬 Technical Details — {action}"):
                            try:
                                data_parsed = json.loads(event["data_used"])
                                st.json(data_parsed)
                            except Exception:
                                st.code(event["data_used"])


# ═══════════════════════════════════════════
# TAB 4: DASHBOARD
# ═══════════════════════════════════════════
with tab4:
    st.markdown("### 📊 AML Operations Dashboard")

    # Fetch all cases
    all_cases_data, err = api_call("GET", "/all-cases")

    if err:
        st.error(err)
        st.info("Start the FastAPI backend to see live dashboard data.")
    elif all_cases_data and all_cases_data.get("cases"):
        cases = all_cases_data["cases"]
        df = pd.DataFrame(cases)

        # Top metrics row
        stats, _ = api_call("GET", "/stats")
        if stats:
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-number">{stats['total_cases']}</div>
                    <div class="metric-label">Total Cases</div>
                </div>""", unsafe_allow_html=True)
            with m2:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-number" style="color:#28a745">{stats['approved']}</div>
                    <div class="metric-label">Approved SARs</div>
                </div>""", unsafe_allow_html=True)
            with m3:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-number" style="color:#ffc107">{stats['draft']}</div>
                    <div class="metric-label">Pending Review</div>
                </div>""", unsafe_allow_html=True)
            with m4:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-number" style="color:#ff4444">{stats['high_risk']}</div>
                    <div class="metric-label">High Risk Cases</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            # Risk distribution
            if "risk_score" in df.columns:
                df["risk_band"] = pd.cut(
                    df["risk_score"].fillna(0),
                    bins=[0, 40, 70, 100],
                    labels=["Low (0-40)", "Medium (40-70)", "High (70-100)"]
                )
                risk_counts = df["risk_band"].value_counts().reset_index()
                risk_counts.columns = ["Risk Band", "Count"]
                fig = px.pie(
                    risk_counts, values="Count", names="Risk Band",
                    title="Risk Score Distribution",
                    color_discrete_map={
                        "Low (0-40)": "#00aa44",
                        "Medium (40-70)": "#ff8800",
                        "High (70-100)": "#ff4444"
                    }
                )
                st.plotly_chart(fig, use_container_width=True)

        with col_chart2:
            # Typology breakdown
            if "typology" in df.columns and df["typology"].notna().any():
                typo_counts = df["typology"].value_counts().reset_index()
                typo_counts.columns = ["Typology", "Count"]
                typo_counts["Typology"] = typo_counts["Typology"].str[:30]
                fig2 = px.bar(
                    typo_counts, x="Count", y="Typology",
                    orientation="h",
                    title="Cases by Typology",
                    color="Count",
                    color_continuous_scale="Blues"
                )
                fig2.update_layout(yaxis_title="", showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

        # Cases table
        st.markdown("#### 📋 All SAR Cases")
        display_cols = ["id", "customer_name", "account_number", "typology", "risk_score", "status", "analyst_name", "created_at"]
        available_cols = [c for c in display_cols if c in df.columns]
        if available_cols:
            display_df = df[available_cols].copy()
            display_df.columns = [c.replace("_", " ").title() for c in available_cols]
            st.dataframe(display_df, use_container_width=True, hide_index=True)

    else:
        st.info("📭 No cases yet. Generate your first SAR in the **Generate SAR** tab!")

        # Show placeholder metrics
        m1, m2, m3, m4 = st.columns(4)
        for col, label, val in zip(
            [m1, m2, m3, m4],
            ["Total Cases", "Approved", "Pending", "High Risk"],
            [0, 0, 0, 0]
        ):
            with col:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-number">0</div>
                    <div class="metric-label">{label}</div>
                </div>""", unsafe_allow_html=True)
