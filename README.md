# RevenueOS 🚀
### AI-Powered GTM Intelligence Platform

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-red?style=for-the-badge&logo=streamlit)](https://bit.ly/4f8G22J)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)](https://python.org)
[![HubSpot](https://img.shields.io/badge/HubSpot-CRM-orange?style=for-the-badge&logo=hubspot)](https://hubspot.com)
[![Slack](https://img.shields.io/badge/Slack-Alerts-purple?style=for-the-badge&logo=slack)](https://slack.com)

---

## What is RevenueOS?

RevenueOS is a full-stack GTM (Go-To-Market) intelligence platform that automates the daily workflow of a sales or revenue operations team. Instead of manually checking CRM, prioritizing leads, and writing outreach emails across 5 different tools — RevenueOS does it all in one AI-powered dashboard.

**Built to demonstrate real-world GTM engineering skills: CRM integration, AI automation, lead scoring, and real-time alerting.**

---

## The Problem It Solves

Every sales team faces the same bottleneck every morning:
- Open HubSpot → check which leads are active
- Identify which leads are going cold
- Write personalized outreach emails for each lead
- Notify the team about high-priority accounts
- Pull analytics to report pipeline health

**This takes 2-3 hours manually. RevenueOS does it in seconds.**

---

## Features

### 📊 Pipeline Dashboard
- Live lead metrics pulled from HubSpot CRM
- Total leads, Hot / Warm / Cold breakdown
- ICP Score distribution chart
- Leads by Industry visualization
- Real-time data — no manual refresh needed

### 🤖 AI Assistant
- Powered by Claude (Anthropic)
- Ask questions about your pipeline in natural language
- Get instant insights: "Which industry has the most hot leads?"
- Generates context-aware answers from your actual CRM data

### 👥 All Leads
- Full lead table with search and filter
- Filter by industry, status, ICP score
- Enriched company data per lead

### 📈 Analytics
- Conversion funnel analysis
- Source attribution (LinkedIn, referral, cold email, etc.)
- Hot leads by job title
- Trend analysis over time

### ⚠️ Decay Alerts
- Automatically flags leads that have gone inactive
- Classifies leads as: Critical / High Risk / Watch
- Visual decay status dashboard
- One-click Slack alert to notify the team

### 📋 GTM Brief
- AI-generated daily GTM summary
- Highlights top opportunities and risks
- Actionable recommendations for the sales team

### 🏢 Account Intel
- Deep company enrichment per account
- AI-generated outreach emails tailored to each lead
- ICP fit scoring with reasoning

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python, FastAPI |
| AI | Claude API (Anthropic) |
| CRM | HubSpot API |
| Alerts | Slack Webhooks |
| Email | Gmail SMTP |
| Data | Pandas, Plotly |
| Deployment | Streamlit Cloud |
| Version Control | GitHub |

---

## Architecture

```
HubSpot CRM
     ↓
load_data() → ICP Scoring → Decay Detection
     ↓               ↓              ↓
Dashboard      AI Assistant    Slack Alert
     ↓
Streamlit Cloud (Live)
```

---

## Integrations

- **HubSpot CRM** — Live contact sync via REST API
- **Claude AI** — Natural language pipeline analysis + email generation
- **Slack** — Automated decay alerts to `#all-revenueos` channel
- **Gmail** — Outreach email delivery via SMTP
- **FastAPI** — `/api/v1/leads` endpoint for external lead capture

---

## Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/Yashikaa07/revenueOS.git
cd revenueOS
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add secrets
Create `.streamlit/secrets.toml`:
```toml
HUBSPOT_API_KEY = "your-hubspot-private-app-token"
ANTHROPIC_API_KEY = "your-claude-api-key"
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/xxx/yyy/zzz"
GMAIL_USER = "your@gmail.com"
GMAIL_APP_PASSWORD = "your-app-password"
```

### 4. Run locally
```bash
streamlit run dashboard/streamlit_app.py
```

---

## Project Structure

```
revenueOS/
├── dashboard/
│   ├── streamlit_app.py      # Main app
│   └── leads_dataset.csv     # Fallback data
├── app/
│   └── modules/
│       ├── enrichment.py     # Company enrichment
│       ├── icp_scoring.py    # Lead scoring logic
│       ├── email_gen.py      # AI email generation
│       ├── chat_assistant.py # Claude AI assistant
│       ├── gmail_sender.py   # Email delivery
│       └── slack_alert.py    # Slack notifications
├── requirements.txt
└── README.md
```

---

## Live Demo

🔗 **[revenueos-fsnkmufxqfrcunkokyaree.streamlit.app](https://bit.ly/4f8G22J)**

---

## Built By

**Yashika Hemnani**
Marketing Analytics & Business Intelligence

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://linkedin.com/in/yashikahemnani)

---

## Use Cases

- **GTM Engineers** — Automate lead prioritization and outreach
- **Sales Managers** — Real-time pipeline visibility
- **Revenue Ops** — Decay detection and CRM hygiene
- **SDRs** — AI-generated personalized emails at scale
