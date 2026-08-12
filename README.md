# Resume Intelligence Platform ☀️

Phase 1 of the Resume Intelligence Platform is complete! We have built the core resume ingestion + deterministic extraction layer, including section parsers, generic text utilities, and service orchestration with comprehensive testing.

The 8-phase roadmap below outlines the architectural evolution from structured extraction to a production MLOps deployment.

---

## 🧭 Resume Intelligence Platform: Full Roadmap

```
PHASE 1
Resume Ingestion & Structured Extraction
████████████████████ 100% ✅
             │
             ▼
PHASE 2
Resume Intelligence & Normalization
░░░░░░░░░░░░░░░░░░░░   0%
             │
             ▼
PHASE 3
Resume Quality & Analysis
░░░░░░░░░░░░░░░░░░░░   0%
             │
             ▼
PHASE 4
Job Description Intelligence
░░░░░░░░░░░░░░░░░░░░   0%
             │
             ▼
PHASE 5
Resume ↔ JD Matching
░░░░░░░░░░░░░░░░░░░░   0%
             │
             ▼
PHASE 6
ML / NLP Intelligence Layer
░░░░░░░░░░░░░░░░░░░░   0%
             │
             ▼
PHASE 7
Backend + Production Engineering
░░░░░░░░░░░░░░░░░░░░   0%
             │
             ▼
PHASE 8
Deployment, Evaluation & MLOps
░░░░░░░░░░░░░░░░░░░░   0%
```

---

## Phase Breakdown

### Phase 1: Resume Ingestion & Extraction ✅

**Input Pipeline:**
```
PDF / Resume → PDF Extraction → Text Cleaning → Deterministic Extraction
```

**Extracted Entities:**
* **Personal:** Name, Email, Phone
* **Sections:** Education, Experience, Projects, Skills

**Engineering Work Covered:**
* PDF parsing
* Text cleaning
* Section detection
* Keyword/config separation
* Generic `text_utils`
* Education parser
* Experience parser
* Project parser
* Skills parser
* Service orchestration
* Unit tests & regression tests
* Real-resume fixture & async integration test with `pytest-asyncio`
* Git workflow & PyPI package setup

**Phase 1 Output Schema:**
```json
{
  "name": "...",
  "email": "...",
  "phone": "...",
  "education": [],
  "experience": [],
  "projects": [],
  "skills": []
}
```

---

### Phase 2: Resume Intelligence & Normalization ⏳

Transforms raw extraction into canonical representations:
* **Skill Normalization:** e.g., `Python Programming` → `Python`, `React.js` → `React`
* **Role Normalization:** Standardized job categories (e.g., `ML Engineer`, `Machine Learning Engineer` → canonical role)
* **Company Normalization:** Anchor & keyword resolution
* **Education Normalization:** `B.Tech`, `Bachelor of Technology` → canonical degree representation
* **Duration Normalization:** Dates & ranges to common representation

```
RAW EXTRACTION → NORMALIZED RESUME
```

---

### Phase 3: Resume Quality & Analysis ⏳

Actionable ATS-oriented evaluation:
* **Completeness:** Section checks (missing email/LinkedIn, skills, project presence)
* **Resume Quality:** Weak project descriptions, excessive length, missing metrics, duplicate skills
* **ATS-Oriented Analysis:**
  * Section completeness
  * Keyword coverage
  * Formatting risks
  * Skill & experience quality

---

### Phase 4: Job Description Intelligence ⏳

Structured parsing of Job Descriptions (JD):
* **Extract:** Required skills, Preferred skills, Role, Experience level, Education requirements, Responsibilities, Tools & domain expertise

---

### Phase 5: Resume ↔ JD Matching ⏳

Dual-sided matching engine:
```
Resume (Structured + Normalized) ──┐
                                   ├─► MATCH ENGINE ─► Match Score (Skills, Role, Experience, Projects)
JD (Structured + Normalized) ──────┘
```
Provides breakdown of strong matching skills vs missing requirements.

---

### Phase 6: ML / NLP Intelligence ⏳

Introduces machine learning components beyond deterministic/rule-based logic:
* **Semantic Skill Matching:** e.g., `scikit-learn` ↔ `sklearn`
* **Embedding-Based Similarity:** Vector matching between project descriptions and JD requirements
* **Classification Models:** Role classification, skill taxonomy, seniority classification
* **Semantic Compatibility:** Joint Resume + JD embedding layer

---

### Phase 7: Backend & Production Engineering ⏳

Transforming core intelligence into an enterprise platform:
```
API Gateway → FastAPI Backend → [Resume Service | JD Service | Match Service] → Data Layer
```
* Pydantic schemas, DB layer, auth, API versioning, error handling, logging, caching, background tasks, Docker & CI/CD.

---

### Phase 8: Deployment + MLOps ⏳

Production lifecycle & continuous evaluation:
* Git → CI → Tests → Docker Build → Cloud Deployment (AWS/GCP) → Monitoring & Model Evaluation
* Model registry (MLflow), experiment tracking, data versioning, continuous evaluation pipelines.

---

## 🧠 Overall Architecture

```
RESUME INTELLIGENCE PLATFORM
             │
             ▼
      ┌─────────────┐
      │ PDF / DOC   │
      └──────┬──────┘
             │
             ▼
   ┌──────────────────┐
   │ Ingestion        │
   │ + Text Cleaning  │
   └────────┬─────────┘
            │
            ▼
 ┌──────────────────────┐
 │ Structured Extraction│
 └──────────┬───────────┘
            │
            ▼
 ┌──────────────────────┐
 │ Normalization        │
 └──────────┬───────────┘
            │
            ▼
 ┌──────────────────────┐
 │ Resume Analysis      │
 └──────────┬───────────┘
            │
 ┌──────────┴───────────┐
 ▼                      ▼
Resume Intelligence   Job Intelligence
 │                      │
 └──────────┬───────────┘
            ▼
  ┌─────────────────┐
  │ Matching Engine │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ ML/NLP Layer    │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ FastAPI Backend │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Docker + Cloud  │
  │ + MLOps         │
  └────────┬────────┘
```

---

## Current Status

```
Phase 1  ████████████████████ 100% ✅
Phase 2  ░░░░░░░░░░░░░░░░░░░░   0%
Phase 3  ░░░░░░░░░░░░░░░░░░░░   0%
Phase 4  ░░░░░░░░░░░░░░░░░░░░   0%
Phase 5  ░░░░░░░░░░░░░░░░░░░░   0%
Phase 6  ░░░░░░░░░░░░░░░░░░░░   0%
Phase 7  ░░░░░░░░░░░░░░░░░░░░   0%
Phase 8  ░░░░░░░░░░░░░░░░░░░░   0%
```

Our immediate next milestone is **Phase 2: Normalization**.
