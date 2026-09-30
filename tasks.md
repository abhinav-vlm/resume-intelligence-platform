# Phase 4.5 Hardening & Generalization — 7-Day Sprint Plan (Days 5–11)

**Sprint Window:** Next 7 Working Days (Continuing from Phase 4.5 Day 5 through Day 11)  
**Daily Time Budget:** **Max 2 Hours Total per Day** (All 5 daily blocks combined = 120 minutes)  
**Block Allocation:** Up to 5 focused blocks per day (10–35 mins each, totaling 120 mins)  
**Baseline Test Count:** **427 passing tests (Phase 4.5 Day 8 baseline: 425 → 427 passed, +2 new tests), 0 regressions**  
**Core Strategy:** **Major Issues First (P0 & Critical P1 Blockers)** to rapidly unlock **Phase 5 (Resume ↔ JD Matching)**. Minor issues (P2–P4 cosmetics, secondary aliases, schema enhancements) are cataloged and deferred to be fixed in parallel during **Phase 6 (ML/NLP Intelligence)**.

---

## 7-Day Sprint Master Schedule (2 Hours Total / Day)

| Day | Daily Focus (Max 2h Total) | Major Issues Targeted (P0 / Critical P1) | Outcome & Deliverable |
|---|---|---|---|
| **Phase 4.5 Day 5** | Resume P0 Boundaries & Date/Experience Normalization | R-023, R-024, R-025, R-035, R-009, R-006, R-030, R-031, R-005 | Zero P0 structural defects; active employment tenure resolved; green test baseline |
| **Phase 4.5 Day 6** | Resume Multi-Page Continuity & Entity Splitting | R-034, R-038, R-022, R-007, R-026, R-036 | Multi-page resume preservation verified; skill conjunctions & combined degrees split; resume pipeline locked |
| **Phase 4.5 Day 7** ✅ | JD Preprocessing & Skill Vocabulary Overhaul (JD-001) | JD-013, JD-001 | Text cleaning wired into JD service; 17-skill bottleneck replaced with scalable tech taxonomy; 95.3% extraction coverage on 5 real JDs; baseline **425 passed** |
| **Phase 4.5 Day 8** ✅ | JD Section Detection & Requirement Context (Required vs Optional) | JD-018, JD-004, JD-006, JD-008, JD-009, JD-015 | Shared `detect_sections()` wired for JDs; context-inherited requirement classification (`required`/`optional`); structured noise filtering; 35-failure test regression resolved; 427 passed, 0 failed |
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

### Phase 4.5 Day 5 Block 2: Fix P0 Project Boundaries & Headers (30 min) ✅ (COMPLETED)
- **Status:** **COMPLETE**
- **Target Issues:** R-023, R-024, R-035, R-009 (residual)
- **Accomplishments:**
  1. **R-023:** Added `is_duration(line)` guard to `_is_project_title()` in `src/utils/text_utils.py` and updated `DURATION_PATTERNS` so standalone project duration lines (`2022 - 2024`, `Jan 2022 - Mar 2024`) are never treated as project titles.
  2. **R-024:** Added `"TECHNOLOGIES"` and `"TECHNOLOGIES & TOOLS"` to `SECTION_HEADERS` and mapped to `"skills"` in `SECTION_ALIASES` in `src/configs/header_configs.py` to stop boundary bleed into projects.
  3. **R-035:** Added Unicode bullet glyphs (`‣`, `●`, `•`, `-`, `*`) in `src/parsers/project_parser.py` so non-standard bullet lines do not mutate the project title into an empty string.
  4. **R-009 (Residual):** Implemented `_is_likely_skill_list()` in `src/utils/text_utils.py` and wired into `project_parser.py` to reject single/multi-token tech lists (`CSS`, `HTML, CSS`, `React, Node.js`) from creating phantom project titles, while preserving comma-containing descriptions and wrapped bullet continuations.
- **Verification:** 11 focused unit tests in `tests/parsers/test_project_parser.py` (25/25 passing).

---

### Phase 4.5 Day 5 Block 3: Fix P0/P1 Experience Parsing Collision (30 min) ✅ (COMPLETED)
- **Status:** **COMPLETE**
- **Target Issues:** R-025, R-005
- **Accomplishments:**
  1. **R-025:** Re-ordered condition checks in `src/parsers/experience_parser.py` so that bullet prefixes (`•`, `-`, `*`, `‣`, `●`) are evaluated **before** `ROLE_KEYWORDS` matching, preventing bullet lines from being stolen as job titles or splitting entries.
  2. **R-005:** Upgraded `contains_keywords()` in `src/utils/text_utils.py` to use regex word boundaries (`\b`) preventing substrings (e.g. `Engineering Systems Pvt Ltd`) from false role matches, and cleanly segmented consecutive experience entries upon role detection following a duration line.
  3. Enabled multi-line wrapped bullet continuation handling in experience descriptions.
