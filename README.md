# 🎯 Industrial & Technical Job Role to Skill Set Mapping
### Deep Market Intelligence, Feature Engineering & Real-Time Streamlit Analytics Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive%20Charts-indigo.svg)](https://plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Executive Overview

This repository conducts a deep data analysis on **734 job postings** representing **71,234 open industrial and vocational vacancies** across manufacturing, automotive, retail, and supply chain sectors in India.

The primary objective addresses the fundamental employment question:
> **"Which job role needs which skill sets?"**

By developing a feature engineering pipeline and an interactive **Streamlit Realtime Dashboard**, this project maps high-dimensional job descriptions into standardized functional job families, extracts a 22-skill taxonomy across 5 technical domains, benchmarks compensation, and analyzes the career mobility pathways of entry-level workers.

---

## 🚀 Live Demo & Dashboard Overview

The repository includes an interactive multi-tab analytics application built with Streamlit and Plotly:

- **Interactive Role vs. Skill Matrix**: Normalized Heatmap showing the percentage affinity of skills across all job roles.
- **Role Capability Profiles & Radars**: In-depth drill-downs into each role's signature competencies and multidimensional radar footprints.
- **Compensation & The "Skill Premium"**: Box plots of stipend/salary distributions and diverging bar charts quantifying the monetary value of individual skills.
- **Talent Pipeline (100% Stacked Bar)**: Educational credentials (8th Pass to B.Tech) mapped against role allocations.
- **Geographic & Industry Ecosystem**: State-level hiring demand and sector treemaps.
- **Career & Skill Fit Matcher**: Real-time calculator where candidates select their credentials to calculate fit score, salary expectation, and missing skills to acquire.

---

## 🧩 The Core Answer: Which Job Role Needs Which Skill Sets?

| Standardized Job Role | Total Openings | Median Pay (₹/mo) | Primary Required Skill Sets (% Demand) |
| :--- | :---: | :---: | :--- |
| **Material Handling & Heavy Equipment** | 600 | ₹13,000 | **Forklift Operation / FLT (68.1%)**, Reach Truck / RT (24.8%), Articulated Forklift / AFLT (23.0%), BOPT & Pallet Truck (13.3%) |
| **CNC & Machine Operation** | 8,636 | ₹17,000 | **CNC Operation (30.4%)**, VMC Operation (7.1%), Machine Setup & Tooling (2.7%), Electrical Maintenance (2.7%) |
| **Quality Assurance & Inspection** | 11,736 | ₹15,400 | **Dimensional Measurement (Caliper/Micrometer) (21.2%)**, CNC & VMC Quality Verification (17.6%), Material Traceability & SOPs (7.1%) |
| **Warehouse, Logistics & Fulfillment** | 8,364 | ₹16,972 | **Loading & Unloading (46.6%)**, **Order Picking & Packing (43.1%)**, Preventive Maintenance (37.9%), 5S & Organization (32.8%) |
| **Welding, Fitting & Technical Trades** | 4,724 | ₹16,721 | **Preventive Maintenance (52.9%)**, Material Traceability (38.2%), **Welding - MIG/TIG/Arc (35.3%)**, Industrial Safety & PPE (11.8%) |
| **Sales, Retail & Commercial** | 782 | ₹11,250 | **Customer Service & Retail Sales (62.5%)**, Material Traceability & Documentation (12.5%) |
| **Engineering & Supervision** | 849 | ₹17,900 | **Electrical Maintenance & Wiring (22.2%)**, Blueprint Reading (11.1%), 5S (11.1%), PPE Compliance (11.1%) |
| **Industrial & Apprentice Trainee** | 18,222 | ₹17,000 | Injection Molding (4.3%), Electrical Maintenance (3.9%), Press & Stamping (1.9%) |
| **Assembly & Production Associate** | 10,941 | ₹14,500 | Line Operations, Injection Molding (3.1%), Fitting & Mechanical Assembly (1.6%) |

---

## 💎 The "Skill Premium" Benchmarking

Comparing median compensation of jobs *with* a skill versus *without* that skill reveals clear wage premiums:
- **Press & Stamping**: **+₹2,429/month (+14.5% premium)** over baseline.
- **Electrical Maintenance & Wiring**: **+₹2,150/month (+12.8% premium)**.
- **Fitting & Mechanical Assembly**: **+₹1,260/month (+7.5% premium)**.
- **PPE & Industrial Safety Compliance**: **+₹1,199/month (+7.2% premium)**.
- **Welding (MIG/TIG/Arc)**: **+₹723/month (+4.3% premium)**.

---

## 📊 Feature Engineering Pipeline

1. **Role Normalization**: Resolved 286 unstructured title variants into 10 clean functional categories via multi-field keyword heuristics.
2. **Skill Extraction Regex**: Built a structured 22-skill taxonomy across 5 functional domains (*Machining, Logistics, Metrology, Trades, and Safety*).
3. **Compensation Parsing**: Extracted clean monthly compensation from fragmented fields (`stipend`, `gross_pay`, `ctc`, and complex `stipend_tiers` strings like `Group 1: ₹16000`).
4. **Qualification Standardization**: Compressed 53 education strings into 6 standardized educational tiers (*Below 10th, 10th, 12th, ITI, Diploma, Graduate/B.Tech*).
5. **Vacancy Imputation**: Cleaned non-numeric and zero-vacancy entries.

---

## 🛠️ Project Structure

```bash
job-role-skill-mapping/
├── app.py                   # Streamlit interactive real-time dashboard
├── data_pipeline.py         # Feature engineering & skill extraction engine
├── deep_analysis.py         # Analytical insights & skill premium computation
├── job-list.csv             # Raw source dataset (734 jobs)
├── processed_jobs.csv       # Cleaned & feature-engineered dataset
├── skill_taxonomy.json      # Structured skill categories and keyword mappings
├── deep_insights.json       # Generated analytical metrics
├── requirements.txt         # Project dependencies
├── .streamlit/
│   └── config.toml          # Streamlit theme and server configuration
└── README.md                # Project documentation
```

---

## 💻 Local Installation & Setup

```bash
# 1. Clone repository
git clone https://github.com/iamazadak/job-role-skill-mapping.git
cd job-role-skill-mapping

# 2. Create virtual environment & activate
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Streamlit Dashboard
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

---

## ☁️ Deploy to Streamlit Community Cloud (Free & 1-Click)

1. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
2. Click **"New app"**.
3. Select this repository: `iamazadak/job-role-skill-mapping`.
4. Set Branch: `main`.
5. Set Main file path: `app.py`.
6. Click **"Deploy!"** — your dashboard will be live on a public URL!
