# Resume Intelligence Platform — Testing & Integration Plan

## A. Current Status & Verified Baseline

- **Current Block Status:** Block 1 = **COMPLETE** ✅
- **Full Test Suite Baseline:** **359 passed**, 0 failed
- **Active Warnings:**
  - `PytestCacheWarning`: `could not create cache path D:\Projects\resume-intelligence-platform\.pytest_cache\v\cache\nodeids: [WinError 5] Access is denied`
  - **Classification:** Local Windows filesystem permissions issue on `.pytest_cache`. Tracked separately from functional test failures. It does **not** represent a product defect or test assertion failure.
- **Baseline Checkpoint:**
  > **Checkpoint:** `359 passing before Block 2 changes.`
  > All subsequent blocks must preserve this green baseline without modifying or weakening existing tests.

---

## B. Test-First Execution Protocol

For every block from Block 2 onward, execution must follow this strict 8-step protocol:
1. **Inspect current implementation:** Read active service and parser code to establish existing runtime behavior.
2. **Identify the contract:** Explicitly state the contract between components (inputs, outputs, exceptions).
3. **Write/adjust focused tests:** Write targeted tests asserting observable contracts. Avoid testing internal implementation details.
4. **Run focused tests:** Execute only the newly added/modified test subset (`pytest <test_file> -k <test_name>`).
5. **Fix production code only if required:** Modify production code **only** when active implementation violates the intended contract.
6. **Run complete suite:** Execute `pytest` across the entire workspace.
7. **Record test count:** Log the new passing test baseline (e.g., `359 + N passing`).
8. **Mark block complete:** Check off acceptance criteria and set the regression checkpoint.

---

## C. Block 2: PDF Ingestion & Raw Extraction Boundary

