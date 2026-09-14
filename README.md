# Resume Intelligence Platform ☀️

Phase 1, Phase 2, Phase 3, Phase 4, and Phase 5 (Day 7: Project Alignment) of the Resume Intelligence Platform are complete! We have built the core ingestion + deterministic extraction layer, an entity normalization engine, an ATS-oriented resume quality analyzer, a Job Description intelligence parser, and a full deterministic Resume ↔ JD Matching engine covering skills, experience, skill-specific experience, role alignment, and project demonstration — all fully orchestrated with **258 passing unit and integration tests**.

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
████████████████████ 100% ✅
             │
             ▼
PHASE 3
Resume Quality & Analysis (P3D4)
████████████████████ 100% ✅
             │
             ▼
PHASE 4
Job Description Intelligence (P4D4)
████████████████████ 100% ✅
             │
             ▼
PHASE 5
Resume ↔ JD Matching (P5D7)
█████████████████░░░  78% 🔄 (Active)
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
* Section detection & extraction
* Name, Email, Phone parsers
* Education parser
* Experience parser
* Project parser
* Skills parser
* Service orchestration
* Real-resume fixture & integration tests with `pytest-asyncio`

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

## Phase 2: Resume Intelligence & Normalization ✅

Transforms raw extraction into canonical representations across all entities:
* **Skill Normalization:** e.g., `Python Programming` → `Python`, `React.js` → `React`
* **Role & Experience Normalization:** Job title canonicalization, company anchor resolution, start/end year bounds
* **Education Normalization:** Standardizes degrees (`B.Tech`, `Bachelor of Technology` → canonical degree representation) and institution names
* **Project Normalization:** Standardizes project metadata, link extraction, and description formatting
* **Pipeline Integration:** End-to-end normalization pipeline

```
RAW EXTRACTION → NORMALIZED RESUME
```

---

## Phase 3: Resume Quality & Analysis (P3D4) ✅

Actionable ATS-oriented evaluation and quality checks:
* **Completeness Analysis:** Evaluates required vs recommended profile fields and identifies missing contact or section data
* **Resume Quality Analysis:**
  * **Structure:** Missing structural elements across education, experience, projects, skills
  * **Content Quality:** Quantified metric detection (regex patterns for percentages, figures, multiples), bullet count, content length evaluation
  * **Consistency:** Timeline chronological validation (detects `start_year > end_year` invalid duration anomalies)
* **Formatting Risk Analysis:**
  * **Bullet Formatting:** Bullet marker consistency checks (`•`, `-`, `*`) across experience and project descriptions
  * **Header Formatting:** Section header detection and trailing colon usage consistency
* **Integrated Service Layer:** Unified API pipeline returning extraction, normalization, completeness score, quality checks, and formatting risks.

---

## Phase 4: Job Description Intelligence (P4D4) ✅

Structured parsing and intelligence extraction for Job Descriptions (JD):
* **JD Ingestion & API Layer:** Endpoint supporting raw text string inputs or multi-part file uploads (`.txt`/`.pdf`), enforcing single input validation.
* **Role & Experience Extraction:** Role title identification (e.g. `Role: Data Scientist`) and total YOE requirement extraction (`YOE_PATTERN` matching expressions like "minimum 5 years of experience").
* **Skill Extraction & Substring Overlap Resolution:** Regex skill extraction with longest-match overlap resolution (resolving `C++` vs `C`, `MySQL` vs `SQL`).
* **Noise Section Filtering:** Identifies and strips non-essential boilerplate sections ("About Us", "Perks & Benefits", "EEO Statement") while preserving core JD sections ("Requirements", "Qualifications", "Responsibilities").
* **Skill-Specific YOE Extraction:** Per-skill experience requirement extraction (e.g. `5+ years of Python experience`, `3 years of experience with React`).

**Phase 4 Output Schema:**
```json
{
  "role": "Data Scientist",
  "experience": 5,
  "skills": ["Python", "Machine Learning", "SQL"],
  "skill_specific_experience": [
    { "skill": "Python", "experience": 5 }
  ],
  "skill_requirements": [
    { "line": "Must have 5+ years of Python experience", "requirement": "required" }
  ]
}
```

> [!NOTE]
> **Phase 4 Limitation (`skill_requirements`):**
> * **Keyword-based classification:** `skill_requirements` currently relies on line-by-line keyword matching heuristics (`required`, `optional`, `unknown`) across filtered JD lines rather than deep contextual understanding.
> * **Future Improvement (Phase 6):** This will be improved in **Phase 6: ML / NLP Intelligence** via semantic relationship modeling and entity-bound contextual requirement extraction.

---

## Phase 5: Resume ↔ JD Matching 🔄

Dual-sided deterministic matching engine:
```
Resume (Structured + Normalized) ──┐
                                   ├─► MATCH ENGINE ─► Match Result (Skills, Role, Experience, Projects)
JD (Structured + Normalized) ──────┘
```