- **Verification:** 4 new unit tests in `tests/parsers/test_experience_parser.py` (11/11 passing).

---

### Phase 4.5 Day 5 Block 4: Tenure & Date Normalization ("Present" / Abbreviations) (25 min) ✅ (COMPLETED)
- **Status:** **COMPLETE**
- **Target Issues:** R-006, R-030, R-031
- **Accomplishments:**
  1. **R-006 & R-030:** Updated `DURATION_PATTERNS` in `src/configs/text_utils_configs.py` to match `PRESENT`. In `src/normalizers/experience_normalizer.py`, mapped `"Present"` case-insensitively to the current calendar date (`datetime.now()`), populating current month name and year so active employment computes accurate, non-zero tenure.
  2. **R-031:** Expanded month matching in `experience_normalizer.py` with `month_aliases` supporting all 12 three-letter month abbreviations (`Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`, `Oct`, `Nov`, `Dec`) and normalizing them to canonical full month names (`January`..`December`).
- **Verification:** 16 focused unit tests in `tests/normalizers/test_experience_normalizer.py` asserting abbreviations and `Present` duration normalization.

---

### Phase 4.5 Day 5 Block 5: Service Test Contracts & Daily Checkpoint (15 min) ✅ (COMPLETED)
- **Status:** **COMPLETE**
- **Target Issues:** Test suite regression & daily baseline lockdown
- **Accomplishments:**
  1. Full regression run across the entire workspace test suite passed with 0 failures and 0 warnings.
  2. Synchronized issue ledger in `issues_resume.md` and verification report in `fixed.md`.
- **Checkpoint:** Baseline locked at **399 passing tests** (+31 new tests today: +11 project parser, +4 experience parser, +16 experience normalizer). 0 regressions.

---

## Phase 4.5 Day 6: Resume Multi-Page Continuity & Entity Parsing (2h Total)

### Phase 4.5 Day 6 Block 1: Multi-Page Experience & Education Continuity (25 min) ✅ (COMPLETED)
- **Status:** **COMPLETE**
- **Target Issues:** R-034, R-038
- **Accomplishments:**
  1. Created binary PDF and text fixture `tests/fixtures/R04_MultiPage_Executive.pdf` and `tests/fixtures/R04_MultiPage_Executive.txt`.
  2. Created 4 service-level integration tests in `tests/services/test_resume_service_multipage.py` verifying multi-page experience entries survive and links are extracted across page boundaries.
- **Verification:** 4/4 passing in `test_resume_service_multipage.py`.

---

### Phase 4.5 Day 6 Block 2: Section Detector Aliases Verification (20 min) ✅ (COMPLETED)
- **Status:** **COMPLETE**
- **Target Issues:** R-024
- **Accomplishments:**
  1. Verified `TECHNOLOGIES` and `TECHNOLOGIES & TOOLS` header recognition in `tests/parsers/test_section_detector.py` (+2 tests).
- **Verification:** 65/65 passing in `test_section_detector.py`.

---

### Phase 4.5 Day 6 Block 3: Active Employment Normalization Verification (20 min) ✅ (COMPLETED)
- **Status:** **COMPLETE**
- **Target Issues:** R-006, R-030
- **Accomplishments:**
  1. Verified dynamic `Present` end-date month/year resolution in `tests/normalizers/test_experience_normalizer.py`.
- **Verification:** 64/64 passing in `test_experience_normalizer.py`.

---

### Phase 4.5 Day 6 Block 4: Skill Conjunction Splitting (25 min) ✅ (COMPLETED)
- **Status:** **COMPLETE**
- **Target Issues:** R-022
- **Accomplishments:**
  1. Conjunction splitting (`\s+and\s+`) added to `src/parsers/skills_parser.py` (`extract_skill_candidates`).
  2. Added `HTML` and `CSS` to `KNOWN_SKILLS` in `src/configs/skill_configs.py`.
  3. Verified candidate extraction via `test_conjunction_separated_skills_are_split` in `tests/parsers/test_skills_parser.py`.
- **Verification:** 23/23 passing in `test_skills_parser.py`. Full suite: **408 passed, 0 failed**.

---

