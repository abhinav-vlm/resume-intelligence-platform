# Phase 4.5 Hardening & Generalization — 7-Day Sprint Plan (Days 5–11)

**Sprint Window:** Next 7 Working Days (Continuing from Phase 4.5 Day 5 through Day 11)  
**Daily Time Budget:** **Max 2 Hours Total per Day** (All 5 daily blocks combined = 120 minutes)  
**Block Allocation:** Up to 5 focused blocks per day (10–35 mins each, totaling 120 mins)  
**Baseline Test Count:** **368 passed, 0 failed**  
**Core Strategy:** **Major Issues First (P0 & Critical P1 Blockers)** to rapidly unlock **Phase 5 (Resume ↔ JD Matching)**. Minor issues (P2–P4 cosmetics, secondary aliases, schema enhancements) are cataloged and deferred to be fixed in parallel during **Phase 6 (ML/NLP Intelligence)**.

---

## 7-Day Sprint Master Schedule (2 Hours Total / Day)

| Day | Daily Focus (Max 2h Total) | Major Issues Targeted (P0 / Critical P1) | Outcome & Deliverable |
|---|---|---|---|
| **Phase 4.5 Day 5** | Resume P0 Boundaries & Date/Experience Normalization | R-023, R-024, R-025, R-035, R-009, R-006, R-030, R-031, R-005 | Zero P0 structural defects; active employment tenure resolved; green test baseline |
| **Phase 4.5 Day 6** | Resume Multi-Page Continuity & Entity Splitting | R-034, R-038, R-022, R-007, R-026, R-036 | Multi-page resume preservation verified; skill conjunctions & combined degrees split; resume pipeline locked |
| **Phase 4.5 Day 7** | JD Preprocessing & Skill Vocabulary Overhaul (JD-001) | JD-013, JD-001 | Text cleaning wired into JD service; 17-skill bottleneck replaced with scalable tech taxonomy |
| **Phase 4.5 Day 8** | JD Section Detection & Requirement Context (Required vs Optional) | JD-018, JD-004, JD-006, JD-008, JD-009, JD-015 | Structured JD section detector; context-inherited skill classification (`required` vs `optional`); robust noise filter |
| **Phase 4.5 Day 9** | JD Role & Experience Extraction Generalization | JD-002, JD-016, JD-017, JD-003, JD-005 | Role extraction handles unlabelled top-lines & `Title:`; YOE handles prefix labels & domain qualifiers |
| **Phase 4.5 Day 10** | JD Education Requirements, Noise Reduction & Schema Lockdown | JD-014, JD-012 | Education requirements in schema; line-level noise eliminated; unified schema aligned with resume pipeline |
| **Phase 4.5 Day 11** | Cross-Pipeline Regression & Phase 5 Matching Sign-Off | Full Resume Corpus (R01–R12) + Full JD Corpus (JD01–JD10 + Real JDs) | Zero P0/P1 defects; vocabulary & scale alignment verified; Phase 5 Matching kickoff approved |

---

## Standard 2-Hour Daily Block Distribution

