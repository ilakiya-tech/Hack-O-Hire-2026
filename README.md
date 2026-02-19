# 🏦 SAR Narrative Generator with Audit Trail
### Barclays Hack-O-Hire 2026 — AML Compliance Suite

AI-Powered • Fully Local • Regulator-Ready

---

## 🚨 Problem Statement

Suspicious Activity Reports (SARs) are critical for Anti-Money Laundering (AML) compliance.

Currently:

- ⏱️ 5–6 hours required to draft one SAR manually
- 📈 Banks generate thousands of SARs yearly
- ⚠️ Poor narratives risk regulatory enforcement
- 👨‍💼 Compliance teams are understaffed

Manual SAR drafting is slow, inconsistent, and difficult to audit.

---

## 💡 Our Solution

A **fully local AI-powered pipeline** that converts transaction data into a **regulator-ready SAR narrative in under 30 seconds**.

### Pipeline Flow

Transaction + KYC Data
↓
Risk Scoring Engine
↓
RAG Retrieval (ChromaDB)
↓
Local LLM Generation (Llama 3.1)
↓
Human Review & Approval


✅ 100% Offline  
✅ Zero External API Calls  
✅ Complete Audit Traceability  

---

## 🏗️ System Architecture

### Frontend
- Streamlit UI
- SAR Generation
- Review & Approval
- Dashboard & Audit Trail

### Backend
- FastAPI REST APIs
  - `/generate-sar`
  - `/approve-sar`
  - `/audit-trail`
  - `/stats`

### AI Pipeline
- LangChain orchestration
- ChromaDB RAG retrieval
- Llama 3.1 8B via Ollama

### Data Layer
- SQLite → Cases & Audit Logs
- ChromaDB → SAR Templates

---

## ⭐ Key Features

### 🤖 AI Narrative Generation
- 7-section regulator-ready SAR
- Generated in <30 seconds
- Fully local LLM execution

### 📊 Risk Scoring Engine
- 0–100 AML risk scoring
- Keyword + typology detection
- Supports multiple financial crime patterns

### 🔎 RAG Pipeline
- Retrieves relevant SAR templates
- Ensures structured narratives

### 📋 Full Audit Trail
Every action logged:
- Model used
- Prompt version
- Timestamp
- Analyst decisions

### 👨‍⚖️ Human-in-the-Loop
- Analysts edit
- Approve / Reject SAR
- Approval history stored

### 📈 Live Dashboard
- Risk distribution
- Case statistics
- Typology breakdown

---

## 🧪 Demo Scenarios

### High Risk — Money Laundering
- ₹50.2L received from 47 accounts
- Immediate SWIFT transfer to Dubai

### Structuring / Smurfing
- Multiple deposits below ₹50K threshold
- Cross-branch deposits

### Account Takeover
- VPN login anomaly
- Rapid fund extraction

---

## 🛠️ Technology Stack

| Component     | Technology           |
|---------------|----------------------|
| LLM           | Llama 3.1 8B (Ollama)|
| Backend       | FastAPI              |
| Frontend      | Streamlit            |
| RAG           | LangChain            |
| Vector DB     | ChromaDB             |
| Database      | SQLite               |
| Visualization | Plotly               |
| Language      | Python 3.10+         |

---

## 🚀 Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/ilakiya-tech/Hack-O-Hire-2026.git
cd sar-generator
2️⃣ Create Virtual Environment
python -m venv .venv
.venv\Scripts\activate
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Install Local LLM
ollama pull llama3.1:8b
5️⃣ Run Application
python run.py
🌐 Access Application
Service	URL
Frontend UI	http://localhost:8501
Backend API	http://localhost:8000
API Docs	http://localhost:8000/docs
📈 Impact
✅ 95% reduction in SAR drafting time

✅ Consistent regulatory formatting

✅ Full explainability

✅ Zero data leakage

✅ Scalable to thousands of cases

🔐 Security
Fully offline execution

No cloud dependency

Bank data never leaves system

Complete audit logging

👥 Built For
Barclays Hack-O-Hire 2026

Problem Statement 5 — AML Compliance Suite

📎 Submission Links
🔗 GitHub Repository:
https://github.com/ilakiya-tech/Hack-O-Hire-2026

❤️ Built With Passion for Financial Compliance Innovation