# Resume Intelligence Platform ☀️

Phase 1, Phase 2, and Phase 3 (Day 4: Resume Quality & Analysis) of the Resume Intelligence Platform are complete! We have built the core ingestion + deterministic extraction layer, an entity normalization engine, and an ATS-oriented resume quality and formatting analyzer, all fully orchestrated with 139 passing unit and integration tests.

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
Job Description Intelligence
░░░░░░░░░░░░░░░░░░░░   0% ⏳ (Next)
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
* PDF parsing ([pdf_parser.py](file:///d:/Projects/resume-intelligence-platform/src/parsers/pdf_parser.py))
* Text cleaning ([text_parser.py](file:///d:/Projects/resume-intelligence-platform/src/parsers/text_parser.py))
* Section detection & extraction
* Name, Email, Phone parsers ([name_parser.py](file:///d:/Projects/resume-intelligence-platform/src/parsers/name_parser.py), [email_parser.py](file:///d:/Projects/resume-intelligence-platform/src/parsers/email_parser.py), [phone_parser.py](file:///d:/Projects/resume-intelligence-platform/src/parsers/phone_parser.py))
* Education parser ([education_parser.py](file:///d:/Projects/resume-intelligence-platform/src/parsers/education_parser.py))
* Experience parser ([experience_parser.py](file:///d:/Projects/resume-intelligence-platform/src/parsers/experience_parser.py))
* Project parser ([project_parser.py](file:///d:/Projects/resume-intelligence-platform/src/parsers/project_parser.py))
* Skills parser ([skills_parser.py](file:///d:/Projects/resume-intelligence-platform/src/parsers/skills_parser.py))
* Service orchestration ([resume_service.py](file:///d:/Projects/resume-intelligence-platform/src/services/resume_service.py))
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

### Phase 2: Resume Intelligence & Normalization ✅

Transforms raw extraction into canonical representations across all entities:
* **Skill Normalization:** ([skill_normalizer.py](file:///d:/Projects/resume-intelligence-platform/src/normalizers/skill_normalizer.py)) e.g., `Python Programming` → `Python`, `React.js` → `React`
* **Role & Experience Normalization:** ([experience_normalizer.py](file:///d:/Projects/resume-intelligence-platform/src/normalizers/experience_normalizer.py)) Job title canonicalization, company anchor resolution, start/end year bounds
* **Education Normalization:** ([education_normalizer.py](file:///d:/Projects/resume-intelligence-platform/src/normalizers/education_normalizer.py)) Standardizes degrees (`B.Tech`, `Bachelor of Technology` → canonical degree representation) and institution names
* **Project Normalization:** ([project_normalizer.py](file:///d:/Projects/resume-intelligence-platform/src/normalizers/project_normalizer.py)) Standardizes project metadata, link extraction, and description formatting
* **Pipeline Integration:** ([resume_normalizer.py](file:///d:/Projects/resume-intelligence-platform/src/normalizers/resume_normalizer.py)) End-to-end normalization pipeline

```
RAW EXTRACTION → NORMALIZED RESUME
```

---

### Phase 3: Resume Quality & Analysis (P3D4) ✅

Actionable ATS-oriented evaluation and quality checks:
* **Completeness Analysis:** ([completeness_analyzer.py](file:///d:/Projects/resume-intelligence-platform/src/analyzers/completeness_analyzer.py)) Evaluates required vs recommended profile fields and identifies missing contact or section data
* **Resume Quality Analysis:** ([quality_analyzer.py](file:///d:/Projects/resume-intelligence-platform/src/analyzers/quality_analyzer.py))
  * **Structure:** Missing structural elements across education, experience, projects, skills
  * **Content Quality:** Quantified metric detection (regex patterns for percentages, figures, multiples), bullet count, content length evaluation
  * **Consistency:** Timeline chronological validation (detects `start_year > end_year` invalid duration anomalies)
* **Formatting Risk Analysis:** ([formatting_analyzer.py](file:///d:/Projects/resume-intelligence-platform/src/analyzers/formatting_analyzer.py))
  * **Bullet Formatting:** Bullet marker consistency checks (`•`, `-`, `*`) across experience and project descriptions
  * **Header Formatting:** Section header detection and trailing colon usage consistency
* **Integrated Service Layer:** ([resume_service.py](file:///d:/Projects/resume-intelligence-platform/src/services/resume_service.py)) Unified API pipeline returning extraction, normalization, completeness score, quality checks, and formatting risks.

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
Phase 2  ████████████████████ 100% ✅
Phase 3  ████████████████████ 100% ✅ (P3D4 Complete)
Phase 4  ░░░░░░░░░░░░░░░░░░░░   0% ⏳ Next Milestone
Phase 5  ░░░░░░░░░░░░░░░░░░░░   0%
Phase 6  ░░░░░░░░░░░░░░░░░░░░   0%
Phase 7  ░░░░░░░░░░░░░░░░░░░░   0%
Phase 8  ░░░░░░░░░░░░░░░░░░░░   0%
```

Our immediate next milestone is **Phase 4: Job Description Intelligence**.