**Phase 5 Day-by-Day Progress:**
```
P5D1  Matching Foundations          ██████████ 100% ✅
P5D2  Experience Matching           ██████████ 100% ✅
P5D3  Skill-Experience Matching     ██████████ 100% ✅
P5D4  Result Composition            ██████████ 100% ✅
P5D5  Robustness & Integration      ██████████ 100% ✅
P5D6  Role Alignment                ██████████ 100% ✅
P5D7  Project Alignment             ██████████ 100% ✅
P5D8  Deterministic Match Scoring   ░░░░░░░░░░   0% ⏳ (Next)
P5D9  Final Integration & Hardening ░░░░░░░░░░   0%
```

**Engineering Work Covered:**
* **Skill Matching:** Categorizes JD skills into `matched`, `unmatched`, and `extra` (resume skills not required by JD).
* **Experience Matching:** Evaluates candidate total tenure against JD YOE requirement (`meets` / `underqualified`) and per-skill experience months against JD skill-specific requirements.
* **Role Alignment:** Strips seniority qualifiers (`Senior`, `Lead`, `Principal`) and maps candidate role history against the canonical target role (`match` / `mismatch` / `unknown`).
* **Project Alignment:** Scans project description bullet points for JD skill mentions (case-insensitive) to produce per-project `demonstrated` vs `not_demonstrated` skill evidence, preserving GitHub/live-demo metadata links.
* **Result Composition:** Aggregates all component match dictionaries into a single structured response.
* **Service & API Layer:** `POST /match` endpoint accepting resume PDF + JD (text string or file upload).

**Phase 5 Output Schema (P5D7):**
```json
{
  "skill_match": {
    "matched": ["Python", "FastAPI"],
    "unmatched": ["Docker"],
    "extra": ["SQL"]
  },
  "experience_match": {
    "required": 24,
    "candidate": 36,
    "difference": -12,
    "status": "meets"
  },
  "skill_experience_match": [
    { "skill": "Python", "required_experience_months": 24, "candidate_experience_months": 36, "difference_months": -12, "status": "meets" }
  ],
  "role_match": {
    "candidate_roles": ["Machine Learning Engineer"],
    "target_role": "ML Engineer",
    "canonical_candidate_roles": ["machine learning engineer"],
    "canonical_target_role": "machine learning engineer",
    "status": "match"
  },
  "project_match": [
    {
      "project": "ML API",
      "metadata": [{ "type": "github", "url": "https://github.com/example/ml-api" }],
      "demonstrated": ["Python", "FastAPI"],
      "not_demonstrated": ["Docker"]
    }
  ]
}
```

> [!NOTE]
> **P5D8 Next — Deterministic Match Scoring:** Aggregate all component signals into a normalized 0–100 composite score with configurable weights (skills, experience, role, projects) and a human-readable verdict (`Strong Match`, `Moderate Match`, `Underqualified`) plus per-dimension breakdown and flags.

---

## Phase 6: ML / NLP Intelligence ⏳

Introduces machine learning components beyond deterministic/rule-based logic:
* **Semantic Skill Matching:** e.g., `scikit-learn` ↔ `sklearn`
* **Semantic Requirement Relationships:** Advanced contextual classification and entity-bound relationship parsing to upgrade Phase 4 `skill_requirements` heuristics
* **Embedding-Based Similarity:** Vector matching between project descriptions and JD requirements
* **Classification Models:** Role classification, skill taxonomy, seniority classification
* **Semantic Compatibility:** Joint Resume + JD embedding layer

---

## Phase 7: Backend & Production Engineering ⏳

Transforming core intelligence into an enterprise platform:
```
API Gateway → FastAPI Backend → [Resume Service | JD Service | Match Service] → Data Layer
```
* Pydantic schemas, DB layer, auth, API versioning, error handling, logging, caching, background tasks, Docker & CI/CD.

---

## Phase 8: Deployment + MLOps ⏳

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
 │ Normalization (P2)   │ ✅
 └──────────┬───────────┘
            │
            ▼
 ┌──────────────────────┐
 │ Resume Analysis (P3) │ ✅ (Completeness, Quality, Formatting)
 └──────────┬───────────┘
            │
 ┌──────────┴───────────┐
 ▼                      ▼
Resume Intelligence   Job Intelligence (P4) ✅
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
Phase 1  ████████████████████ 100% ✅ (P1 Complete)
Phase 2  ████████████████████ 100% ✅ (P2 Complete)
Phase 3  ████████████████████ 100% ✅ (P3D4 Complete)
Phase 4  ████████████████████ 100% ✅ (P4D4 Complete)
Phase 5  █████████████████░░░  78% 🔄 (P5D7 Complete — P5D8 Next)
Phase 6  ░░░░░░░░░░░░░░░░░░░░   0%
Phase 7  ░░░░░░░░░░░░░░░░░░░░   0%
Phase 8  ░░░░░░░░░░░░░░░░░░░░   0%
```

**258 tests passing.** Our immediate next milestone is **P5D8: Deterministic Match Scoring** — building the composite 0–100 weighted scorer and verdict engine on top of the completed matching foundation.