Each day's 120-minute window is divided into up to 5 focused blocks:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 DAILY 2-HOUR SESSION (120 MIN)                          │
├───────────────┬──────────────────┬──────────────────┬─────────────────┬────────────────┤
│ Block 1 (15m) │  Block 2 (30m)   │  Block 3 (30m)   │  Block 4 (25m)  │ Block 5 (20m)  │
│ Standup &     │  High-Priority   │  Core Production │  Integration &  │ Checkpoint &   │
│ Root-Cause    │  Test & Fix A    │  Test & Fix B    │  Regression Run │ Doc Sync       │
└───────────────┴──────────────────┴──────────────────┴─────────────────┴────────────────┘
```

---

## Phase 4.5 Day 5: Resume Structural Hardening & Critical Boundaries (2h Total)

### Phase 4.5 Day 5 Block 1: Issue Audit & Baseline Lockdown (20 min) ✅ (COMPLETED)
- **Status:** **COMPLETE**
- **Accomplishments:**
  - Audited all 42 resume issues and 18 JD issues against active codebase.
  - Verified R-002 is FIXED in source code via [`extract_linkedin()`](file:///d:/Projects/resume-intelligence-platform/src/utils/resume_metadata_utils.py) and wired into [`resume_service.py`](file:///d:/Projects/resume-intelligence-platform/src/services/resume_service.py).
  - Verified R-037 is PARTIALLY FIXED in source code via `WORK HISTORY`, `ACADEMIC QUALIFICATIONS`, `AREAS OF EXPERTISE` in [`header_configs.py`](file:///d:/Projects/resume-intelligence-platform/src/configs/header_configs.py).
  - Consolidated R-041 and R-042 into [`issues_jd.md`](file:///d:/Projects/resume-intelligence-platform/issues_jd.md) as JD-002 and JD-017.
  - Added JD-018 (JD section detector architecture gap) to [`issues_jd.md`](file:///d:/Projects/resume-intelligence-platform/issues_jd.md).
  - Migrated all test contracts and execution roadmaps from `issue.md` into Section 5 of [`issues_resume.md`](file:///d:/Projects/resume-intelligence-platform/issues_resume.md).
  - Deleted obsolete `issue.md` and updated [`fixed.md`](file:///d:/Projects/resume-intelligence-platform/fixed.md).
- **Checkpoint:** Baseline locked at **368 passing tests**, documentation ledger 100% synchronized.

---

### Phase 4.5 Day 5 Block 2: Fix P0 Project Boundaries & Headers (30 min)
- **Target Issues:** R-023, R-024, R-035, R-009 (residual)
- **Scope & Actions:**
  1. **R-023:** Add `is_duration(line)` guard to `_is_project_title()` in `src/utils/text_utils.py` so standalone project duration lines (`Jun 2022 - Jul 2022`) are never treated as project titles.
  2. **R-024:** Add `"TECHNOLOGIES"` to `SECTION_HEADERS` and map `"technologies": "skills"` in `SECTION_ALIASES` in `src/configs/header_configs.py` to stop boundary bleed into projects.
  3. **R-035:** Support Unicode bullet glyphs (`\u2022`, `\u2023`, `\u25cf`, etc.) in `src/parsers/project_parser.py` so non-standard bullet lines do not mutate the project title into an empty string.
  4. **R-009 (Residual):** Filter out single-token uppercase tech keywords (`CSS`, `HTML`, `SQL`) from `_is_project_title()` when appearing as continuation lines.
- **Verification:** Focused unit tests in `tests/parsers/test_project_parser.py` and `tests/parsers/test_section_detector.py`.

---

### Phase 4.5 Day 5 Block 3: Fix P0/P1 Experience Parsing Collision (30 min)
- **Target Issues:** R-025, R-005
- **Scope & Actions:**
  1. **R-025:** Re-order condition checks in `src/parsers/experience_parser.py` so that bullet prefixes (`•`, `-`, `*`) are evaluated **before** `ROLE_KEYWORDS` matching, preventing bullet lines from being stolen as job titles.
  2. **R-005:** Defend against `block[i-1]` company assumption in `src/parsers/experience_parser.py`. If `block[i-1]` contains role keywords, commas, or location indicators, split composite company/role strings or inspect layout context.
- **Verification:** Unit tests in `tests/parsers/test_experience_parser.py` asserting role bullets are preserved in descriptions.

---

### Phase 4.5 Day 5 Block 4: Tenure & Date Normalization ("Present" / Abbreviations) (25 min)
- **Target Issues:** R-006, R-030, R-031
- **Scope & Actions:**
  1. **R-006 & R-030:** Update `DURATION_PATTERNS` in `src/configs/text_utils_configs.py` to match `Month YYYY - Present` and `Month YYYY - Current`. In `src/normalizers/experience_normalizer.py`, map `"Present"` / `"Current"` to the current calendar date (`datetime.now()`) so active employment produces accurate months.
  2. **R-031:** Expand month regex in `experience_normalizer.py` to recognize 3-letter and abbreviated months (`Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`, `Sept`, `Oct`, `Nov`, `Dec`).
- **Verification:** Assert currently-employed candidates receive non-zero months experience in `test_experience_normalizer.py`.

---

### Phase 4.5 Day 5 Block 5: Service Test Contracts & Daily Checkpoint (15 min)
- **Target Issues:** Integration contract tests + daily baseline update
- **Scope & Actions:**
  1. Execute the 3 Block 2 test contracts migrated from `issue.md`:
     - `test_process_resume_passes_blocks_and_links_to_projects`
     - `test_process_resume_handles_blank_pdf_without_crashing`
     - `test_process_resume_propagates_pdf_extraction_error`
  2. Run full test suite across workspace (`python -m pytest -p no:cacheprovider tests`).
  3. Update `fixed.md` with new passing test baseline count.
- **Checkpoint Target:** **372+ passing tests**, 0 regressions.

---

## Phase 4.5 Day 6: Resume Multi-Page Continuity & Entity Parsing (2h Total)

### Phase 4.5 Day 6 Block 1: Multi-Page Experience & Education Continuity (25 min)
- **Target Issues:** R-034, R-038
- **Scope & Actions:**
  1. **R-034 Empirical Verification:** Validate `R04_MultiPage_Executive.pdf` against `resume_service.py` to confirm whether multi-page experience entries (`Stripe`, `Goldman Sachs`, `Bloomberg LP`) are preserved or dropped. If dropped, verify section detection header recognition across page breaks.
  2. **R-038 Empirical Verification:** Confirm multi-page education extraction so that section joining in `resume_service.py` prevents premature termination.
- **Verification:** Integration test with multi-page fixture asserting all job entries survive.

---

### Phase 4.5 Day 6 Block 2: Skill Conjunctions & Project Title Normalization (25 min)
- **Target Issues:** R-022, R-007
- **Scope & Actions:**
  1. **R-022:** In `src/parsers/skills_parser.py`, split candidate strings on `" and "` in addition to `[,|/]`, ensuring conjunction-joined skills (e.g. `HTML, CSS and React JS`) are tokenized into distinct candidates.
  2. **R-007:** In `src/parsers/project_parser.py` (and `normalize_projects`), strip display suffixes such as `| GitHub`, `| LIVE`, `| Demo`, `- GitHub` from extracted project titles.
- **Verification:** Tests asserting `React JS` extracted as distinct skill and clean project titles without pipe suffixes.

---

### Phase 4.5 Day 6 Block 3: Education Composite Line Splitting & Doctoral Degrees (25 min)
- **Target Issues:** R-026, R-036
- **Scope & Actions:**
  1. **R-026:** In `src/parsers/education_parser.py`, handle composite single lines containing both institution and degree (e.g. `B.Tech in Computer Science, IIT Bombay`) by splitting into distinct degree and institution fields.
  2. **R-036:** Add doctoral degrees (`PHD`, `PH.D`, `DOCTOR`, `DOCTORATE`) to `DEGREE_KEYWORDS` and map to `"Ph.D."` in `DEGREE_ALIASES`.
- **Verification:** Test composite education line parsing; test Ph.D. detection on `R03_Senior_Staff_ML.pdf`.

---

### Phase 4.5 Day 6 Block 4: Full 12-Resume Corpus Verification (30 min)
- **Target Issues:** Full Resume Regression (R01 through R12, Harshit, Aditya, Abhinav)
- **Scope & Actions:**
  1. Run end-to-end extraction against all 12 resume fixtures in `tests/fixtures/`.
  2. Assert:
     - 0 P0/P1 defects remaining.
     - Accurate LinkedIn, email, phone, skills, experience, education, projects.
     - Zero unhandled exceptions or crashes.
- **Verification:** Zero P0/P1 failures across the entire resume test corpus.

---

### Phase 4.5 Day 6 Block 5: Daily Checkpoint & Deferral Catalog (15 min)
- **Target Issues:** Documentation & Phase 6 deferral lockdown
- **Scope & Actions:**
  1. Update `issues_resume.md` and `fixed.md` status matrices.
  2. Formally catalog minor non-blocking issues (R-003, R-011, R-012, R-014, R-015, R-016, R-017, R-018, R-019, R-020, R-021, R-027, R-028, R-029, R-032, R-033, R-039, R-040) for parallel execution during Phase 6.
  3. Resume pipeline is officially locked and ready for Phase 5 matching.
- **Checkpoint Target:** Full test suite green, resume pipeline finalized for matching.

---

## Phase 4.5 Day 7: JD Preprocessing & Skill Vocabulary Overhaul (2h Total)

### Phase 4.5 Day 7 Block 1: JD Ingestion Preprocessing (JD-013) (20 min)
- **Target Issues:** JD-013
- **Scope & Actions:**
  1. Wire `clean_text()` into `src/services/jd_service.py` and `parse_jd()` before section filtering and extraction.
  2. Eliminate Unicode noise, irregular line-breaks, and non-ASCII character glitches.
- **Verification:** Unit tests verifying `clean_text` execution on raw text and PDF inputs for JD pipeline.

---

### Phase 4.5 Day 7 Block 2: Scalable Skill Vocabulary Redesign (JD-001 Architecture) (35 min)
- **Target Issues:** JD-001 (Architecture)
- **Scope & Actions:**
  1. Replace the closed 17-skill `KNOWN_SKILLS` set with a comprehensive tech taxonomy in `src/configs/skill_configs.py` covering:
     - Machine Learning / AI: `TensorFlow`, `PyTorch`, `Scikit-learn`, `Pandas`, `NumPy`, `Keras`, `MLflow`, `Hugging Face`, `NLP`, `Computer Vision`.
     - Databases & Caching: `PostgreSQL`, `MongoDB`, `Redis`, `Cassandra`, `Elasticsearch`, `DynamoDB`.
     - DevOps & Cloud: `Azure`, `GCP`, `Terraform`, `Jenkins`, `CI/CD`, `Bash`, `Ansible`.
     - Backend & Systems: `Go`, `Rust`, `Ruby`, `Kafka`, `Spark`, `GraphQL`, `REST`, `Spring Boot`, `.NET`.
- **Verification:** Assert lookup dictionary matches modern tech stack tokens.

---

### Phase 4.5 Day 7 Block 3: Dynamic JD Skill Extractor Engine (30 min)
- **Target Issues:** JD-001 (Extraction Engine)
- **Scope & Actions:**
  1. Upgrade `_extract_skills()` in `src/parsers/jd_parser.py` to extract skills from both taxonomy pattern matching and candidate phrase extraction (similar to resume `skills_parser.py`).
  2. Ensure extraction captures both known and candidate unknown skills rather than silently discarding unlisted technologies.
- **Verification:** JD9 (Data Science test) extracts all 8 skills (`TensorFlow`, `PyTorch`, `Scikit-learn`, `Pandas`, `NumPy`, `Jupyter`, `Python`, `SQL`).

---

### Phase 4.5 Day 7 Block 4: Real-World JD Skill Verification (25 min)
- **Target Issues:** JD-001 Validation on Real JDs
- **Scope & Actions:**
  1. Validate skill extraction on real fixtures: `jd_ml_engineer_test.pdf`, Meta ML JD, Databricks SE JD, DeepMind Research Engineer JD, Stripe Backend JD.
  2. Confirm extraction rate exceeds 90% across real JD fixtures.
- **Verification:** Real PDF fixture skill extraction asserts pass.

---

### Phase 4.5 Day 7 Block 5: Daily Checkpoint & Test Baseline Update (10 min)
- **Target Issues:** Regression checkpoint
- **Scope & Actions:**
  1. Run full workspace test suite (`python -m pytest -p no:cacheprovider tests`).
  2. Update `fixed.md` with JD-001 resolution.
- **Checkpoint Target:** Full test suite green, JD-001 marked RESOLVED.

---

## Phase 4.5 Day 8: JD Section Detection & Requirement Context (2h Total)

### Phase 4.5 Day 8 Block 1: Structured JD Section Detector (JD-018) (30 min)
- **Target Issues:** JD-018
- **Scope & Actions:**
  1. Implement structured section detection for JDs (`detect_jd_sections()` in `src/parsers/jd_parser.py`).
  2. Segment JDs into canonical section objects:
     - `ROLE_OVERVIEW` / `ABOUT_THE_ROLE`
     - `REQUIREMENTS` / `BASIC_QUALIFICATIONS` / `MINIMUM_QUALIFICATIONS`
     - `PREFERRED_QUALIFICATIONS` / `BONUS` / `DESIRED`
     - `RESPONSIBILITIES` / `WHAT_YOU_WILL_DO`
     - `BENEFITS` / `PERKS`
     - `COMPANY_INFO` / `ABOUT_US` (Noise)
     - `EQUAL_OPPORTUNITY` (Noise)
- **Verification:** Unit tests asserting section boundary segmentation on multi-section JDs.

---

### Phase 4.5 Day 8 Block 2: Re-entrant & Robust Noise Filtering (25 min)
- **Target Issues:** JD-006, JD-009, JD-015
- **Scope & Actions:**
  1. Upgrade noise header matching from exact lowercase string equality to prefix/keyword matching (`"About Us - Our Story"` recognized as noise).
  2. Make noise filtering re-entrant: entering a noise section does not permanently drop subsequent valid sections.
- **Verification:** Test decorated noise headers and multi-noise section JDs.

---

### Phase 4.5 Day 8 Block 3: Context-Inherited Requirement Classification (JD-004, JD-008) (35 min)
- **Target Issues:** JD-004, JD-008
- **Scope & Actions:**
  1. **JD-004:** Refactor `_classify_skill_requirement()` to inherit context from the enclosing parent section (skills under `Requirements` default to `"required"`; skills under `Preferred Qualifications` default to `"optional"`).
  2. **JD-008:** Unify skills and requirement levels into a single structured output list:
     ```json
     [
       {"skill": "Python", "requirement": "required"},
       {"skill": "AWS", "requirement": "optional"}
     ]
     ```
- **Verification:** Assert items under `Required:` are never classified `unknown`.

---

### Phase 4.5 Day 8 Block 4: Multi-Section Requirement Tests (20 min)
- **Target Issues:** Unit verification
- **Scope & Actions:**
  1. Author unit tests asserting section-inherited requirement levels.
  2. Test mixed JDs containing both required and optional skill blocks.
- **Verification:** 100% pass on requirement classification tests.

---

### Phase 4.5 Day 8 Block 5: Daily Checkpoint & Regression Suite (10 min)
- **Target Issues:** Regression check
- **Scope & Actions:**
  1. Run full test suite across workspace.
  2. Update `fixed.md` with JD-004, JD-006, JD-008, JD-009, JD-018 resolutions.
- **Checkpoint Target:** Full test suite green.

---

## Phase 4.5 Day 9: JD Role & Experience Extraction Generalization (2h Total)

### Phase 4.5 Day 9 Block 1: Role Extraction Generalization (JD-002, R-041) (30 min)
- **Target Issues:** JD-002, R-041 (consolidated)
- **Scope & Actions:**
  1. In `src/configs/jd_configs.py`: Add `"title"`, `"opening"`, `"vacancy"`, `"we are hiring"` to `ROLE_KEYWORDS`.
  2. In `src/parsers/jd_parser.py`: Implement fallback heuristic in `_extract_role()` to inspect the first non-empty substantive line before the first section header if no labeled prefix exists.
  3. Validate on Meta, DeepMind, Databricks, Siemens, and Uber test inputs.
- **Verification:** Assert role extraction success on unlabeled first lines and `Title:` labels.

---

### Phase 4.5 Day 9 Block 2: Experience Regex Overhaul (JD-016, JD-017, R-042) (35 min)
- **Target Issues:** JD-016, JD-017, R-042 (consolidated)
- **Scope & Actions:**
  1. **JD-016:** Add prefix label matching to `YOE_PATTERN` (e.g. `Experience:\s*\d+\+?\s*years`).
  2. **JD-017:** Loosen negative lookahead in `YOE_PATTERN`: permit domain modifiers (`software engineering`, `applied machine learning`, `relevant`, `related`) and allow trailing `in <domain>` or `with <domain>` clauses.
  3. Validate on `jd_ml_engineer_test.pdf` (`Experience: 3+ years` -> 36 months) and Meta JD (`4+ years in applied ML` -> 48 months).
- **Verification:** Real JD overall experience extraction success rate improves to >90%.

---

### Phase 4.5 Day 9 Block 3: Skill-Specific Experience & Ranges (JD-003, JD-005) (25 min)
- **Target Issues:** JD-003, JD-005
- **Scope & Actions:**
  1. **JD-003:** Expand `SKILL_YOE_PATTERN` to match `N+ years of experience in <skill>` and `<skill>: N+ years`.
  2. **JD-005:** Handle range formats (`4-6 years`) by extracting minimum (`48` months) rather than arbitrarily picking the max.
- **Verification:** Unit tests asserting skill-specific duration extraction.

---

### Phase 4.5 Day 9 Block 4: Real JD Extraction Check (20 min)
- **Target Issues:** End-to-end verification
- **Scope & Actions:**
  1. Verify role, overall experience, and skill-specific experience across all 9 real JDs.
- **Verification:** Real JDs pass role and experience extraction cleanly.

---

### Phase 4.5 Day 9 Block 5: Daily Checkpoint & Documentation Sync (10 min)
- **Target Issues:** Daily sync
- **Scope & Actions:**
  1. Run full test suite.
  2. Update `fixed.md` and `issues_jd.md`.
- **Checkpoint Target:** Full test suite green.

---

## Phase 4.5 Day 10: JD Schema Completion & Downstream Integration (2h Total)

### Phase 4.5 Day 10 Block 1: Education Requirements Extraction (JD-014) (30 min)
- **Target Issues:** JD-014
- **Scope & Actions:**
  1. Add education requirement extraction to `src/parsers/jd_parser.py` (degree levels: `Bachelors`, `Masters`, `Ph.D.`; fields: `Computer Science`, `Data Science`, etc.).
  2. Add `"education_requirements"` to JD output schema.
- **Verification:** Unit tests asserting degree requirements extracted from qualifications sections.

---

### Phase 4.5 Day 10 Block 2: Requirement Noise Reduction (JD-012) (25 min)
- **Target Issues:** JD-012
- **Scope & Actions:**
  1. Restrict requirement classification strictly to extracted skill candidates and bullet points, avoiding classifying generic boilerplate lines.
- **Verification:** Output dictionary contains clean requirements without noise lines.

---

### Phase 4.5 Day 10 Block 3: Unified JD Output Schema & Contract Lockdown (35 min)
- **Target Issues:** JD output schema standardization
- **Scope & Actions:**
  1. Standardize `parse_jd()` and `jd_service.py` output contract to mirror `resume_service.py`.
  2. Output dictionary: `role`, `experience_months`, `skills` (with requirement tags), `education_requirements`, `sections`, `metadata`.
- **Verification:** Integration contract test asserting all schema fields in `tests/services/test_jd_service.py`.

---

### Phase 4.5 Day 10 Block 4: JD Service Boundary & Error Tests (20 min)
- **Target Issues:** Service robustness
- **Scope & Actions:**
  1. Author service tests for blank JDs, single-line JDs, and PDF file exceptions.
- **Verification:** 100% pass on `test_jd_service.py`.

---

### Phase 4.5 Day 10 Block 5: Daily Checkpoint & Baseline Lockdown (10 min)
- **Target Issues:** Regression check
- **Scope & Actions:**
  1. Run full test suite.
  2. Update `fixed.md` and `issues_jd.md`.
- **Checkpoint Target:** Full test suite green, JD pipeline ready for matching.

---

## Phase 4.5 Day 11: End-to-End Regression & Phase 5 Readiness Sign-Off (2h Total)

### Phase 4.5 Day 11 Block 1: Full Resume Corpus Regression (30 min)
- **Target Issues:** All Resume Issues Verification (R-001 through R-040)
- **Scope & Actions:**
  1. Run complete 12-fixture resume test suite (`R01_Fresher_CS.pdf` through `R12_No_Experience_BioMed.pdf`, `HARSHIT_WEBDEV.pdf`, `resume_without_experience.pdf`, `Resume - Aditya Saha.pdf`, `Abhinav_ML_Resume.pdf`).
  2. Assert 0 P0 defects, 0 crashes, accurate extraction across all fields.
- **Verification:** 100% pass across resume fixtures.

---

### Phase 4.5 Day 11 Block 2: Full JD Corpus Regression (30 min)
- **Target Issues:** All JD Issues Verification (JD-001 through JD-018)
- **Scope & Actions:**
  1. Run complete JD test suite (10 synthetic JDs + `jd_ml_engineer_test.pdf` + 9 real production JDs).
  2. Assert role detection >95%, experience extraction >90%, required vs optional skills cleanly categorized.
- **Verification:** 100% pass across JD fixtures.

---

### Phase 4.5 Day 11 Block 3: Cross-Pipeline Vocabulary & Scale Alignment (25 min)
- **Target Issues:** Prerequisite for Phase 5 Matching Engine
- **Scope & Actions:**
  1. Confirm skill normalization resolves to canonical names across both pipelines (`React.js` -> `React`).
  2. Confirm experience duration scales match (`experience_months` as integer).
- **Verification:** Alignment assertions pass in cross-pipeline integration test.

---

### Phase 4.5 Day 11 Block 4: Deferral Catalog Finalization (20 min)
- **Target Issues:** Documentation closure
- **Scope & Actions:**
  1. Finalize list of minor issues deferred to Phase 6 in [`issues_resume.md`](file:///d:/Projects/resume-intelligence-platform/issues_resume.md) and [`issues_jd.md`](file:///d:/Projects/resume-intelligence-platform/issues_jd.md).
  2. Complete [`fixed.md`](file:///d:/Projects/resume-intelligence-platform/fixed.md) report.
- **Verification:** Documentation 100% consistent with code.

---

### Phase 4.5 Day 11 Block 5: Formal Phase 4.5 Sign-Off & Phase 5 Kickoff (15 min)
- **Target Issues:** Milestone transition
- **Scope & Actions:**
  1. Final full test suite run across the entire workspace.
  2. Confirm **0 failures**, zero blocking defects.
  3. Mark **Phase 4.5: COMPLETE ✅**.
  4. Unlock **Phase 5: Resume ↔ JD Matching Engine**.

---

## Minor Issues Deferred to Parallel Fixes in Phase 6

The following minor, cosmetic, or non-blocking issues are cataloged to be addressed in parallel during **Phase 6 (ML/NLP Intelligence)** so that **Phase 5 (Matching Engine)** is not blocked:

### Resume Minor Issues (Deferred to Phase 6)
- **R-003 (P1):** Name parser casing transformation (`.title()`) and phone/email pre-check heuristics.
- **R-011 (P2):** Secondary education header aliases (`ACADEMIC BACKGROUND`, `DEGREES`, `SCHOOLING`).
- **R-012 (P2):** Secondary experience header aliases (`CAREER HISTORY`, `EMPLOYMENT HISTORY`).
- **R-014 (P1):** Dedicated schema representation for `ACHIEVEMENTS`.
- **R-015 (P2):** Dedicated schema representation for `CERTIFICATIONS` and `PUBLICATIONS`.
- **R-016 (P2):** Dedicated schema representation for `SUMMARY` / `OBJECTIVE`.
- **R-017 (P2):** Normalization of wrapped multi-line skill values.
- **R-018 (P3):** Glyph/font icon artifacts in raw text layer.
- **R-019 (P2):** Inclusive (+1) month counting interval clarification.
- **R-020 (P4):** Duplicate name annotation artifact in PDF text layer.
- **R-021 (P2):** Secondary/senior-secondary school degree aliases.
- **R-027 (P2):** Fractional CGPA string parsing (`8.67/10.0`).
- **R-028 (P2):** Bullet-prefixed education score lines.
- **R-029 (P1):** Hyperlinks on project sub-lines below the title bounding box.
- **R-032 (P2):** In-place `text_blocks` dictionary mutation idempotency.
- **R-033 (P2):** Routing non-standard sections (`INTERESTS`, `ABOUT ME`) into schema.
- **R-039 (P2):** Completeness analyzer project requirement relaxation for experienced candidates.
- **R-040 (P2):** Premier institute acronyms (`IISER`, `NIT`, `IIIT`).

### JD Minor Issues (Deferred to Phase 6)
- **JD-007 (P2):** Fallback to max skill-specific experience when overall experience is missing.
- **JD-010 (P3):** Decoupling `KNOWN_SKILLS` from `SKILL_YOE_PATTERN` regex.
- **JD-011 (P2):** Line-by-line vs joined-text cross-context regex scanning safeguards.