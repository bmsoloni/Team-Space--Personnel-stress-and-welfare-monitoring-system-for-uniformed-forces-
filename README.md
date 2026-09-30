# 🛡️ CRPF AI-Based Predictive Personnel Stress & Welfare Monitoring System
**Problem Statement #26186 | Ministry of Home Affairs | CRPF**

## Tech Stack
| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite + Redux Toolkit |
| Backend | Python Flask 3.x + Blueprints |
| Database | MySQL 8.x + SQLAlchemy |
| AI Engine | XGBoost + scikit-learn + SHAP |
| RAG Engine | ChromaDB + sentence-transformers + Ollama (Llama 3) |

## Quick Start

### 1. Database Setup
```bash
mysql -u root -p < database/schema/init.sql
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate         # Windows
pip install -r requirements.txt

# Copy and configure environment
copy .env.example .env
# Edit .env with your MySQL credentials

# Train AI models (generates synthetic data first)
cd training
python synthetic_data_generator.py
python train_stress_model.py
cd ..

# Run Flask server
python run.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. RAG Setup (Optional - requires Ollama)
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3:8b

# Ingest knowledge base documents
# Add PDFs to backend/knowledge_base/guidelines/
# Then call: POST /api/rag/ingest  (via Admin Panel)
```

## Default Logins
| Role | Email | Password |
|---|---|---|
| Super Admin | admin@crpf.gov.in | Admin@123 |
| Welfare Officer | welfare@crpf.gov.in | Admin@123 |
| Commander | commander@crpf.gov.in | Admin@123 |
| Medical Officer | medical@crpf.gov.in | Admin@123 |

> **Note:** Update passwords immediately after first login in production.

## Key Features
- 🤖 AI-powered stress & burnout risk prediction (XGBoost + Random Forest)
- 🔍 SHAP explainability — understand *why* someone is at risk
- 🧠 RAG chatbot grounded in CRPF welfare policies
- 📊 Real-time dashboard with heatmaps and trend charts
- 🚨 Automated welfare alerts with escalation
- 🔐 AES-256 field encryption + RBAC for 5 roles
- 📋 PDF & Excel report generation
- 📱 Wellness self-assessment (opt-in, consent-based)

## Privacy Design
- Personnel PII (name, service number) encrypted with AES-256 in MySQL
- AI models use only anonymized IDs + numerical features — no names
- LLM (Ollama) runs locally — zero data leaves the organization
- Commanders see only aggregated unit data, never individual profiles
- All data access logged immutably in audit_logs table