### Objective
Verify the boundary between raw PDF upload ingestion and low-level extraction functions ([`extract_text`](file:///d:/Projects/resume-intelligence-platform/src/parsers/pdf_parser.py#L3-L10), [`extract_text_blocks`](file:///d:/Projects/resume-intelligence-platform/src/parsers/pdf_parser.py#L28-L52), [`extract_links`](file:///d:/Projects/resume-intelligence-platform/src/parsers/pdf_parser.py#L12-L26)), confirming consistent byte routing, downstream text/block/link wiring, edge cases, and failure propagation behavior.

### Scope

- **B2.1 Upload Content Handling:**
  - Verify that `file.read()` bytes are read once and passed identically to `extract_text()`, `extract_text_blocks()`, and `extract_links()`.
  - *Existing Coverage Note:* Fully covered in Block 1 by [`test_process_resume_passes_uploaded_content_to_pdf_pipeline`](file:///d:/Projects/resume-intelligence-platform/tests/services/test_resume_service.py#L606-L733). **Do not duplicate.**

- **B2.2 Extraction Integration:**
  - Verify that extracted text flows into [`clean_text()`](file:///d:/Projects/resume-intelligence-platform/src/parsers/text_parser.py) and downstream section/contact detection.
  - Verify that `extract_text_blocks` output and `extract_links` output flow directly as inputs to [`process_projects(text_blocks, links)`](file:///d:/Projects/resume-intelligence-platform/src/parsers/project_parser.py).
  - *Existing Coverage Note:* Text flow into `clean_text` and `detect_sections` is covered by [`test_process_resume_detects_sections_from_cleaned_text`](file:///d:/Projects/resume-intelligence-platform/tests/services/test_resume_service.py#L735-L853). The passing of `text_blocks` and `links` into `process_projects` is not yet asserted at the service integration level.

- **B2.3 Edge Cases:**
  - **Blank / Text-Free PDF:** When a valid PDF contains no extractable text (e.g. blank page), `extract_text()` returns `""`, `extract_text_blocks()` returns `[]`, and `extract_links()` returns `[]`. The service must execute without crashing, returning empty lists/None for downstream extracted entities.
  - **Empty Byte Stream (`b""`):** Passing empty bytes causes PyMuPDF to raise `pymupdf.EmptyFileError`. The service contract does not trap this; it propagates as an unhandled extraction error.

- **B2.4 Failure Behavior:**
  - **Current Runtime Contract:** [`process_resume()`](file:///d:/Projects/resume-intelligence-platform/src/services/resume_service.py#L25-L115) does **not** wrap PDF extraction calls in `try...except`.
  - When an underlying extraction function raises an exception (e.g. `pymupdf.FileDataError` on corrupt bytes, or `pymupdf.EmptyFileError` on empty stream), the exception **propagates directly to the caller**.
  - *Contract Rule:* Do **not** invent a defensive `{"error": ...}` catch block for corrupt PDF bytes unless an explicit API contract change is approved. Document and test the existing propagation contract.

### Existing Coverage

| Test | Location | What is Covered |
|---|---|---|
| `test_process_resume_rejects_non_pdf` | `tests/services/test_resume_service.py:567` | Non-PDF content-type rejection |
| `test_process_resume_does_not_process_non_pdf` | `tests/services/test_resume_service.py:582` | Short-circuit before parser invocation |
| `test_process_resume_passes_uploaded_content_to_pdf_pipeline` | `tests/services/test_resume_service.py:606` | B2.1: identical bytes passed to text, blocks, links |
| `test_process_resume_detects_sections_from_cleaned_text` | `tests/services/test_resume_service.py:735` | B2.2 (partial): text flows to cleaner and section detector |
| `test_extract_text` | `tests/parsers/test_pdf_parser.py:5` | Direct unit test for `extract_text` |
| `test_extract_text_blocks` | `tests/parsers/test_pdf_parser.py:22` | Direct unit test for `extract_text_blocks` |
| `test_extract_links` | `tests/parsers/test_pdf_parser.py:46` | Direct unit test for `extract_links` |

### Tests to Add

1. **`test_process_resume_passes_blocks_and_links_to_projects`** (`tests/services/test_resume_service.py`):
   - Monkeypatch `extract_text_blocks` to return a sentinel block list `[{"text": "Project A", ...}]`.
   - Monkeypatch `extract_links` to return a sentinel link list `[{"url": "https://github.com/..."}]`.
   - Monkeypatch `process_projects` to record received arguments.
   - Assert `process_projects` received the exact block and link data returned by the extractors.
2. **`test_process_resume_handles_blank_pdf_without_crashing`** (`tests/services/test_resume_service.py`):
   - Monkeypatch `extract_text` -> `""`, `extract_text_blocks` -> `[]`, `extract_links` -> `[]`.
   - Assert result is a valid dict with `sections == []`, `skills == []`, `experience == []`, `education == None`, and valid analyzer outputs.
3. **`test_process_resume_propagates_pdf_extraction_error`** (`tests/services/test_resume_service.py`):
   - Monkeypatch `extract_text` to raise `pymupdf.FileDataError("Failed to open stream")`.
   - Assert `pytest.raises(pymupdf.FileDataError)` when calling `process_resume()`, locking down the existing propagation contract.

### Production Changes Required
- **None expected.** Current implementation in [`src/services/resume_service.py`](file:///d:/Projects/resume-intelligence-platform/src/services/resume_service.py) already aligns with these contracts. Production code will only be changed if a test exposes an unintended deviation.

### Acceptance Criteria
- [ ] B2.1: Upload byte consistency verified (covered by existing B1 test).
- [ ] B2.2: Blocks and links integration with `process_projects` asserted.
- [ ] B2.3: Blank PDF text scenario validated with graceful empty output.
- [ ] B2.4: Extraction failure propagation locked down by contract test.
- [ ] Full test suite passes with **362 passing tests** (359 baseline + 3 new tests).
- [ ] 0 regressions across existing test suite.

### Regression Checkpoint
- **Target:** 362 passed, 0 failed.

---

## D. Subsequent Blocks Roadmap (In Dependency Order)

```
[Block 1: Service Entry & PDF Content Type] (COMPLETE - 359 tests)
                      │
                      ▼
[Block 2: PDF Ingestion & Raw Extraction Boundary] (NEXT - 3 tests)
                      │
                      ▼
[Block 3: Preamble, Contact & LinkedIn Integration]
                      │
                      ▼
[Block 4: Section Routing & Canonical Aggregation]
                      │
                      ▼
[Block 5: Normalization & Tenuring Calculation Pipeline]
                      │
                      ▼
[Block 6: Downstream Quality, Formatting & Completeness Analyzers]
                      │
                      ▼
[Block 7: End-to-End Schema Contract & Real-Resume Regression]
```

---

### Block 3: Preamble, Contact Info & LinkedIn Integration

- **Objective:** Verify candidate header extraction (name, email, phone) and resolve the unpopulated `linkedin` contract.
- **Scope:**
  - Verify `clean_text` feeds [`extract_email()`](file:///d:/Projects/resume-intelligence-platform/src/parsers/email_parser.py), [`extract_phone()`](file:///d:/Projects/resume-intelligence-platform/src/parsers/phone_parser.py), and [`extract_name()`](file:///d:/Projects/resume-intelligence-platform/src/parsers/name_parser.py).
  - Verify missing/empty contact details return `None` without crashing.
  - Address **R-002**: Current implementation hardcodes `"linkedin": None` in `resume_service.py` despite `extract_links()` capturing hyperlinks.
- **Existing Coverage:** Unit tests exist for email, phone, name parsers. Resume service hardcodes `linkedin: None`.
- **Tests to Add:**
  - Integration test for candidate contact extraction wiring.
  - Integration test asserting LinkedIn URL extraction from `extract_links()` output into `resume_data["linkedin"]`.
- **Production Changes:** Populate `"linkedin"` from links matching LinkedIn pattern in [`src/services/resume_service.py`](file:///d:/Projects/resume-intelligence-platform/src/services/resume_service.py).
- **Acceptance Criteria:** LinkedIn URL correctly populated when present; contact fields populate cleanly.
- **Regression Checkpoint:** Test baseline updated and verified green.

---

### Block 4: Section Routing & Canonical Aggregation

- **Objective:** Verify that section detector outputs are cleanly routed to specialized parsers, and that repeated/multi-page canonical sections are aggregated.
- **Scope:**
  - Skills section routing: All sections where `section["name"] == "skills"` aggregated before calling `extract_skills()` (R-010).
  - Experience section routing: All sections where `section["name"] == "experience"` aggregated before calling `process_experience()` (R-034).
  - Education section routing: All sections where `section["name"] == "education"` aggregated before calling `process_education()` (R-038).
  - Alternate headings routing: Headings like `WORK HISTORY`, `ACADEMIC QUALIFICATIONS`, `AREAS OF EXPERTISE` routed to canonical sections (R-037).
- **Existing Coverage:** Unit tests for `detect_sections` and section aliases in [`tests/parsers/test_section_detector.py`](file:///d:/Projects/resume-intelligence-platform/tests/parsers/test_section_detector.py).
- **Tests to Add:**
  - Service-level integration tests verifying multi-section concatenation for experience, education, and skills.
  - Service-level verification that unmapped non-standard sections (e.g. `certifications`, `publications`, `achievements`) do not bleed into parser inputs.
- **Production Changes:** Only if multi-section aggregation reveals edge cases in line separation.
- **Acceptance Criteria:** Multi-page resumes (e.g. `R04_MultiPage_Executive`) preserve entries across page boundaries without truncation.
- **Regression Checkpoint:** Test baseline updated and verified green.

---

### Block 5: Normalization & Tenuring Calculation Pipeline

- **Objective:** Ensure parser outputs are consistently normalized and aggregated metrics are accurately computed.
- **Scope:**
  - Normalizers: `normalize_skills`, `normalize_education`, `normalize_experience`, `normalize_projects`.
  - Total experience calculation via `calculate_total_experience` (handling ongoing "Present" tenure, R-030).
  - `process_skill_experience`: associating skills with duration across normalized experience entries.
- **Existing Coverage:** Unit tests in `tests/normalizers/` and `tests/analyzers/test_skill_experience_analyzer.py`.
- **Tests to Add:**
  - Integration test verifying that normalized data replaces raw parser dicts in `resume_data`.
  - Integration test verifying `skill_experience` receives normalized `experience` and `skills`.
- **Production Changes:** Only if contract mismatches exist between parser outputs and normalizer expectations.
- **Acceptance Criteria:** `total_experience_months` and `skill_experience` accurately computed on realistic fixtures.
- **Regression Checkpoint:** Test baseline updated and verified green.

---

### Block 6: Downstream Quality, Formatting & Completeness Analyzers

- **Objective:** Verify downstream analyzers operate reliably without crashing on sparse, unusual, or partial resumes.
- **Scope:**
  - `analyze_completeness`: verify required/recommended fields logic (especially for freshed/no-experience resumes, R-039).
  - `analyze_quality`: safe handling of missing years, None scores, and short descriptions (R-013).
  - `analyze_formatting`: consistent formatting diagnostics.
- **Existing Coverage:** Unit tests in `tests/analyzers/`.
- **Tests to Add:**
  - Service-level test verifying analyzers run successfully on minimal resumes (e.g. no experience, no projects).
  - Contract test asserting exact keys returned in `completeness`, `quality_check`, and `formatting_check`.
- **Production Changes:** None expected unless analyzer contracts deviate from service expectations.
- **Acceptance Criteria:** Analyzers execute cleanly without exceptions on all 12 corpus profiles.
- **Regression Checkpoint:** Test baseline updated and verified green.

---

### Block 7: End-to-End Service Contract & Real-Resume Regression

- **Objective:** Final integration lockdown and full-corpus regression testing.
- **Scope:**
  - Complete schema validation of `process_resume` return dictionary.
  - Regression execution against audit corpus (R01 through R12, including R04 multi-page, R10 alternate headings, R03 ML staff, R12 biomed).
  - Re-verify full test suite.
- **Existing Coverage:** End-to-end smoke test in `test_resume_service.py:test_process_resume()`.
- **Tests to Add:**
  - Comprehensive contract assertions validating all 15 top-level dictionary keys.
  - Integration regression assertions against standard PDF fixtures.
- **Production Changes:** None.
- **Acceptance Criteria:** 100% green test suite across unit, integration, and corpus validation.
- **Regression Checkpoint:** Final full-suite pass with zero regressions.

---

## E. Architectural & Testing Principles

1. **Avoid Test Duplication:** Before drafting any new test, check existing parser, normalizer, and service tests. Extend existing test functions with parameterized cases where appropriate instead of creating duplicate scaffolds.
2. **Observable Contracts over Implementation Details:** Tests must validate observable outputs, returned dictionaries, and exception propagation rather than internal variable naming or private helper sequencing.
3. **No Unrelated Refactoring:** Never refactor working parsers, normalizers, or analyzers during an integration block unless the block's explicit scope demands it.
4. **Preserve Green Baseline:** Every block starts and ends with a green test run. Never break existing passing tests to accommodate new ones.

---

## F. Current Execution State

### Completed
- **Block 1: Service Entry & PDF Content Type Validation** ✅
- **Test Baseline:** **359 passed, 0 failed** (1 benign `.pytest_cache` permission warning)

### Next Immediate Action
- **Block 2: PDF Ingestion & Raw Extraction Boundary**
  1. Add `test_process_resume_passes_blocks_and_links_to_projects` to [`tests/services/test_resume_service.py`](file:///d:/Projects/resume-intelligence-platform/tests/services/test_resume_service.py).
  2. Add `test_process_resume_handles_blank_pdf_without_crashing` to [`tests/services/test_resume_service.py`](file:///d:/Projects/resume-intelligence-platform/tests/services/test_resume_service.py).
  3. Add `test_process_resume_propagates_pdf_extraction_error` to [`tests/services/test_resume_service.py`](file:///d:/Projects/resume-intelligence-platform/tests/services/test_resume_service.py).
  4. Run focused tests, then full test suite to reach verified baseline of **362 passing tests**.

### Subsequent Execution Order
1. **Block 3:** Preamble, Contact & LinkedIn Integration
2. **Block 4:** Section Routing & Canonical Aggregation
3. **Block 5:** Normalization & Tenuring Calculation Pipeline
4. **Block 6:** Downstream Quality, Formatting & Completeness Analyzers
5. **Block 7:** End-to-End Service Contract & Real-Resume Regression