### Phase 4.5 Day 6 Block 5: READ-ONLY AUDIT & Gap Analysis (20 min) ✅ (COMPLETED)
- **Status:** **COMPLETE (AUDIT ONLY)**
- **Target Issues:** Full working tree audit across 9 investigation areas
- **Accomplishments:**
  1. Executed full workspace test suite: **408 passed, 0 failed** in 1.00s.
  2. Audited skills parser: identified bullet retention on un-colonized lines (R-043), multi-word phrase fragmentation (R-044), and slash acronym fragmentation (R-045).
  3. Audited experience parser: identified company-first layout misassignment and description leakage (R-005).
  4. Audited experience normalizer: identified 0 month calculation on year-only (`2020 - 2024`) and year-to-Present (`2024 - Present`) tenures (R-046).
  5. Audited education parser: identified degree overwriting on Degree-first layouts (R-047) and composite line degree drops (R-026).
  6. Audited configurations: verified missing doctoral degrees (R-036) and premier institute acronyms (R-040).
  7. Audited project parser, skill normalizer, name parser, and text preprocessing.
  8. Synchronized tracking documentation across `issues_resume.md`, `fixed.md`, and `tasks.md`.
  9. Strict compliance: 0 source files modified, 0 test files modified, 0 new files created.
- **Checkpoint Target:** Repository locked at **408 passed, 0 failed**. Audit ready for review.

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

### Phase 4.5 Day 7 Block 4: Real-World JD Skill Verification (25 min) ✅ (COMPLETED)
- **Status:** **COMPLETE**
- **Target Issues:** JD-001 Validation on Real JDs
- **Accomplishments:**
  1. Created binary PDF and text fixtures in `tests/fixtures/`: `jd_ml_engineer_test.pdf`, `Meta_ML_JD.pdf` (`Meta ML JD.pdf`), `Databricks_SE_JD.pdf` (`Databricks SE JD.pdf`), `DeepMind_Research_Engineer_JD.pdf` (`DeepMind Research Engineer JD.pdf`), and `Stripe_Backend_JD.pdf` (`Stripe Backend JD.pdf`).
  2. Verified skill extraction rate reaches 100% (>90% threshold) across all real JD fixtures in `tests/parsers/test_real_jd_fixtures.py` (+12 tests).
- **Verification:** 12/12 passing in `test_real_jd_fixtures.py`. Full test suite: **425 passed, 0 failed**.

---

### Phase 4.5 Day 7 Block 5: Daily Checkpoint & Test Baseline Update (10 min) ✅ (COMPLETED)
- **Status:** **COMPLETE**
- **Target Issues:** Regression checkpoint + documentation sync
- **Accomplishments:**
  1. Full workspace test suite: **425 passed, 0 failed** in 1.22s.
  2. Updated `fixed.md` with JD-001 and JD-013 resolution (Section 8).
  3. Updated `issues_jd.md`: JD-001 marked RESOLVED, audit summary updated to 17 remaining open issues.
  4. Created `future_architecture_tasks.md` to catalog compound skill recognition, semantic validation, and vocabulary evolution as future concerns — NOT current defects.
- **Checkpoint:** Baseline locked at **425 passed, 0 failed**. JD-001 RESOLVED. Phase 4.5 Day 7 COMPLETE.

---

## Phase 4.5 Day 8: JD Section Detection & Requirement Context (2h Total)

### Phase 4.5 Day 8 Block 1: Structured JD Section Detector (JD-018) (30 min) ✅ (COMPLETED)
- **Status:** **COMPLETE** *(implemented as pre-existing production refactor before Day 8 test sprint)*
- **Target Issues:** JD-018
- **Accomplishments:**
  1. `detect_sections()` in `src/parsers/section_detector.py` extended with `section_headers`, `section_aliases`, and `prefix_matching` parameters — now serves both resume and JD pipelines.
  2. `detect_jd_sections()` added to `src/parsers/jd_parser.py`, delegating to the shared detector with `JD_SECTION_HEADERS`, `JD_SECTION_ALIASES`, and `prefix_matching=True`.
  3. `JD_SECTION_HEADERS` and `JD_SECTION_ALIASES` populated in `src/configs/jd_configs.py` covering: `ROLE_OVERVIEW`, `REQUIREMENTS`, `PREFERRED_QUALIFICATIONS`, `RESPONSIBILITIES`, `BENEFITS`, `COMPANY_INFO` (noise), `EQUAL_OPPORTUNITY` (noise), `NOISE`.
  4. `detect_sections()` returns structured section dictionaries: `{"name": canonical, "original_name": normalized, "text": body}`.
- **Verification:** Shared section detector drives both resume and JD pipelines. All real-JD fixture tests pass.

---

### Phase 4.5 Day 8 Block 2: Re-entrant & Robust Noise Filtering (25 min) ✅ (COMPLETED)
- **Status:** **COMPLETE** *(implemented as pre-existing production refactor before Day 8 test sprint)*
- **Target Issues:** JD-006, JD-009, JD-015
- **Accomplishments:**
  1. `_filter_noise_sections()` in `src/parsers/jd_parser.py` now operates on structured section dictionaries — it filters on `section["name"]` membership in `NOISE_SECTIONS` (`{"COMPANY_INFO", "EQUAL_OPPORTUNITY", "NOISE"}`) rather than on raw line strings.
  2. Noise filtering is fully re-entrant: entering a noise section discards only its own body; subsequent valid sections are preserved as independent structured objects.
  3. Prefix/keyword matching via `prefix_matching=True` in `detect_sections()` handles decorated noise headers (`About Us - Our Story`, `About the Company | Our Mission`) without requiring exact-match expansion of `NOISE_SECTION_HEADERS`.
- **Verification:** All `_filter_noise_sections` tests pass with structured section dict inputs.

---

### Phase 4.5 Day 8 Block 3: Context-Inherited Requirement Classification (JD-004, JD-008) (35 min) ✅ (COMPLETED)
- **Status:** **COMPLETE** *(implemented as pre-existing production refactor before Day 8 test sprint)*
- **Target Issues:** JD-004, JD-008
- **Accomplishments:**
  1. **JD-004:** `_classify_skill_requirement()` now accepts a `parent_section` argument. Skills under `REQUIREMENTS` / `BASIC_QUALIFICATIONS` / `MINIMUM_QUALIFICATIONS` default to `"required"`; skills under `PREFERRED_QUALIFICATIONS` / `BONUS` / `DESIRED` default to `"optional"`. Explicit line-level signals still take precedence.
  2. **JD-008:** `_extract_skills()` now accepts `list[dict]` sections, iterates section bodies, and returns both a deduplicated `skills: list[str]` and a unified `skill_requirements: list[{skill, requirement}]`. The old per-line `{line, requirement}` shape is replaced by the per-skill `{skill, requirement}` shape.
  3. `_section_requirement_context()` helper introduced to translate canonical section names into default requirement levels.
- **Verification:** `test_extract_skills_requirement_from_requirements_section` and `test_extract_skills_requirement_from_preferred_section` confirm context inheritance.

---

### Phase 4.5 Day 8 Block 4: Test-Contract Migration & Genuine Bug Fix (20 min) ✅ (COMPLETED)
- **Status:** **COMPLETE**
- **Target Issues:** Test regression (35 failures); genuine production bug in `parse_jd()`
- **Accomplishments:**
  1. **Test regression root cause:** The production refactor (Blocks 1–3) introduced a structured-section contract. 35 tests remained on the old contract (list-of-strings inputs to `_extract_skills`, `_filter_noise_sections`; `{line, requirement}` shape for `skill_requirements`; `detect_sections` mocks not accepting keyword arguments).
  2. **`tests/parsers/test_jd_parser.py`** — Migrated all `_extract_skills()` and `_filter_noise_sections()` tests to accept and assert on structured section dictionaries. Preserved all behavioral contracts: known/unknown skill extraction, case-insensitive matching, deduplication, partial-word protection, C++ vs C overlap, MySQL vs SQL overlap, multi-skill lines, requirement classification. Updated `test_extract_role_stops_at_noise_section` to the current architecture.
  3. **`tests/services/test_jd_service.py`** — Migrated `skill_requirements` assertion from `{"line", "requirement"}` shape to the current `{"skill", "requirement"}` shape.
  4. **`tests/services/test_resume_service_injestion.py`** — Updated all four `detect_sections` mocks to accept `section_headers`, `section_aliases`, and `**kwargs` to match the production call signature.
  5. **Genuine production bug fixed** in `src/parsers/jd_parser.py`:
     - **Root cause:** Preamble sections produced by `detect_sections()` have `original_name = None`. `parse_jd()` unconditionally appended `section["original_name"]` to `clean_jd`, inserting `None`. `_extract_role()` then crashed with `TypeError: argument of type 'NoneType' is not iterable` when evaluating `":" not in line` on a `None` value.
     - **Fix:** Guard the reconstruction loop — only append `original_name` when it is truthy (non-`None`).
     - **Change:** Minimal one-condition guard: `if section["original_name"]: clean_jd.append(...)`
- **Verification:** Targeted suite: **75 passed, 0 failed**.


---

### Phase 4.5 Day 8 Block 5: Daily Checkpoint & Regression Suite (10 min) ✅ (COMPLETED)
- **Status:** **COMPLETE**
- **Target Issues:** Regression check
- **Accomplishments:**
  1. Full test suite across workspace: **427 passed, 0 failed** in 1.01s.
  2. Updated `fixed.md` with Day 8 execution summary (Section 9): JD-004, JD-006, JD-008, JD-009, JD-015, JD-018 resolutions documented.
  3. Updated `issues_jd.md`: JD-004, JD-006, JD-008, JD-009, JD-015, JD-018 marked RESOLVED; audit summary updated.
- **Checkpoint:** Baseline locked at **427 passed, 0 failed**. Phase 4.5 Day 8 COMPLETE.

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