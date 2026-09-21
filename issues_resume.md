# Resume Parser Issues

---

~~## R-001: Skills parser silently drops all skills on lines without a colon~~

- **Source:** `HARSHIT_WEBDEV.pdf`, `resume_without_experience.pdf`
- **Category:** Information Loss
- **Severity:** P0

### Observed
`skills_parser.py` only extracts skills from lines that contain a `:`. Lines without a colon are completely skipped.

```
# From cleaned text (both resumes):
TECHNICAL SKILLS :
• Programming Languages : Python,C++, SQL, JavaScript, HTML, CSS, C   ← extracted
• Web Development Frameworks : ReactJS, Express.JS, Next.JS, Jest, MongoDB ← extracted
```

If a resume formats its skills section as a plain list (no `Category: skill, skill` pattern), the entire skills section returns `None`:

```python
extract_skills('TECHNICAL SKILLS :\nPython\nReact\nSQL')
# => None
```

### Source Evidence
Many real-world resumes list skills as plain bullet-points or comma-separated values without a category prefix:

```
SKILLS
Python, React, SQL, Docker
```
or
```
SKILLS
• Python
• React
• SQL
```

### Expected
A robust parser should extract individual skill tokens regardless of whether they appear on a categorized line (`Category: skill1, skill2`) or as plain items.

### Impact
Entire skills section becomes `None` for any resume not using the `Category: value` format. Downstream `skill_experience`, matching, scoring, and completeness checks all fail or produce empty results.

### Likely Area
`src/parsers/skills_parser.py` — the `if ':' in line` branch (line 19). Lines without a colon are not processed at all.

### Status
- **Status:** FIXED
- **Fixed in:** Phase 4.5 Day 1 (commit `e72a322`)
- **Validation:** Unit tests in `test_skills_parser.py` (22 tests) + integration tests in `test_resume_service.py`. Verified on `HARSHIT_WEBDEV.pdf` and `resume_without_experience.pdf`.
- **Relevant test:** `tests/parsers/test_skills_parser.py`, `tests/services/test_resume_service.py`
- **Notes:** `extract_skill_candidates` supports lines without colons, skips `SKILL_CATEGORY_HEADERS`, splits on delimiters `[,|/]`, and separates known and unknown skills with length/word filters.

---

## R-002: LinkedIn URL extracted from PDF links is never surfaced in the output

- **Source:** `HARSHIT_WEBDEV.pdf`
- **Category:** Information Loss
- **Severity:** P0

### Observed
The PDF contains a clickable LinkedIn hyperlink:
```
"url": "https://www.linkedin.com/in/abhinav-pratap-singh-1a8a57200/"
```
`extract_links()` correctly detects this link. However, the resume service hard-codes `"linkedin": None` in `resume_data` and never assigns the LinkedIn URL.

```python
# resume_service.py line 70
"linkedin": None,
```

### Source Evidence
PDF links list from `HARSHIT_WEBDEV.pdf`:
```json
{"url": "https://www.linkedin.com/in/abhinav-pratap-singh-1a8a57200/", ...}
```

The resume visually shows a LinkedIn icon with a link. The `.txt` fixture also shows `Abhinav Pratap Singh` (the display name) on a line with the LinkedIn icon character.

### Expected
LinkedIn URL should be resolved from the extracted links list and populated in the `linkedin` field of the output.

### Impact
`linkedin` is always `None` even when the document contains a LinkedIn URL. The `completeness_analyzer` marks `linkedin` as missing for every resume. Downstream matching and ATS scoring can never use the LinkedIn profile.

### Likely Area
`src/services/resume_service.py` — the `links` list is obtained but never searched for LinkedIn URLs before building `resume_data`.

### Status
OPEN

---

## R-003: Name parser returns the first non-empty line unconditionally — misidentifies non-name content as name

- **Source:** `HARSHIT_WEBDEV.pdf`
- **Category:** Incorrect Extraction
- **Severity:** P1

### Observed
For `HARSHIT_WEBDEV.pdf`, the raw extracted text contains icon/glyph characters before the name line:

```
'ABHINAV PRATAP SINGH\n\x83 +91 9774913812\n# apsbqt@gmail.com\n...'
```

After `clean_text()`, the cleaned output is:
```
ABHINAV PRATAP SINGH
 +91 9774913812
# apsbqt@gmail.com
ï Abhinav Pratap Singh
§ Blockmecoder
```

The first non-empty line after cleaning is `ABHINAV PRATAP SINGH` — so this case succeeds. However, if a PDF's text extraction order differs (e.g., phone number renders first), the name parser would return the phone number or email as the name:

```python
extract_name(' +91 9774913812\n# apsbqt@gmail.com\nABHINAV PRATAP SINGH')
# => '+91 9774913812'  (VERIFIED in edge case test)
```

Also: the parser applies `.title()` to the returned line. For `ABHINAV PRATAP SINGH` it returns `Abhinav Pratap Singh` — which transforms the casing from ALL-CAPS. This is a silent casing transformation that discards the original formatting without any indication.

### Source Evidence
From `HARSHIT_WEBDEV.pdf` raw text, line 1 is `ABHINAV PRATAP SINGH` (all caps as intended). The `.title()` silently lowercases all letters except the first of each word.

### Expected
The name parser should not blindly return the first line. At minimum, it should skip lines that match email patterns, phone patterns, or consist of single special characters. The casing transformation should either be documented or preserved.

### Impact
On any resume where contact info appears before the name (different PDF column/flow order), the name field will contain a phone number or email. `.title()` also produces incorrect casing for names containing initials, prefixes (e.g., `O'Brien` → `O'Brien` but `McDonalds` → `Mcdonalds`).

### Likely Area
`src/parsers/name_parser.py` — the `return line.title()` on the first non-empty line (line 9).

### Status
OPEN

---

~~## R-004: Wrapped/continued bullet lines are split into a new orphan line in the description~~

- **Source:** `HARSHIT_WEBDEV.pdf`
- **Category:** Information Loss
- **Severity:** P1

### Observed
When a bullet point wraps to the next line in the PDF (due to line width), the continuation line does not start with a bullet character. The experience parser only appends lines starting with `•`, `-`, or `*` to `description`. Lines without these prefixes that appear within experience are silently dropped.

From cleaned text of `HARSHIT_WEBDEV.pdf`:
```
• Utilized Latest technology in Next library to improve a web application with 15 percent visual inhancement and
10 percent page loading.
```
The second line `10 percent page loading.` does NOT start with a bullet. The parser result shows:
```json
"description": [
  "• Utilized Latest technology in Next library to improve a web application with 15 percent visual inhancement and",
  ...
]
```
The continuation `10 percent page loading.` is completely absent from the output.

### Source Evidence
Source document (`.txt` fixture, lines 27-28):
```
• Utilized Latest technology in Next library to improve a web application with 15 percent visual inhancement and
10 percent page loading.
```
The full sentence should be: *"...with 15 percent visual inhancement and 10 percent page loading."*

### Expected
Continuation lines (lines within a description block that don't start with a bullet and don't match section headers or durations) should be appended to the previous bullet's text, not silently dropped.

### Impact
Metric data and key qualitative details in experience descriptions are lost. `quality_analyzer` will report incorrect `content_length` and may incorrectly report `has_metrics: false` when the metric was in the dropped continuation line.

### Likely Area
`src/parsers/experience_parser.py` — `_extract_experience()` only adds bullet lines to `curr_experience` via the `if line.startswith(...)` check at line 52. Non-bullet, non-duration lines within the experience block are discarded.

### Status
- **Status:** FIXED
- **Fixed in:** Phase 4.5 Day 1 (commit `e72a322`)
- **Validation:** Unit tests in `test_experience_parser.py` + verified on `HARSHIT_WEBDEV.pdf` where continuation lines are appended.
- **Relevant test:** `tests/parsers/test_experience_parser.py`
- **Notes:** `_parse_experience` maintains `description_started` state flag and appends non-bullet continuation lines to `experience["description"][-1]`.

---

## R-005: Experience parser assumes `block[i-1]` is always the company — crashes or misassigns on non-standard layouts

- **Source:** `HARSHIT_WEBDEV.pdf`, generalization
- **Category:** Incorrect Extraction / Generalization
- **Severity:** P1

### Observed
In `_parse_experience()`, when a duration line is found, the company is assigned as `block[i-1]` (the line immediately preceding the duration line):

```python
elif is_duration(line):
    experience["duration"] = line
    experience["company"] = block[i-1]
```

This assumes a strict layout:
```
Company Name
Duration
Role
```

If the layout is:
```
Duration
Company Name
Role
```
or:
```
Company Name | Location
Duration
Role
```
the company would be assigned `None` (if duration is the first line, `i-1 = -1`, which in Python returns the last element), or would be incorrectly assigned the role line if role appears before duration.

### Source Evidence
The HARSHIT_WEBDEV.pdf has this layout (which works):
```
Gosotek
January - February, 2024
Front-End Software Engineering (Remote Intern)
```

Many real-world resumes use:
```
Software Engineer | Acme Corp        [Month Year - Month Year]
```
or:
```
[Duration on same line as company]
```

### Expected
The company assignment should be defensive: validate that `block[i-1]` is not a duration string, not a bullet, not a known section header, and not out of bounds before assigning it as company.

### Impact
For non-standard layouts the company field is either `None` or contains the wrong line. This corrupts the `skill_experience` evidence (which records company) and downstream matching.

### Likely Area
`src/parsers/experience_parser.py` — `_parse_experience()`, line 51: `experience["company"] = block[i-1]`.

### Status
OPEN

---

## R-006: Duration pattern does not match `Month YYYY - Month YYYY` format — "Present" not normalized

- **Source:** `HARSHIT_WEBDEV.pdf`, generalization
- **Category:** Information Loss / Generalization
- **Severity:** P1

### Observed
The `DURATION_PATTERNS` in `text_utils_configs.py` are:
```python
r"\d{4}\s*[-–]\s*(\d{4}|PRESENT)"
r"(JAN|FEB|...)...\s*[-–]\s*(JAN|FEB|...)...,?\s*\d{4}"
```

Test results:
```
is_duration('Jan 2020 - Mar 2021') => False
is_duration('January 2020 - Present') => True  (matches pattern 1 via PRESENT? No — 2020 is the 4-digit year, so "2020 - Present" matches)
```

Actually verified: `is_duration('January 2020 - Present') => True` because `2020` matches `\d{4}` and `Present` (uppercased: `PRESENT`) matches the `PRESENT` alt. BUT:
- `is_duration('Jan 2020 - Mar 2021') => False` — abbreviated months with a year on each side don't match.
- `_normalize_duration('2020 - Present') => (None, None, 2020, None)` — `Present` is not captured as `end_year`. The `end_year` is `None`, so `calculate_total_experience` **silently skips** this entry entirely (requires all 4 fields to be non-None).

### Source Evidence
For an internship `January - February, 2024` (both months same year), `_normalize_duration` returns `('January', 'February', 2024, 2024)` — handled by the special `month_count == 2, year_count == 1` branch. This works for HARSHIT_WEBDEV.

But `January 2020 - Present` returns `('January', None, 2020, None)` — `end_year` is `None`, entry is excluded from `calculate_total_experience`.

### Expected
- `Jan YYYY - Month YYYY` (abbreviated start month) should be recognized as a duration.
- `Present` should be resolved to the current date (or at minimum, the `end_year` and `end_month` should be set to a sentinel/current date) so that currently-employed candidates' tenure is counted.

### Impact
Currently-employed candidates (with `Present` end date) have their experience excluded from `total_experience_months` calculation, producing an incorrect (lower) total. Abbreviated month formats produce false negatives in `is_duration`.

### Likely Area
`src/configs/text_utils_configs.py` — `DURATION_PATTERNS`. Also `src/normalizers/experience_normalizer.py` — `_normalize_duration()` and `calculate_total_experience()`.

### Status
OPEN

---

## R-007: Project title field retains the `| GitHub` / `| LIVE` suffix — not split from the title

- **Source:** `HARSHIT_WEBDEV.pdf`, `resume_without_experience.pdf`
- **Category:** Information Loss / Schema Limitation
- **Severity:** P1

### Observed
All three projects have titles that include the link label embedded as text:
```json
"project": "Bloger - A Full Stack Blog App | GitHub"
"project": "Weather Sphere - A Real-time Weather App | GitHub"
"project": "PrompTopic - An AI Prompting Tool | GitHub"
```

The `| GitHub` suffix is a display artifact (hyperlink label embedded in the title text) — it is not part of the actual project name.

### Source Evidence
Source document line 33: `Bloger - A Full Stack Blog App | GitHub`
The actual project name is `Bloger - A Full Stack Blog App`. The `| GitHub` is just the text that the hyperlink anchor is attached to. The structured output conflates the link label with the project title.

### Expected
The project name should be `Bloger - A Full Stack Blog App`. The GitHub link is already correctly captured in `metadata`. The `| GitHub`, `| LIVE`, etc. suffixes should be stripped from the project title.

### Impact
Downstream text matching against project names will always see `| GitHub` as part of the name. Display in any UI will show the awkward suffix. The project title field is semantically incorrect.

### Likely Area
`src/parsers/project_parser.py` — `_parse_projects()` assigns the raw text line as `project["project"]` without stripping link-label suffixes (line 58).

### Status
OPEN

---

~~## R-008: First experience bullet continuation line lost — `10 percent page loading` dropped completely~~

- **Source:** `HARSHIT_WEBDEV.pdf`
- **Category:** Information Loss
- **Severity:** P1

### Observed
The first bullet in the Gosotek experience reads (from source):
```
• Utilized Latest technology in Next library to improve a web application with 15 percent visual inhancement and
10 percent page loading.
```
The parser output for this bullet is:
```
"• Utilized Latest technology in Next library to improve a web application with 15 percent visual inhancement and"
```
The continuation `10 percent page loading.` is completely absent from the structured output.

> **Note:** This is a concrete instance of R-004 but documented separately as a **confirmed data loss** in the actual test document, not a hypothetical.

### Source Evidence
`.txt` fixture lines 27-28 and cleaned text lines 23-24 both show the two-line bullet. The parsed output only contains the first line.

### Expected
`"• Utilized Latest technology in Next library to improve a web application with 15 percent visual inhancement and 10 percent page loading."`

### Impact
A metric ("10 percent page loading") is lost from the structured output. `quality_analyzer.has_metrics` may undercount quantified achievements for this experience entry.

### Likely Area
`src/parsers/experience_parser.py` — non-bullet continuation lines in experience descriptions are not appended to the previous bullet (same root as R-004).

### Status
- **Status:** FIXED
- **Fixed in:** Phase 4.5 Day 1 (commit `e72a322`)
- **Validation:** Unit tests in `test_experience_parser.py` and integration in `process_resume` (`tests/services/test_resume_service.py`). Gosotek first bullet verified to contain `"10 percent page loading."`.
- **Relevant test:** `tests/parsers/test_experience_parser.py`, `tests/services/test_resume_service.py`
- **Notes:** Concrete instance of R-004; fully resolved and verified.

---

## R-009: Multi-page PDF breaks project descriptions — wrapped lines on page boundary become phantom project titles

- **Source:** `resume_without_experience.pdf`
- **Category:** Incorrect Extraction
- **Severity:** P0

### Observed
`resume_without_experience.pdf` spans multiple pages. When a bullet point line wraps across a page boundary, the continuation text on the next page starts at the top without a bullet character. The `_is_project_title()` function returns `True` for any non-empty, non-lowercase-starting, non-bullet, non-period-ending line — so continuation text is misidentified as a new project title.

Observed output:
```json
{"project": "HTML, CSS", "metadata": [], "description": []},
{"project": "CSS", "metadata": [], "description": []}
```
These are continuation fragments of "Tools and Technologies used: ReactJS, Node.js, Express.js, MongoDB, JavaScript, HTML, CSS" that wrapped across page boundaries. `HTML, CSS` and `CSS` are being treated as project names.

### Source Evidence
From text blocks of `resume_without_experience.pdf`:
```python
{'text': '• Tools and Technologies used : ReactJS, Node.js, Express.js, MongoDB, JavaScript,', ...page: 0}
{'text': 'HTML, CSS', ...page: 1}  # ← continuation, misidentified as project title
```
The actual source shows this is a single bullet continued across the page break.

### Expected
Cross-page text-block continuations should be joined to the previous line, not treated as new project titles. At minimum, `_is_project_title()` should require that potential titles don't consist solely of comma-separated word fragments.

### Impact
- Phantom project entries `"HTML, CSS"` and `"CSS"` appear in the parsed output.
- The bullet text for `Bloger` is incomplete — `JavaScript, HTML, CSS` is missing from the description.
- `quality_analyzer` counts these phantom projects and reports misleading `bullet_count` and `content_length`.
- Completeness check sees more projects than actually exist.

### Likely Area
`src/parsers/project_parser.py` — `_is_project_title()` in `src/utils/text_utils.py` (line 18). It has no heuristics to distinguish a real title from a wrapped line fragment.

### Status
- **Status:** PARTIAL
- **Fixed in:** Phase 4.5 Day 1 (commit `e72a322`)
- **Validation:** `HTML, CSS` phantom project eliminated via comma check in `_is_project_title` and page change detection in `_extract_projects`.
- **Relevant test:** `tests/parsers/test_project_parser.py`
- **Notes:** `CSS` phantom project still persists in `resume_without_experience.pdf` because single-token lines on the same page without commas still pass `_is_project_title("CSS")`.

---

## R-010: Skills parser only extracts from the first skills section encountered — stops at any `SECTION_HEADERS` keyword

- **Source:** `HARSHIT_WEBDEV.pdf`, `resume_without_experience.pdf`
- **Category:** Generalization
- **Severity:** P2

### Observed
The skills parser breaks as soon as it encounters ANY entry from `SECTION_HEADERS` after entering the skills section:

```python
if contains_keywords(line, SECTION_HEADERS):
    break
```

`SECTION_HEADERS` includes `ACHIEVEMENTS`. In both test resumes, `ACHIEVEMENTS` follows `TECHNICAL SKILLS`. This works correctly here. However, if a resume has multiple skills sections (e.g., `TECHNICAL SKILLS` and `SOFT SKILLS` as separate sections), only the first one is captured. The second section, if preceded by something in `SECTION_HEADERS`, would be skipped.

Additionally, the `contains_keywords` check for the SKILL header (`SKILLS`, `TECHNICAL SKILLS`, `TECHNICAL SKILLS :`) is highly specific. Alternatives like `CORE COMPETENCIES`, `TOOLS & TECHNOLOGIES`, `TECHNOLOGIES`, or `KEY SKILLS` are not recognized.

### Source Evidence
From `SECTION_HEADERS`:
```python
SKILL = ["SKILLS", "TECHNICAL SKILLS", "TECHNICAL SKILLS :"]
```
Resumes using `KEY SKILLS`, `CORE COMPETENCIES`, `TECHNOLOGIES`, `LANGUAGES & FRAMEWORKS`, etc. would have no skills extracted.

### Expected
Skills section headers should include common variants. If multiple skill sections exist, all should be captured.

### Impact
Any resume not using one of three exact header phrases has skills = `None`. Completeness check marks `skills` as missing, scoring and matching produce zero skill overlap.

### Likely Area
`src/configs/header_configs.py` — `SKILL` list. `src/parsers/skills_parser.py` — single-section extraction logic.

### Status
- **Status:** FIXED
- **Fixed in:** Phase 4.5 Day 3 (Section-Aware Architecture)
- **Validation:** `detect_sections` extracts all skills sections (including aliases like `TECHNICAL SKILLS` and `NON TECHNICAL SKILLS`), groups them into canonical `"skills"`, and `resume_service.py` concatenates their content before passing to `skills_parser.py`. Furthermore, `skills_parser.py` was refactored to parse isolated text without stopping at `SECTION_HEADERS`. Verified on `R09_Multiple_Skills_Sections.pdf`.
- **Relevant test:** `tests/parsers/test_section_detector.py`, `tests/parsers/test_skills_parser.py`, `tests/services/test_resume_service.py`
- **Notes:** Section detector handles top-level boundaries; skills parser operates on isolated skills section content.

---

## R-011: Education section header only recognizes exact `EDUCATION` — misses common variants

- **Source:** Generalization
- **Category:** Generalization
- **Severity:** P2

### Observed
```python
EDUCATION_SECTION_HEADERS = ["EDUCATION"]
```
`contains_keywords` checks if `"EDUCATION"` is contained in the uppercased line. This means `EDUCATIONAL BACKGROUND`, `ACADEMIC QUALIFICATIONS`, `ACADEMIC BACKGROUND`, `ACADEMICS`, `DEGREES` are all missed.

However, because `contains_keywords` uses substring matching (`keyword.upper() in line`), `EDUCATIONAL BACKGROUND` would actually match since it contains `EDUCATION`. But `ACADEMICS`, `ACADEMIC QUALIFICATIONS`, `DEGREES` would not.

### Source Evidence
Common real-world alternatives not covered: `ACADEMIC BACKGROUND`, `ACADEMIC QUALIFICATIONS`, `ACADEMICS`, `DEGREES`, `SCHOOLING`.

### Expected
Education section headers should include common variants.

### Impact
Education section is not parsed for resumes using non-standard section headers. `completeness_analyzer` marks `education` as missing.

### Likely Area
`src/configs/header_configs.py` — `EDUCATION_SECTION_HEADERS`.

### Status
OPEN

---

## R-012: Experience section only triggered by exact `EXPERIENCE` — misses `WORK EXPERIENCE`, `PROFESSIONAL EXPERIENCE`, `EMPLOYMENT`, `INTERNSHIP`

- **Source:** Generalization
- **Category:** Generalization
- **Severity:** P2

### Observed
```python
EXPERIENCE_HEADERS = ['EXPERIENCE']
```

`contains_keywords` uses substring matching, so `WORK EXPERIENCE`, `PROFESSIONAL EXPERIENCE`, `INDUSTRY EXPERIENCE` would all match because they contain `EXPERIENCE`. However, labels like `EMPLOYMENT HISTORY`, `INTERNSHIP`, `WORK HISTORY`, `CAREER HISTORY` would not.

Verified:
```
contains_keywords('Internship Experience', EXPERIENCE_HEADERS) => True  (contains 'EXPERIENCE')
contains_keywords('WORK EXPERIENCE', EXPERIENCE_HEADERS) => True
```
But `EMPLOYMENT HISTORY` → `False`. `INTERNSHIP` → `False`.

### Source Evidence
Common variants not matched: `EMPLOYMENT`, `EMPLOYMENT HISTORY`, `WORK HISTORY`, `CAREER HISTORY`, `INTERNSHIP`.

### Expected
Experience headers should cover `EMPLOYMENT`, `EMPLOYMENT HISTORY`, `WORK HISTORY`, `CAREER HISTORY`, `INTERNSHIP`.

### Impact
Experience section is not parsed for resumes using non-matching headers.

### Likely Area
`src/configs/header_configs.py` — `EXPERIENCE_HEADERS`.

### Status
OPEN

---

## R-013: `quality_analyzer` crashes with `TypeError` if `start_year` or `end_year` is `None` in education or experience entries

- **Source:** Generalization
- **Category:** Incorrect Extraction
- **Severity:** P1

### Observed
`_analyze_education_consistency()` (line 152) and `_analyze_experience_consistency()` (line 164) do:

```python
if entry["start_year"] > entry["end_year"]:
```

If either `start_year` or `end_year` is `None` (which happens when duration cannot be parsed, or only one year is found), this comparison raises:
```
TypeError: '>' not supported between instances of 'NoneType' and 'NoneType'
```

### Source Evidence
When education or experience entries have unparseable dates (e.g., `"2023 - Present"` produces `end_year=None`), or when `_normalize_duration` returns `(None, None, None, None)`, the quality analyzer will raise a `TypeError` at comparison time.

### Expected
Null-checks should guard comparisons: `if entry["start_year"] is not None and entry["end_year"] is not None and entry["start_year"] > entry["end_year"]`.

### Impact
Any resume with a currently-employed experience ("`Present`") or an education entry without a parseable end year will cause the entire resume processing to crash with an unhandled exception.

### Likely Area
`src/analyzers/quality_analyzer.py` — `_analyze_education_consistency()` line 152 and `_analyze_experience_consistency()` line 164.

### Status
- **Status:** FIXED
- **Fixed in:** Phase 3 / Phase 4.5 Day 3
- **Validation:** `src/analyzers/quality_analyzer.py` lines 255-257 and 282-284 guard comparisons with `start_year is not None and end_year is not None and start_year > end_year`. Null values safely evaluate without TypeError.
- **Relevant test:** `tests/analyzers/test_quality_analyzers.py::test_education_consistency_valid_duration`, `test_education_consistency_invalid_duration`.
- **Notes:** Null-checks in place prevent crashes when start_year or end_year is None.

---

## R-014: `ACHIEVEMENTS` section content is completely discarded — not extracted or schema-represented

- **Source:** `HARSHIT_WEBDEV.pdf`, `resume_without_experience.pdf`
- **Category:** Information Loss / Schema Limitation
- **Severity:** P1

### Observed
Both resumes contain an `ACHIEVEMENTS` section with meaningful content:
```
ACHIEVEMENTS :
• JEE Mains Rank Holder : Ranked among the Top 2.1 percentile out of 1.2 million students in the JEE Mains examination, 2020.
• Gold Medal in Sports Event : Ranked first in the Inter-Branch Physical Strength competition at Sports Fest 2022, NIT-A.
```

There is no `achievements` field in `resume_data` in `resume_service.py` and no parser for this section. The achievements are present in the raw `text` field but are not structured.

### Source Evidence
Source document lines 60-64 (HARSHIT_WEBDEV.txt):
```
ACHIEVEMENTS :
• JEE Mains Rank Holder : ...
• Gold Medal in Sports Event : ...
```

Output: no `achievements` key in the structured response.

### Expected
An `achievements` field (list of strings) should be populated in the output, structured the same way as experience `description`.

### Impact
Achievements — often the most differentiating section for early-career candidates — are entirely lost from the structured output. They cannot be used for ATS matching, scoring, or display. This is particularly impactful since both test resumes are early-career and achievements may substitute for limited experience.

### Likely Area
`src/services/resume_service.py` — no achievements parser is called. `src/schemas/resume.py` — no achievements field in schema. No `src/parsers/achievements_parser.py` exists.

### Status
OPEN

---

## R-015: `CERTIFICATIONS` and `PUBLICATIONS` section headers in `SECTION_HEADERS` — but no parsers exist for them

- **Source:** Generalization
- **Category:** Schema Limitation
- **Severity:** P2

### Observed
```python
SECTION_HEADERS = ['EDUCATION', 'EXPERIENCE', 'PROJECTS', 'ACHIEVEMENTS', 'CERTIFICATIONS', 'PUBLICATIONS', ...]
```

`CERTIFICATIONS` and `PUBLICATIONS` are listed as known section headers (used to stop other parsers from over-running), but there is no parser, normalizer, or output field for either section. Content in these sections is not extracted.

### Source Evidence
The headers are declared in `header_configs.py` lines 6-7. No `certifications_parser.py` or `publications_parser.py` exists.

### Expected
Either parsers should exist for these sections, or the sections should be documented as planned-but-not-implemented. If skipped intentionally, their content should at least be preserved as raw text.

### Impact
Certifications (e.g., AWS Certified Solutions Architect, Google Cloud Professional) are common, high-value signals for technical job matching. Publications matter for research/data science roles. Both are lost.

### Likely Area
`src/parsers/` — no certifications or publications parser. `src/services/resume_service.py` — neither section is processed.

### Status
OPEN

---

## R-016: Summary/Profile/Objective section not extracted

- **Source:** Generalization
- **Category:** Schema Limitation
- **Severity:** P2

### Observed
Neither test resume has a summary section. However, the resume service has no parser, no schema field, and no recognition for sections commonly titled `SUMMARY`, `PROFILE`, `OBJECTIVE`, `ABOUT`, `PROFESSIONAL SUMMARY`, or `CAREER OBJECTIVE`.

### Source Evidence
The `SECTION_HEADERS` list and `header_configs.py` do not contain `SUMMARY`, `PROFILE`, or `OBJECTIVE`. The `resume_data` dict has no summary field.

### Expected
A `summary` field should be extracted if present, as profile summaries are a primary signal for candidate-role fit.

### Impact
Profile summaries — which often contain the candidate's specialization, years of experience, and key skills in narrative form — are completely lost. This affects semantic matching quality.

### Likely Area
`src/parsers/` — no summary parser. `src/services/resume_service.py`.

### Status
OPEN

---

## R-017: Skills normalizer does not deduplicate after alias resolution across mixed-case inputs from skills parser

- **Source:** `HARSHIT_WEBDEV.pdf`, `resume_without_experience.pdf`
- **Category:** Incorrect Extraction
- **Severity:** P2

### Observed
The skills parser extracts `ReactJS` from the raw text. After normalization, it becomes `React`. The KNOWN_SKILLS list in `skill_configs.py` includes `React`. If the same resume also has `React` in a skills line (e.g., via `Contains_keywords` matching), both would be normalized to `React` — but `skill_normalizer` uses a `not in` check to prevent exact duplicates:

```python
if canonical_skill not in normalized_skills:
    normalized_skills.append(canonical_skill)
```

This works for exact matches. However, the skills parser returns `ReactJS` (from line `ReactJS, Express.JS, Next.JS`), which normalizes to `React`. If another line also has `ReactJS`, it would be normalized to `React` but already be in the list — so deduplication works. The issue is that `Git` and `GitHub` are both extracted as separate skills (both present in source: `Git, GitHub`) and both kept as separate entries:

```json
["Git", "GitHub"]
```

`GitHub` is not in `SKILL_ALIASES` or `KNOWN_SKILLS` but is extracted as a raw skill. It is not normalized or merged with `Git`. These are distinct tools, but the lack of a semantic layer means `GitHub` is kept as a raw string without normalization.

Also: `Back-end Web Development` in `resume_without_experience.pdf` was extracted as `Back-end` (truncated) due to line wrapping:
```
• Technologies : Front-End Web Development, Test-Driven Development, Back-end
Web Development
```
The line wraps mid-skill-value, and the skills parser only reads the first part (`Back-end`), dropping ` Web Development` from the value.

### Source Evidence
Normalized skills from `resume_without_experience.pdf`:
```json
"Back-end"  ← should be "Back-end Web Development"
```
vs `HARSHIT_WEBDEV.pdf`:
```json
"Back-end Web Development"  ← correct
```

### Expected
The skills parser should handle values that wrap to the next line within the same bullet. `skill_normalizer` should preserve the full normalized value.

### Impact
`Back-end Web Development` is a different skill token than `Back-end`. In skill matching, these would not match, causing false negatives when comparing to a JD that requires `Back-end Web Development`.

### Likely Area
`src/parsers/skills_parser.py` — line-by-line processing loses multi-line skill values. `src/normalizers/skill_normalizer.py` — no handling for truncated skill fragments.

### Status
OPEN

---

## R-018: Contact info icon/glyph characters from PDF decorators leak into cleaned text and are not stripped

- **Source:** `HARSHIT_WEBDEV.pdf`
- **Category:** Incorrect Extraction
- **Severity:** P3

### Observed
The raw extracted text from `HARSHIT_WEBDEV.pdf` contains icon characters used as decorators for contact info:
```
'ABHINAV PRATAP SINGH\n\x83 +91 9774913812\n# apsbqt@gmail.com\nï Abhinav Pratap Singh\nï  Blockmecoder\n'
```

After `clean_text()`, these remain:
```
 +91 9774913812
# apsbqt@gmail.com
ï Abhinav Pratap Singh
§ Blockmecoder
```

Characters like `ï`, `§`, `#`, and the leading space on the phone line are icon substitution artifacts from PDF font glyph misinterpretation. `clean_text()` only strips tabs, carriage returns, and multiple spaces/newlines.

### Source Evidence
Raw text repr: `'\x83 +91 9774913812\n# apsbqt@gmail.com\nï Abhinav Pratap Singh\nï  Blockmecoder\n'`

The `#` before the email, `ï` before the LinkedIn name, `§` before the GitHub handle — all are icon-glyph artifacts.

### Expected
`clean_text()` should strip or replace known font-icon/glyph characters (or at least warn). Ideally, contact section detection should be icon-agnostic.

### Impact
If the phone line starts with `\x83 ` or `# `, the `extract_phone` regex matches because it searches the whole text — it finds the number anywhere. But the email regex would match despite the `#` prefix. The name parser is affected most: if `\x83 +91 9774913812` appears as the first non-empty line in edge cases, name extraction fails (see R-003). Also, raw `ï` and `§` characters in `cleaned_text` are stored in the `text` field of the response.

### Likely Area
`src/parsers/text_parser.py` — `clean_text()`. No stripping of non-ASCII control/icon characters.

### Status
OPEN

---

## R-019: `total_experience_months` off-by-one: calculation adds +1 to every interval month count

- **Source:** `HARSHIT_WEBDEV.pdf`
- **Category:** Incorrect Extraction
- **Severity:** P2

### Observed
For the Gosotek internship: January 2024 – February 2024.
```
start: (2024, 1), end: (2024, 2)
months = (2 - 1) + (2024 - 2024) * 12 + 1 = 1 + 0 + 1 = 2
```
The output is `total_experience_months: 2`.

January to February is 1 month (or 2 months inclusive). The `+1` in `_calculate_months` makes it inclusive: Jan and Feb count as 2 months. This is a design choice, but the +1 is applied uniformly to every interval, which means a single-month tenure (Jan–Jan) would be counted as 1 month (0 + 0 + 1 = 1), and a 12-month tenure (Jan–Dec, same year) would be 12 + 0 + 1 = 13.

The same +1 is present in `skill_experience_analyzer._calculate_months`.

### Source Evidence
`total_experience_months: 2` for a January–February internship. January to February can be interpreted as 1 calendar month apart or 2 months inclusive. The `+1` makes it consistently inclusive-counting, but this may not match industry standard (months worked = end month index − start month index).

### Expected
Clarify the intended semantics. If inclusive counting is intended, document it. If exclusive (months worked), remove the `+1`. Inconsistency could affect experience requirements matching (e.g., 36-month requirement for a 35-month candidate could pass or fail incorrectly).

### Impact
Every experience duration is potentially overcounted by 1 month. For candidates with multiple short tenures, the overcounting is compounded.

### Likely Area
`src/normalizers/experience_normalizer.py` — `_calculate_months()` line 61. `src/analyzers/skill_experience_analyzer.py` — `_calculate_months()` line 79.

### Status
OPEN

---

## R-020: HARSHIT_WEBDEV.pdf resume data contains duplicate name (appears twice in raw text as `ï Abhinav Pratap Singh`)

- **Source:** `HARSHIT_WEBDEV.pdf`
- **Category:** Other
- **Severity:** P4

### Observed
The raw PDF extraction produces the name twice:
```
ABHINAV PRATAP SINGH       ← header text
...
ï Abhinav Pratap Singh     ← LinkedIn display name artifact
```

The name parser returns the first non-empty line, so it returns `ABHINAV PRATAP SINGH` (transformed to title case by `.title()`). The second occurrence is not used. However, the LinkedIn display name artifact `ï Abhinav Pratap Singh` remains in the cleaned text and would confuse any downstream text search.

### Source Evidence
Raw text line 4: `ï Abhinav Pratap Singh` (the LinkedIn profile name extracted as a text layer character run).

### Expected
This is a known artifact of PDF hyperlink annotation text. While not a parser bug per se, the presence of icon characters followed by the name being re-extracted is worth noting for downstream text searches.

### Impact
Minor: name is correctly extracted. Downstream text analysis sees the name twice, which could affect TF-IDF or similarity scores.

### Likely Area
`src/parsers/pdf_parser.py` — `extract_text()` extracts all text layers including hyperlink annotations.

### Status
OPEN

---

## R-021: Education degree parsing fails for degrees not matching `DEGREE_KEYWORDS` — falls back to raw line

- **Source:** `HARSHIT_WEBDEV.pdf`, `resume_without_experience.pdf`
- **Category:** Generalization
- **Severity:** P2

### Observed
For `Senior Secondary (XII)` and `Secondary (X)`, `contains_keywords(line, DEGREE_KEYWORDS)` returns `True` because `XII` and `X` are in `DEGREE_KEYWORDS`:
```python
DEGREE_KEYWORDS = [..., 'X', 'XII', '12TH', '10TH']
```

However, the degree normalizer does NOT recognize `Senior Secondary (XII)` — `normalize_degree()` checks `degree_lower.startswith(alias)` against `DEGREE_ALIASES`. `DEGREE_ALIASES` has no entry for `senior secondary`, `secondary`, `x`, or `xii`. So `normalize_degree` falls back to returning the raw string:
```json
"degree": "Senior Secondary (XII)"   ← not normalized
"degree": "Secondary (X)"            ← not normalized
"field": null
```

This is inconsistent with the B.Tech entry which is properly normalized to `"B.Tech"` with `"field": "Electronics and Communication Engineering"`.

### Source Evidence
```json
{"degree": "B.Tech", "field": "Electronics and Communication Engineering"}   // ← normalized
{"degree": "Senior Secondary (XII)", "field": null}                          // ← not normalized
{"degree": "Secondary (X)", "field": null}                                   // ← not normalized
```

### Expected
`DEGREE_ALIASES` should include entries for `senior secondary (xii)`, `secondary (x)`, `higher secondary`, `ssc`, `hsc`, `10th`, `12th`, etc.

### Impact
Degree field is inconsistently normalized across entries within the same document. Downstream matching cannot reliably compare degree types.

### Likely Area
`src/configs/normalization_configs.py` — `DEGREE_ALIASES`. `src/normalizers/education_normalizer.py` — `normalize_degree()`.

### Status
OPEN

---

## Audit Summary — Resume Parser

| | |
|---|---|
| **Documents tested** | 2 (`HARSHIT_WEBDEV.pdf`, `resume_without_experience.pdf`) |
| **Unique issues found** | 21 |

### Issues by Severity

| Severity | Count | IDs |
|---|---|---|
| P0 | 3 | R-001, R-002, R-009 |
| P1 | 8 | R-003, R-004, R-005, R-006, R-007, R-008, R-013, R-014 |
| P2 | 8 | R-010, R-011, R-012, R-015, R-016, R-017, R-019, R-021 |
| P3 | 1 | R-018 |
| P4 | 1 | R-020 |

### Top 5 Highest-Priority Issues

1. **R-009 (P0)** — Multi-page PDF creates phantom project entries (`HTML, CSS`, `CSS`) — ~~`HTML, CSS` fixed~~, `CSS` phantom project still persists.
2. **R-002 (P0)** — LinkedIn URL extracted but hard-coded as `None` — confirmed information loss in `HARSHIT_WEBDEV.pdf`.
3. ~~**R-001 (P0)** — Skills parser drops all skills when lines lack a colon — generalization failure.~~ (FIXED in commit `e72a322`)
4. **R-013 (P1)** — `quality_analyzer` crashes with `TypeError` when `start_year`/`end_year` is `None`.
5. **R-014 (P1)** — `ACHIEVEMENTS` section not extracted from either test document — confirmed information loss.

---

# Parser Generalization Audit

Independent generalization audit across 3 distinct resume formats:
1. `HARSHIT_WEBDEV.pdf` (Reference format: categorized technical skills, project titles with `| GitHub` links, standard single-job experience)
2. `Resume - Aditya Saha.pdf` (Alternative format: degree/institution variation, ongoing job with "Present", multi-line project blocks with duration and preview links, conjunction-separated skills, academic achievements & interests)
3. `Abhinav_ML_Resume.pdf` (ML resume format: single-line role+company+location, "Technologies" header instead of "Skills", combined institution+degree lines, certifications section with credential links, projects without metadata)

---

### Strengthened Existing Issues

ID: R-002
Priority: P0
Resume: `HARSHIT_WEBDEV.pdf`, `Resume - Aditya Saha.pdf`, `Abhinav_ML_Resume.pdf`
Component: Resume Service (`resume_service.py`)
Category: Information Loss

Observed behavior:
LinkedIn URLs are successfully extracted from PDF hyperlink annotations by `extract_links()` in all 3 resumes, but `process_resume()` unconditionally sets `"linkedin": None` on line 69 of `src/services/resume_service.py`.

Expected behavior:
Extracted links should be inspected for LinkedIn URLs (or regex matching against header text) and assigned to the `"linkedin"` field.

Evidence:
- `HARSHIT_WEBDEV.pdf`: `https://www.linkedin.com/in/abhinav-pratap-singh-1a8a57200/` extracted from annotation; output has `"linkedin": null`.
- `Resume - Aditya Saha.pdf`: `https://www.linkedin.com/in/adityasaha39/` extracted from annotation; output has `"linkedin": null`.
- `Abhinav_ML_Resume.pdf`: `https://www.linkedin.com/in/abhinav-pratap-singh-1a8a57200?...` extracted from annotation; output has `"linkedin": null`.
In all 3 cases, `completeness_analyzer` flags `"missing_recommended": ["linkedin"]`.

Impact:
100% of tested resumes with valid LinkedIn profiles lose their LinkedIn URLs, corrupting ATS candidate records and downstream enrichment.

Root cause:
Hard-coded `"linkedin": None` in `resume_service.py`.

Existing issue:
Strengthens R-002 (confirmed universal across all 3 resumes).

Recommended direction:
Filter `links` list for `linkedin.com` domains in `resume_service.py` and populate the field before running analyzers.

---

ID: R-005
Priority: P1
Resume: `Abhinav_ML_Resume.pdf`
Component: Experience Parser (`experience_parser.py`)
Category: Incorrect Extraction / Entity Association

Observed behavior:
In `_parse_experience`, when a duration line is encountered, the parser unconditionally assumes `experience["company"] = block[i-1]`. On resumes where role, company, and location are combined on the previous line (`Machine Learning Engineer, LTTS – Mysore, KA`), the entire string becomes the company name.

Expected behavior:
The parser should recognize composite lines containing role and company, and segment them instead of assuming line `i-1` is purely the company name.

Evidence:
In `Abhinav_ML_Resume.pdf`:
Line 14: `Machine Learning Engineer, LTTS – Mysore, KA`
Line 15: `Sept 2024 – Present`
Parsed output:
`"company": "Machine Learning Engineer, LTTS – Mysore, KA"`

Impact:
Company name contains role and location, distorting company matching, entity resolution, and company-specific experience calculation.

Root cause:
Rigid positional assumption `experience["company"] = block[i-1]` without line decomposition.

Existing issue:
Strengthens R-005.

Recommended direction:
Implement line-level decomposition (e.g. splitting on commas, dashes, or pipes) to extract role, company, and location entities independently.

---

ID: R-006
Priority: P1
Resume: `Resume - Aditya Saha.pdf`, `Abhinav_ML_Resume.pdf`
Component: Text Utils / Normalizers (`text_utils.py`, `experience_normalizer.py`, `education_normalizer.py`)
Category: Information Loss / Date Handling

Observed behavior:
`DURATION_PATTERNS` in `text_utils_configs.py` does not match `Month YYYY - Month YYYY` (e.g. `Jul 2017 - Mar 2019`, `Jun 2022 - Jul 2022`). Furthermore, `_normalize_duration` in `experience_normalizer.py` fails to recognize "Present" as an active duration marker.

Expected behavior:
`is_duration()` should recognize all standard month-year range formats. `_normalize_duration()` should resolve "Present" to the current month and year.

Evidence:
- `Resume - Aditya Saha.pdf`: Education entry `Jul 2017 - Mar 2019` fails `is_duration()`, resulting in `duration: null` and `start_year: null, end_year: null`.
- `Resume - Aditya Saha.pdf`: Experience entry `May 2022 - Present` yields `start_month: "May", end_month: null, start_year: 2022, end_year: null`. `calculate_total_experience()` evaluates to `0` months.
- `Abhinav_ML_Resume.pdf`: Experience entry `Sept 2024 – Present` yields `start_month: null, end_month: null, start_year: 2024, end_year: null`. `calculate_total_experience()` evaluates to `0` months.

Impact:
Candidates currently working have 0 months of calculated experience. Education durations are lost, triggering `missing_start_year` and `missing_end_year` quality alerts.

Root cause:
Pattern 2 in `DURATION_PATTERNS` only expects `Month - Month, Year` (e.g. `January - February, 2024`), failing on dual-year strings. Normalizers do not map "Present" to current date.

Existing issue:
Strengthens R-006.

Recommended direction:
Expand `DURATION_PATTERNS` to cover `(?:Jan|Feb|...)\s+\d{4}\s*[-–]\s*(?:(?:Jan|Feb|...)\s+\d{4}|Present)`. Support "Present" mapping in normalizers.

---

ID: R-007
Priority: P1
Resume: `HARSHIT_WEBDEV.pdf`
Component: Project Parser (`project_parser.py`)
Category: Incorrect Normalization

Observed behavior:
Project titles retaining trailing delimiter metadata such as `| GitHub` or `| LIVE` are stored verbatim without stripping the suffix.

Expected behavior:
Project names should be cleaned of repository or host link suffixes.

Evidence:
`HARSHIT_WEBDEV.pdf`:
`"project": "Bloger - A Full Stack Blog App | GitHub"`
`"project": "Weather Sphere - A Real-time Weather App | GitHub"`
`"project": "PrompTopic - An AI Prompting Tool | GitHub"`

Impact:
Pollutes project entity names in matching algorithms, database storage, and UI presentation.

Root cause:
`_parse_projects` sets `project["project"] = text` without stripping trailing delimiters.

Existing issue:
Strengthens R-007.

Recommended direction:
Clean project title string using delimiter splitting (`|`, `- GitHub`, `(GitHub)`).

---

ID: R-009
Priority: P0
Resume: `Resume - Aditya Saha.pdf`
Component: Project Parser (`project_parser.py`, `text_utils.py`)
Category: Project Boundary Detection

Observed behavior:
Single-line duration strings inside project sections that lack commas (e.g. `Jun 2022 - Jul 2022`, `Dec 2021 - Jan 2022`, `Nov 2021 - Dec 2021`) pass `_is_project_title()` and are instantiated as separate project objects.

Expected behavior:
Duration strings must be recognized as project metadata or duration attributes of the preceding project, never as new project entities.

Evidence:
In `Resume - Aditya Saha.pdf`:
Raw projects: 3 real projects (`COURSEJAM`, `VSTREAM`, `ADMIN UI`).
Parsed output: 6 project entities:
- Project 0: `"COURSEJAM - An E-Commerece Website"` (empty description, empty metadata)
- Project 1: `"Jun 2022 - Jul 2022"` (contains all description bullets and preview links)
- Project 2: `"VSTREAM - A clone like video streaming"` (empty description, empty metadata)
- Project 3: `"Dec 2021 - Jan 2022"` (contains all description bullets and preview links)
- Project 4: `"ADMIN UI"` (empty description, empty metadata)
- Project 5: `"Nov 2021 - Dec 2021"` (contains all description bullets and preview links)

Impact:
Severe structural corruption: every project is split into an empty ghost shell and an anonymous duration title. Project title search, keyword matching, and bullet counts are invalid.

Root cause:
`_is_project_title()` only rejects lines starting with lowercase, ending in '.', starting with bullets, or containing commas. `Jun 2022 - Jul 2022` satisfies all conditions and is treated as a title.

Existing issue:
Strengthens R-009 (demonstrates that phantom project generation occurs on single-page resumes via duration lines, not just multi-page boundaries).

Recommended direction:
Check `is_duration(line)` before `_is_project_title(line)`, and associate duration with the current active project.

---

ID: R-014
Priority: P1
Resume: `HARSHIT_WEBDEV.pdf`, `Resume - Aditya Saha.pdf`
Component: Section Detection / Schemas
Category: Information Loss

Observed behavior:
`ACHIEVEMENTS` and `ACADEMIC ACHIEVEMENTS` sections are detected as stopping boundaries for prior sections, but their content is completely dropped.

Expected behavior:
Achievement entries and associated URLs (e.g. LeetCode, HackerRank, contest rankings) should be extracted and represented in the candidate schema.

Evidence:
- `HARSHIT_WEBDEV.pdf`: JEE Mains Rank Holder and Sports Event medals are discarded.
- `Resume - Aditya Saha.pdf`: 5 achievement bullets containing LeetCode, Geektrust, HackerRank test links and Codathon rank 469 are discarded.

Impact:
High-signal competitive programming, academic rank, and certification achievements are lost to downstream ranking.

Root cause:
No achievement parser exists, and `resume_data` schema has no `achievements` field.

Existing issue:
Strengthens R-014.

Recommended direction:
Add an `achievements` parser and incorporate an `achievements` array into the resume schema.

---

ID: R-015
Priority: P1
Resume: `Abhinav_ML_Resume.pdf`
Component: Section Detection / Parsers
Category: Information Loss

Observed behavior:
`CERTIFICATIONS` section stops the experience parser, but its entries (`Python for Data Science` by IBM, `Discover data analysis` by Microsoft) and associated Credly / Microsoft verification links are discarded.

Expected behavior:
Certifications should be extracted with title, issuing organization, and verification URL.

Evidence:
`Abhinav_ML_Resume.pdf`:
Lines 22-28 contain two certifications with clickable links (`https://www.credly.com/badges/...`, `https://learn.microsoft.com/api/...`). Both are absent from output.

Impact:
Verified candidate credentials and licenses are invisible to recruiters and matching engines.

Root cause:
No parser exists for the `CERTIFICATIONS` section.

Existing issue:
Strengthens R-015.

Recommended direction:
Implement a `certifications_parser.py` and extract credential links from `links`.

---

ID: R-018
Priority: P3
Resume: `HARSHIT_WEBDEV.pdf`, `Resume - Aditya Saha.pdf`, `Abhinav_ML_Resume.pdf`
Component: Text Parser (`text_parser.py`)
Category: Noise / Glyphs

Observed behavior:
PDF decorative font icon glyphs (e.g. `ƒ`, `#`, `ï`, `§`, `‡`, `°`, `>`, `Ó`) leak into the cleaned text and contaminate downstream lines.

Expected behavior:
Icon font artifacts and non-standard symbols in contact blocks should be cleaned during text normalization.

Evidence:
- `HARSHIT_WEBDEV.pdf`: `ƒ +91 9774913812`, `# apsbqt@gmail.com`, `ï Abhinav Pratap Singh`, `§ Blockmecoder`
- `Resume - Aditya Saha.pdf`: `‡ github.com/adityasaha39 | ° linkedin.com/in/adityasaha39 | > aditya.saha2017@gmail.com | Ó +91-8787679905`
- `Abhinav_ML_Resume.pdf`: `# harshitsinghtil@gmail.com | ƒ 7726850107 | § Blockmecoder | ï Abhinav Pratap Singh`

Impact:
Creates noise in raw text, risks breaking header parsers, and leaks raw character artifacts into stored profile representations.

Root cause:
`clean_text()` only replaces tabs, carriage returns, and multiple whitespace/newlines; it performs no glyph stripping.

Existing issue:
Strengthens R-018.

Recommended direction:
Add regex sanitization for common font-awesome/private-use Unicode icon code points.

---

ID: R-021
Priority: P2
Resume: `Resume - Aditya Saha.pdf`
Component: Education Normalizer (`education_normalizer.py`)
Category: Incorrect Normalization

Observed behavior:
When degree text uses the plural form `Bachelors of Technology`, `normalize_degree()` fails to match `DEGREE_ALIASES` and falls back to returning the entire raw string with `field: null`.

Expected behavior:
Plural degree variations (`bachelors`, `masters`) should resolve to canonical forms (`B.Tech`, `M.Tech`) with field of study extracted.

Evidence:
`Resume - Aditya Saha.pdf`:
Raw line: `Bachelors of Technology in Electronics And Communication Engineering`
Parsed output:
`"degree": "Bachelors of Technology in Electronics And Communication Engineering"`, `"field": null`

Impact:
Inability to match candidate degrees against JD requirements expecting canonical `B.Tech` or `Bachelor of Technology`.

Root cause:
`DEGREE_ALIASES` only contains singular `"bachelor of technology"`, not `"bachelors of technology"`.

Existing issue:
Strengthens R-021.

Recommended direction:
Add plural aliases (`bachelors of technology`, `bachelors of science`, `bachelors of engineering`) to `DEGREE_ALIASES`.

---

### New Issues Discovered During Generalization Audit

ID: R-022
Priority: P1
Resume: `Resume - Aditya Saha.pdf`
Component: Skills Parser (`skills_parser.py`)
Category: Information Loss / Generalization

Observed behavior:
Skill lines that separate technologies with the conjunction `" and "` instead of commas or slashes fail candidate extraction. Only 3 skills (`C`, `C++`, `Git`) were recognized out of over 12 skills listed.

Expected behavior:
Candidate skill extractor should tokenize on conjunctions like `" and "` in addition to `[,|/]`.

Evidence:
In `Resume - Aditya Saha.pdf`:
- `Frontend Technology: HTML, CSS and React JS` -> tokenized as `['HTML', 'CSS and React JS']`. `React JS` is lost from known skills.
- `Backend Technology: Node JS and Express JS` -> tokenized as `['Node JS and Express JS']`. `Node.js` and `Express.js` are lost.
- `DataBase: MongoDB and SQL` -> tokenized as `['MongoDB and SQL']`. `SQL` is lost.
- `Tools: Git, Github and Postman` -> tokenized as `['Git', 'Github and Postman']`. `Postman` and `GitHub` are lost.
Result: `known_skills` is only `['C', 'C++', 'Git']`.

Impact:
Over 75% of candidate skills are dropped, destroying resume-to-JD match scoring.

Root cause:
`extract_skill_candidates()` splits strictly with `re.split(r"[,|/]", value)`, ignoring `" and "`.

Existing issue:
New.

Recommended direction:
Update splitting regex to `r"[,|/]|(?:\s+and\s+)"` or post-process unknown candidates by checking for conjunction splitting.

---

ID: R-023
Priority: P0
Resume: `Resume - Aditya Saha.pdf`
Component: Project Parser (`project_parser.py`, `text_utils.py`)
Category: Project Boundary Detection

Observed behavior:
Standalone duration lines following project titles (e.g. `Jun 2022 - Jul 2022`) are misclassified as project titles, creating phantom project records and separating the project title from its description.

Expected behavior:
A line matching a date/duration pattern must be attributed as the date metadata of the current active project, not treated as a new project title.

Evidence:
In `Resume - Aditya Saha.pdf`:
Line 26: `COURSEJAM - An E-Commerece Website`
Line 27: `Jun 2022 - Jul 2022`
Parsed output generates two distinct entries in `projects`:
1. `{"project": "COURSEJAM - An E-Commerece Website", "metadata": [], "description": []}`
2. `{"project": "Jun 2022 - Jul 2022", "metadata": [...], "description": [...]}`

Impact:
Downstream systems see 6 projects instead of 3; the actual project titles have 0 bullets and 0 metrics, while phantom duration titles hold the descriptions. Quality analyzer reports empty descriptions for 50% of projects.

Root cause:
`_is_project_title()` does not test for date/duration patterns before classifying a capitalized line as a project title.

Existing issue:
New (related to R-009, but specific to intra-page duration lines).

Recommended direction:
Integrate a duration check: if `is_duration(line)` is true, attach it to the current project rather than starting a new project block.

---

ID: R-024
Priority: P0
Resume: `Abhinav_ML_Resume.pdf`
Component: Skills Parser / Project Parser (`skills_parser.py`, `project_parser.py`, `header_configs.py`)
Category: Section Detection / Boundary Bleed

Observed behavior:
The resume uses `Technologies` as its skills section header. `Technologies` is not recognized as a skills section header in `header_configs.py` (it is only listed in `SKILL_CATEGORY_HEADERS`). Consequently, `extract_skills()` skips it, extracting 0 skills. Furthermore, because `Technologies` is not in `SECTION_HEADERS`, the preceding `PROJECTS` section fails to terminate and absorbs all technology categories, programming languages, and tools into the description and metadata of the last project (`Mobile Price Range Prediction`).

Expected behavior:
`Technologies` should be recognized as a valid skills section header when appearing as a primary section. `project_parser` should terminate cleanly at `Technologies`.

Evidence:
In `Abhinav_ML_Resume.pdf`:
- `extract_skills()` returns `{"known": [], "unknown": []}`.
- `completeness_analyzer` flags `"missing_required": ["skills"]`.
- `quality_analyzer` flags `"issue": "missing_skills"`.
- `Mobile Price Range Prediction` description contains:
  `"...Technologies Programming Languages: Python, SQL Technologies: Pandas, NumPy, TensorFlow, Seaborn etc."`
- `Mobile Price Range Prediction` metadata contains:
  `"Tools: VS Code, Git, GitHub, G-Colab, Jupyter"`

Impact:
Total failure of skill extraction for resumes using "Technologies". Description corruption of candidate projects.

Root cause:
`SKILL` list in `header_configs.py` only contains `["SKILLS", "TECHNICAL SKILLS", "TECHNICAL SKILLS :"]`. `SECTION_HEADERS` lacks `TECHNOLOGIES`.

Existing issue:
New.

Recommended direction:
Add `TECHNOLOGIES` to `SECTION_HEADERS` and `SKILL` section configurations, ensuring section-level headers take precedence over category headers when appearing as standalone lines.

---

ID: R-025
Priority: P0
Resume: `Abhinav_ML_Resume.pdf`
Component: Experience Parser (`experience_parser.py`)
Category: Incorrect Extraction / Entity Association

Observed behavior:
In `_parse_experience`, if a bullet point in the job description contains a role keyword (such as "engineering" matching `ENGINEER`), the parser mistakes the bullet line for the candidate's job role. It overwrites the true role and removes the bullet point from the description.

Expected behavior:
Bullet lines (starting with `•`, `-`, `*`) must strictly belong to the description and should never be evaluated as candidate job titles.

Evidence:
In `Abhinav_ML_Resume.pdf`:
Candidate's real role: `Machine Learning Engineer, LTTS – Mysore, KA`
Bullet 2 of description: `• Enhanced model accuracy by preprocessing time-series data, performing feature engineering, and optimizing hyperparameters.`
Parsed output:
`"role": "• Enhanced model accuracy by preprocessing time-series data, performing feature engineering, and optimizing"`
The description array in the parsed output only has 2 bullets instead of 3, because bullet 2 was stolen as the role.
In `experience_normalizer`, `"position"` is normalized to this hijacked bullet text.

Impact:
Destroys job title extraction. Candidate's position is recorded as a long sentence fragment, breaking title matching and recruiter displays. Experience description loses critical quantitative content.

Root cause:
In `_parse_experience` (lines 48-57), `if contains_keywords(line, ROLE_KEYWORDS)` is evaluated BEFORE checking `elif line.startswith(("•", "-", "*"))`.

Existing issue:
New.

Recommended direction:
Check for bullet prefixes first (`line.startswith(("•", "-", "*"))`) and immediately append to `description` before running any role keyword checks.

---

ID: R-026
Priority: P1
Resume: `Abhinav_ML_Resume.pdf`
Component: Education Parser (`education_parser.py`)
Category: Information Loss / Entity Association

Observed behavior:
When degree and institution appear on the same line (e.g. `National Institute of Technology, Agartala, Bachelor of Technology in Electronics`), `_parse_education()` assigns the line to `institution` and sets `degree` to `None`.

Expected behavior:
The parser should recognize when a single line contains both an institution keyword and a degree keyword, splitting them into separate entities.

Evidence:
In `Abhinav_ML_Resume.pdf`:
Line 3: `National Institute of Technology, Agartala, Bachelor of Technology in Electronics`
Line 4: `and Communication Engineering`
Parsed output:
- `"institution": "National Institute of Technology, Agartala, Bachelor of Technology in Electronics"`
- `"degree": null`
- `"field": null`
All 3 education entries in this resume result in `"degree": null`.
`quality_analyzer` reports `"missing_degree"` on all education entries.

Impact:
Candidate appears to have no degrees on record. Education matching fails.

Root cause:
In `_parse_education()` (lines 42-45):
```python
if contains_keywords(line, INSTITUTION_KEYWORDS):
    education["institution"] = line
elif contains_keywords(line, DEGREE_KEYWORDS):
    education["degree"] = line
```
Because the line matches `INSTITUTION_KEYWORDS`, the `elif` is never evaluated.

Existing issue:
New.

Recommended direction:
When a line contains both keywords, segment by delimiter (comma, dash) or keyword boundary to extract institution and degree independently.

---

ID: R-027
Priority: P2
Resume: `Resume - Aditya Saha.pdf`
Component: Education Normalizer (`education_normalizer.py`)
Category: Information Loss / Normalization

Observed behavior:
When CGPA is formatted as a fraction with a scale (e.g. `CGPA: 8.67/10.0`), `normalize_education()` fails to convert the score to float, catching `ValueError` silently and leaving `score: None`.

Expected behavior:
The parser should parse fractional grades, extracting the numerator as `score` and the denominator as the grade scale.

Evidence:
In `Resume - Aditya Saha.pdf`:
Line: `CGPA: 8.67/10.0`
`normalize_education()` evaluates `float("8.67/10.0")`, which raises `ValueError`.
Output: `"score": null, "score_type": "CGPA"`.

Impact:
Candidate's 8.67 CGPA is lost from normalized education data.

Root cause:
`normalize_education()` assumes `score.split(":", 1)[-1].strip()` is a bare float.

Existing issue:
New.

Recommended direction:
Extract the float score using regex `r"(\d+(?:\.\d+)?)\s*(?:/\s*(\d+(?:\.\d+)?))?"`.

---

ID: R-028
Priority: P2
Resume: `Abhinav_ML_Resume.pdf`
Component: Education Normalizer (`education_normalizer.py`)
Category: Information Loss / Normalization

Observed behavior:
Education score lines prefixed with bullet markers (e.g. `• CGPA: 8.29` or `• Percentage: 73.80`) fail `score.lower().startswith("cgpa")` check, resulting in `"score_type": None`.

Expected behavior:
Score type detection should strip bullet markers and leading whitespace before inspecting the prefix.

Evidence:
In `Abhinav_ML_Resume.pdf`:
Line: `• CGPA: 8.29` -> `"score": 8.29, "score_type": null`
Line: `• Percentage: 73.80` -> `"score": 73.8, "score_type": null`

Impact:
Downstream consumers cannot determine whether a score is a CGPA or percentage, complicating minimum qualification checks.

Root cause:
`score.lower().startswith("cgpa")` does not strip leading bullet characters (`•`, `-`, `*`).

Existing issue:
New.

Recommended direction:
Strip leading bullets and whitespace: `score.lstrip("•-* \t").lower().startswith("cgpa")`.

---

ID: R-029
Priority: P1
Resume: `Resume - Aditya Saha.pdf`
Component: Project Parser (`project_parser.py`)
Category: Information Loss / Link Association

Observed behavior:
`_parse_projects()` associates hyperlink annotations with a project only if the link bounding box overlaps vertically with `project["_bbox"]` (the project title line). Links placed on subsequent lines (e.g. `Preview :- https://coursejam-aditya.netlify.app`) or plain-text URLs are completely ignored.

Expected behavior:
Links occurring anywhere within the project block's vertical span or appearing as text URLs in metadata lines should be associated with the project.

Evidence:
In `Resume - Aditya Saha.pdf`:
Links exist in PDF annotations for `https://coursejam-aditya.netlify.app/`, `https://github.com/adityasaha39/coursejam`, `https://vstream-aditya.netlify.app/`, etc.
Parsed output in `project_normalizer`:
All metadata items are stored as `type: "text"` with values like `"Preview :- https://coursejam-aditya.netlify.app..."`. No structured `"type": "github"` or `"type": "website"` links are extracted.

Impact:
Candidate project links (GitHub repos, live demos) are lost from structured metadata, breaking candidate portfolio verification.

Root cause:
`_parse_projects()` strictly checks `_boxes_overlap_y(project["_bbox"], link["bbox"])` against only the title line bbox, ignoring all other lines in the project block.

Existing issue:
New.

Recommended direction:
Check link overlap against the bounding box of the entire project block (min Y to max Y), and extract URLs from plain text lines matching URL regexes.

---

ID: R-030
Priority: P1
Resume: `Resume - Aditya Saha.pdf`, `Abhinav_ML_Resume.pdf`
Component: Experience Normalizer (`experience_normalizer.py`)
Category: Calculation Error / Downstream Contract

Observed behavior:
When a candidate is currently employed and their duration ends in `Present` (e.g. `May 2022 - Present`, `Sept 2024 – Present`), `_normalize_duration()` leaves `end_month` and `end_year` as `None`. In `calculate_total_experience()`, the check `if None in (start_month, end_month, start_year, end_year): continue` discards the entire interval, yielding `0` total experience months.

Expected behavior:
"Present" should be normalized to the current calendar month and year so active work experience is counted.

Evidence:
- `Resume - Aditya Saha.pdf`: One24 SDE Internship from May 2022 to Present (over 2 years). `total_experience_months` evaluates to `0`.
- `Abhinav_ML_Resume.pdf`: LTTS ML Engineer from Sept 2024 to Present. `total_experience_months` evaluates to `0`.
- In both resumes, `skill_experience` evaluates to `{}` because skill interval calculation also requires `end_year` and `end_month`.

Impact:
Active, experienced candidates appear to have 0 months of experience. ATS filters requiring minimum experience reject qualified candidates.

Root cause:
No handling for "Present" in `_normalize_duration()`, and strict `None` rejection in `calculate_total_experience()` and `calculate_skill_experience()`.

Existing issue:
New (critical calculation consequence of R-006).

Recommended direction:
Map "Present" to current date `(datetime.now().year, datetime.now().strftime("%B"))` during normalization.

---

ID: R-031
Priority: P1
Resume: `Resume - Aditya Saha.pdf`, `Abhinav_ML_Resume.pdf`
Component: Experience Normalizer (`experience_normalizer.py`)
Category: Information Loss / Normalization

Observed behavior:
`_normalize_duration()` uses a regex that only matches full month names (`January|February|...`), completely failing on standard 3-letter or 4-letter abbreviations (`Jul`, `Mar`, `Sept`, `Dec`, `Nov`).

Expected behavior:
Month normalization should support standard abbreviations (`Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`/`Sept`, `Oct`, `Nov`, `Dec`).

Evidence:
- `Resume - Aditya Saha.pdf`: `Jul 2017 - Mar 2019` -> `start_month: null, end_month: null`.
- `Abhinav_ML_Resume.pdf`: `Sept 2024 – Present` -> `start_month: null, end_month: null`.

Impact:
Experience intervals cannot be computed even when month names are explicitly stated in the resume.

Root cause:
Hardcoded regex in `experience_normalizer.py`:
`re.findall(r"January|February|March|April|May|June|July|August|September|October|November|December", duration, re.IGNORECASE)`

Existing issue:
New.

Recommended direction:
Expand regex to match abbreviations and map them to canonical month names using `MONTH_ALIASES`.

---

ID: R-032
Priority: P2
Resume: `HARSHIT_WEBDEV.pdf`, `Abhinav_ML_Resume.pdf`
Component: Project Parser (`project_parser.py`)
Category: Side Effect / Data Corruption

Observed behavior:
`_extract_projects()` modifies input dictionary objects in `text_blocks` in-place using `curr_project[-1]["text"] += " " + text`. If `process_projects()` or any test pipeline calls extraction multiple times on the same `text_blocks` list, line text is repeatedly concatenated, producing duplicated sentences in descriptions.

Expected behavior:
Parsers should treat input data structures as immutable or create shallow/deep copies before modifying text fields.

Evidence:
When running `_extract_projects` followed by `process_projects` on the same `text_blocks`:
`HARSHIT_WEBDEV.pdf`:
`"• Developed a scalable and efficient full-stack blog application enabling users to create and explore blogs with 15 percent more efficiency. 15 percent more efficiency."`
`Abhinav_ML_Resume.pdf`:
`"• Improved cricket match insights by accurately predicting IPL scores. Developed a machine learning model utilizing regression techniques. utilizing regression techniques."`

Impact:
Subtle, hard-to-debug data corruption when `text_blocks` is reused in services, retries, or testing suites.

Root cause:
In-place dictionary modification: `curr_project[-1]["text"] += " " + text`.

Existing issue:
New.

Recommended direction:
Copy dictionary (`dict(curr_project[-1])`) before modifying text.

---

ID: R-033
Priority: P2
Resume: `Resume - Aditya Saha.pdf`, `Abhinav_ML_Resume.pdf`
Component: Section Detection (`header_configs.py`)
Category: Information Loss / Generalization

Observed behavior:
Sections such as `INTERESTS`, `AREAS OF INTEREST`, or `ABOUT ME` are not registered in `SECTION_HEADERS`. In some cases, their content bleeds into preceding sections, or is completely unextracted without schema representation.

Expected behavior:
Non-standard sections should be safely recognized as section boundaries to prevent bleeding, and optionally captured under an `extracurriculars` or `profile` section.

Evidence:
- `Resume - Aditya Saha.pdf`: `INTERESTS` section (`Problem Solving`, `Working with Team`, `Bulding Real Life Products`) is unparsed.
- `Abhinav_ML_Resume.pdf`: `ABOUT ME` / summary sections in similar formats risk bleeding if placed after projects.

Impact:
Information loss and potential section boundary contamination.

Root cause:
`SECTION_HEADERS` contains an overly narrow set of keywords.

Existing issue:
New (broadens R-016).

Status:
- **Status:** PARTIAL
- **Fixed in:** Phase 4.5 Day 3 (`src/configs/header_configs.py`)
- **Validation:** `INTERESTS`, `ABOUT ME`, and `SUMMARY` were added to `SECTION_HEADERS`. `section_detector` now correctly identifies them as boundaries and prevents section bleeding.
- **Notes:** While boundary detection is solved, these sections are not yet mapped in `SECTION_ALIASES` or extracted into specialized structured schema fields.

Recommended direction:
Map non-standard sections in `SECTION_ALIASES` and introduce schema fields for summary/interests.

---

## Resume Generalization Summary

### Audit Statistics
- **Number of resumes tested:** 3 (`HARSHIT_WEBDEV.pdf`, `Resume - Aditya Saha.pdf`, `Abhinav_ML_Resume.pdf`)
- **Number of existing issues reproduced & strengthened:** 9 (R-002, R-005, R-006, R-007, R-009, R-014, R-015, R-018, R-021)
- **Number of new issues discovered:** 12 (R-022 through R-033)
- **Total distinct issues now documented:** 33

### Most Common Failure Categories
1. **Section Boundary & Header Detection:** Narrow keyword lists (`SKILL`, `SECTION_HEADERS`) caused total failure on standard variations (e.g. `Technologies` causing 100% skill loss and project bleed in `Abhinav_ML_Resume.pdf`).
2. **Project Boundary & Title Classification:** Relying on basic capitalization checks (`_is_project_title`) caused duration lines (`Jun 2022 - Jul 2022`) to fracture projects into empty shells and phantom duration records in `Resume - Aditya Saha.pdf`.
3. **Date & Duration Parsing:** Rigid regexes expecting only `Month - Month, Year` or `YYYY - YYYY` failed on `Month YYYY - Month YYYY`, abbreviated months (`Jul`, `Sept`), and "Present", resulting in active jobs showing 0 months experience.
4. **Tokenization & Delimiters:** Skill candidate extraction splitting only on `[,|/]` failed on conjunctions (`" and "`), discarding common skills like `React`, `SQL`, `MongoDB`, and `Node.js`.
5. **Entity Association:** Assuming rigid line-relative positions (line `i-1` is company, role keywords only occur in titles) caused description bullets containing "engineering" to steal candidate job titles.

### Parser Assumptions That Appear Resume-Specific
1. **Assuming skills are always labeled `Skills:` or `Technical Skills:`**: Fails when labeled `Technologies`.
2. **Assuming project title lines contain GitHub hyperlinks on the exact same vertical coordinate**: Fails when links appear on a `Preview :-` or `Link:` line below the title.
3. **Assuming duration strings follow `Month - Month, Year` without a year after the first month**: Fails on standard `Month Year - Month Year`.
4. **Assuming job titles and companies are on separate lines**: Fails when role, company, and location are comma-separated on a single line (`Machine Learning Engineer, LTTS – Mysore, KA`).
5. **Assuming role keywords never appear in bullet descriptions**: Fails on bullets describing "feature engineering" or "developing".
6. **Assuming institution and degree are never combined on the same line**: Fails on standard university + degree combined lines.

### Information Consistently Lost Across Formats
- **LinkedIn URLs:** Universal loss across 100% of tested resumes (hardcoded `None`).
- **Active Employment Duration:** Ongoing jobs with "Present" calculate to 0 months experience.
- **Skills connected by "and":** Conjunction skills (`MongoDB and SQL`) completely dropped from known skills.
- **Achievements & Certifications:** 100% dropped from structured output across all resumes.
- **Fractional CGPA scores (`X/10.0`):** Converted to `None` due to unhandled slash syntax.

### Areas Requiring Contract / Schema Decisions Before Implementation
1. **Active Employment Schema Contract:** Does the system calculate `total_experience_months` dynamically up to the current date when "Present" is encountered, or does the contract require an explicit `is_current: bool` field on experience entries?
2. **Unstructured / Secondary Sections Schema:** Should `ACHIEVEMENTS`, `CERTIFICATIONS`, and `INTERESTS` be added as first-class fields in `resume_data` and OpenAPI schemas, or normalized under a generic `sections` dictionary?
3. **Project Model Contract:** How should multi-link projects (live demo + GitHub + preview) be represented in the project schema (`metadata: list[dict]` vs explicit `links: {"github": str, "live": str}`) to prevent ambiguous text vs link storage?
4. **Multi-Entity Line Parsing:** Does the contract support composite line extraction (splitting `Role, Company, Location`), and how should confidence scores or fallbacks be defined when delimiters are ambiguous?

---

# Phase 4.5 Day 3: Real-World Corpus Validation & Issue Audit

**Audit Date:** 2026-09-21  
**Platform State:** Phase 4.5 Day 3 Complete (Section-Aware Architecture)  
**Test Baseline:** 358 passed, 1 warning (Windows pytest-cache permission warning)  
**Corpus Tested:** 14 Resumes (2 existing test fixtures + 12 diverse real-world PDFs) & 9 Real Job Descriptions  
**Code Modifications:** None (Preserving 100% source code integrity; documentation-only audit)

---

## 1. Real-World Resume Corpus (14 Resumes)

A representative, highly diverse set of 14 resume PDFs was validated against the current pipeline (`process_resume()`). The corpus covers freshers, junior SDEs, senior/staff ML engineers, directors, multi-page resumes, project-heavy profiles, competitive programmers, certified cloud engineers, narrative summaries, non-standard section headers, and unusual font-glyph formatting.

### Corpus Summary Table

| File | Category / Profile | Sections Detected | Skills (Known / Unknown) | Education | Experience | Projects | Total Exp (Months) | Key Pipeline Observations |
|---|---|---|---|---|---|---|---|---|
| `HARSHIT_WEBDEV.pdf` | Junior Web Dev (Reference) | 6 | 10 / 15 | 3 | 1 (Gosotek) | 3 | 2 | Clean baseline; R-002 (LinkedIn=None) and R-007 (project titles retain \| GitHub) observed |
| `resume_without_experience.pdf` | Fresher Web Dev (Multi-Page) | 5 | 10 / 16 | 3 | 0 | 4 | 0 | Multi-page boundary; R-009 phantom project `CSS` still persists with 0 description |
| `R01_Fresher_CS.pdf` | College Fresher / Hackathon Finalist | 5 | 9 / 2 | 1 | 0 | 2 | 0 | Fractional CGPA lost (`score=None`); R-035 project title mutated into description |
| `R02_Junior_SDE.pdf` | Junior SDE (1-2 YOE, "Present") | 4 | 9 / 0 | 1 | 1 | 0 | 0 | Dual job collapsed into 1 (R-006); bullet hijacked as role (R-025); 0 exp months (R-030) |
| `R03_Senior_Staff_ML.pdf` | Senior Staff ML (Ph.D., 8+ YOE) | 4 | 8 / 4 | 2 | 1 | 0 | 0 | Stanford Ph.D. degree dropped (R-036); multiple jobs collapsed; 0 exp months (R-030) |
| `R04_MultiPage_Executive.pdf` | Engineering Director (2-Page Multi-Page) | 7 | 7 / 6 | 2 | 1 | 0 | 0 | Page 2 experience dropped at section boundary (R-034); Certifications unparsed (R-015) |
| `R05_Projects_Heavy_FullStack.pdf` | Full-Stack (Next.js, Live Links, Verce/Netlify) | 4 | 9 / 2 | 1 | 0 | 3 | 0 | Rich GitHub & Live URLs on metadata lines lost (R-029); title mutated into description (R-035) |
| `R06_Achievements_Competitive.pdf` | Competitive Coder (LeetCode Guardian, JEE) | 5 | 5 / 5 | 1 | 1 | 0 | 0 | 5 top-tier achievements dropped (R-014); fractional CGPA 9.45/10.0 lost (R-027) |
| `R07_Certifications_Cloud_DevOps.pdf` | Cloud DevOps (AWS PSA, CKA, Terraform) | 5 | 5 / 4 | 1 | 1 | 0 | 0 | Certifications & Credly links dropped (R-015); ongoing job calculates to 0 months (R-030) |
| `R08_Summary_Profile_DataScience.pdf` | Lead Data Scientist (6 YOE, Narrative Summary) | 4 | 5 / 8 | 2 | 0 | 0 | 0 | Narrative summary unextracted into schema (R-016); experience missed due to layout (R-005) |
| `R09_Multiple_Skills_Sections.pdf` | Full-Stack Systems (Tech + Non-Tech Skills) | 6 | 8 / 4 | 1 | 1 | 1 | 0 | Section detector successfully detected and merged both skill sections! (R-010 FIXED) |
| `R10_Alternate_Headings.pdf` | Alternate Headings (Work History, Academics) | 3 | 0 / 0 | 0 | 0 | 1 | 0 | Headings not in `SECTION_HEADERS` causing complete extraction failure (R-037) |
| `R11_Unusual_Formatting_Icons.pdf` | SRE (Date-first layout, Icon Glyphs) | 4 | 5 / 4 | 2 | 1 | 0 | 0 | Date-first layout causes last bullet to become company name (R-005); glyphs in text (R-018) |
| `R12_No_Experience_BioMed.pdf` | Computational Biology (IISER, Publications) | 6 | 4 / 4 | 1 | 0 | 2 | 0 | IISER Pune not recognized as institution (R-040); publications dropped (R-015) |

---

## 2. Real-World Job Description Corpus (9 Job Descriptions)

A corpus of 9 real-world job descriptions from industry-leading tech companies was analyzed against `src/parsers/jd_parser.py` (`parse_jd`).

### Job Description Corpus Summary Table

| ID | Company | Role Title | Target Domain | Extracted Role | Experience Months | Extracted Skills | Missed Critical Skills |
|---|---|---|---|---|---|---|---|
| **JD-01** | Meta | Machine Learning Engineer - Ranking & Recommendations | Applied ML / RecSys | `None` (missing `Role:`) | `None` | `Python`, `SQL`, `Docker`, `Kubernetes` | `PyTorch`, `TensorFlow`, `Machine Learning`, `Deep Learning` |
| **JD-02** | OpenAI | AI Backend Engineer, API Infrastructure | AI Backend / High Concurrency | `AI Backend Engineer, API Infrastructure` | `None` | `Python`, `FastAPI`, `Kubernetes`, `Docker`, `AWS` | `Triton`, `vLLM`, `TensorRT-LLM`, `Redis` |
| **JD-03** | Anthropic | GenAI / Alignment Research Engineer | GenAI / Alignment / LLM | `GenAI / Alignment Research Engineer` | `None` | `Python` | `PyTorch`, `RLHF`, `Transformer`, `LangChain`, `LlamaIndex` |
| **JD-04** | Databricks | Data & ML Platform Engineer | ML Platform / MLOps | `None` (unlabeled title) | `None` | `Python`, `Java`, `SQL`, `Kubernetes`, `AWS`, `Docker`, `Git` | `Apache Spark`, `Delta Lake`, `MLflow`, `Kubeflow`, `Ray`, `Scala` |
| **JD-05** | Stripe | Machine Learning Engineer - Fraud & Risk | Real-time ML / Fraud | `Machine Learning Engineer - Fraud & Risk` | `None` | `Python`, `SQL`, `Docker`, `Java` | `Scikit-learn`, `XGBoost`, `PyTorch`, `Kafka` |
| **JD-06** | Google DeepMind | Research Engineer, Foundation Models | Foundation Models / Research | `None` (used `Title:`) | 24 | `Python` | `PyTorch`, `JAX`, `TensorFlow`, `Deep Learning` |
| **JD-07** | Siemens | Generative AI Engineer | GenAI / RAG / Enterprise | `None` (unlabeled title) | `None` | `Python`, `FastAPI`, `Docker`, `Git`, `AWS` | `LangChain`, `LangGraph`, `LlamaIndex`, `Pinecone`, `Qdrant`, `Chroma` |
| **JD-08** | Uber | Senior Machine Learning Engineer - Maps & Routing | Applied ML / GNN / Routing | `None` (unlabeled title) | `None` | `Python`, `SQL`, `Docker`, `Kubernetes` | `PyTorch`, `Horovod`, `Graph Neural Networks` |
| **JD-09** | Amazon (AWS) | Applied AI/ML Engineer - Bedrock Solutions | GenAI Solutions / Cloud | `Applied AI/ML Engineer - Bedrock Solutions` | `None` | `AWS`, `Python`, `Git`, `Docker` | `LangChain`, `Bedrock`, `SageMaker`, `Linux` |

### Key Structural Discoveries in Real JDs
1. **Pervasive Vocabulary Truncation (JD-001):** Top ML frameworks (`PyTorch`, `TensorFlow`, `JAX`, `LangChain`, `LlamaIndex`, `Spark`, `MLflow`) are 100% dropped because they are missing from `KNOWN_SKILLS`.
2. **Missing `Title:` and Unlabeled Role Extraction (R-041 / JD-002):** 5 out of 9 JDs (55%) failed role extraction because titles either lacked prefixes or used `Title:` (not in `ROLE_KEYWORDS`).
3. **Experience Requirement Phrasing Gaps (R-042 / JD-003):** 8 out of 9 JDs (89%) failed overall experience extraction because of qualifiers like `of professional experience in applied machine learning` or `software engineering or machine learning experience`.

---

## 3. New Issues Discovered During Real-World Validation

---

### R-034: Multi-page and repeated canonical experience sections are dropped by experience parser

- **ID:** R-034
- **Title:** Multi-page and repeated canonical experience sections dropped by experience parser
- **Status:** OPEN
- **Severity:** P0
- **Category:** Information Loss / Architectural Gap
- **Observed in:** `R04_MultiPage_Executive.pdf`

#### Observed Behavior
When a candidate's work history spans across multiple pages and the heading `EXPERIENCE` repeats at the top of subsequent pages, `section_detector` successfully detects both canonical sections (`['preamble', 'summary', 'experience', 'experience', ...]`). However, `process_experience()` still receives raw `cleaned_text`, and `_extract_experience()` contains:
```python
if contains_keywords(line, SECTION_HEADERS):
    break
```
As soon as the first experience section terminates at `EDUCATION` on Page 1, `_extract_experience()` permanently breaks out of the extraction loop. The entire second `EXPERIENCE` section on Page 2 (containing Bloomberg LP) is completely dropped from structured output.

#### Evidence
In `R04_MultiPage_Executive.pdf`:
- Page 1 has Stripe and Goldman Sachs under `EXPERIENCE`.
- Page 2 has Bloomberg LP under `EXPERIENCE`.
- `sections` list has both sections: `['experience', 'experience']`.
- Parsed `experience` array only has 1 company (`Stripe`). Goldman Sachs and Bloomberg LP are lost.

#### Impact
High-tenure candidates with multi-page resumes lose significant portions of their work history, leading to inaccurate experience calculations and false negative ATS filtering.

#### Likely Component
`src/services/resume_service.py` and `src/parsers/experience_parser.py`.

#### Suggested Future Fix
Migrate `experience_parser` to receive isolated section text from `section_detector` (similar to Phase 4.5 Day 3 `skills_parser` migration), combining all detected `experience` section contents before parsing.

---

### R-035: Project parser mutates title block into description when bullet characters do not strictly match `•`, `-`, or `*`

- **ID:** R-035
- **Title:** Project parser mutates title block into description when bullet characters do not strictly match standard bullets
- **Status:** OPEN
- **Severity:** P0
- **Category:** Data Corruption / Information Loss
- **Observed in:** `R01_Fresher_CS.pdf`, `R05_Projects_Heavy_FullStack.pdf`, `R09_Multiple_Skills_Sections.pdf`, `R10_Alternate_Headings.pdf`, `R12_No_Experience_BioMed.pdf`

#### Observed Behavior
In `src/parsers/project_parser.py`, `_extract_projects()` checks:
```python
if text.startswith(("•", "-", "*")):
    curr_project.append(line)
elif _is_project_metadata(text, PROJECT_METADATA_KEYWORDS):
    curr_project.append(line)
elif _is_project_title(text):
    ...
elif curr_project:
    if not page_changed:
        curr_project[-1]["text"] += " " + text
```
When a PDF uses alternative bullet characters (e.g. Unicode `\u2023`, `\u25cf`, `\u25b6`, `\u25e6`, or font-glyph mappings), `text.startswith(("•", "-", "*"))` evaluates to `False`. The description line falls into `elif curr_project:` and is concatenated in-place to `curr_project[-1]["text"]` (the title block). In the subsequent `_parse_projects()` pass, the mutated title line now ends with a period and exceeds title length limits. Consequently, `_is_project_title()` rejects it, and it falls into `else: project["description"].append(text)`. The project title is left as `None` (normalized to `""`).

#### Evidence
In `R01_Fresher_CS.pdf`, `R05_Projects_Heavy_FullStack.pdf`, and `R12_No_Experience_BioMed.pdf`:
```json
{
  "project": "",
  "metadata": [],
  "description": ["AI Resume Analyzer | GitHub Developed automated resume parser..."]
}
```
All project titles become empty strings `""`, and descriptions contain the merged title line.

#### Impact
100% loss of project title entities for resumes using non-standard bullet symbols. Downstream project keyword matching and title-based quality scoring completely fail.

#### Likely Component
`src/parsers/project_parser.py` (`_extract_projects` and `_parse_projects`).

#### Suggested Future Fix
1. Expand recognized bullet characters: `("•", "-", "*", "–", "—", "·", "\u2022", "\u2023", "\u25cf", "\u25b6", "\u25e6")`.
2. Do not mutate the title block in `_extract_projects` by concatenating non-matching lines to it.

---

### R-036: `DEGREE_KEYWORDS` missing doctoral degrees (`PhD`, `Ph.D.`, `Doctor of Philosophy`)

- **ID:** R-036
- **Title:** `DEGREE_KEYWORDS` missing doctoral degrees (`PhD`, `Ph.D.`, `Doctor of Philosophy`)
- **Status:** OPEN
- **Severity:** P1
- **Category:** Information Loss / Generalization
- **Observed in:** `R03_Senior_Staff_ML.pdf`

#### Observed Behavior
In `src/configs/education_configs.py`, `DEGREE_KEYWORDS` includes:
`B.TECH`, `BACHELOR`, `B.E`, `M.TECH`, `MASTER`, `MCA`, `MBA`, `BSC`, `MSC`, `DIPLOMA`, `X`, `XII`.
Doctoral degree identifiers (`PHD`, `PH.D`, `DOCTOR`, `DOCTORATE`) are completely absent. In `src/parsers/education_parser.py`:
```python
elif contains_keywords(line, DEGREE_KEYWORDS):
    education["degree"] = line
```
Because the line `Doctor of Philosophy in Computer Science` does not match any keyword in `DEGREE_KEYWORDS`, `education["degree"]` remains `None`.

#### Evidence
In `R03_Senior_Staff_ML.pdf`:
- Raw text: `Stanford University \n Doctor of Philosophy in Computer Science \n 2011 - 2015`.
- Parsed normalized education output:
  ```json
  {
    "degree": null,
    "field": null,
    "institution": "Stanford University",
    "start_year": 2011,
    "end_year": 2015
  }
  ```
The candidate's Ph.D. degree is completely lost.

#### Impact
Doctoral degrees of researchers and senior scientists are erased, causing failure on minimum qualification checks for advanced research and engineering roles.

#### Likely Component
`src/configs/education_configs.py` (`DEGREE_KEYWORDS`) and `src/configs/normalization_configs.py` (`DEGREE_ALIASES`).

#### Suggested Future Fix
Add `PHD`, `PH.D`, `DOCTOR`, `DOCTORATE` to `DEGREE_KEYWORDS` and map them to `"Ph.D."` in `DEGREE_ALIASES`.

---

### R-037: Section detector does not recognize `WORK HISTORY`, `ACADEMIC QUALIFICATIONS`, or `AREAS OF EXPERTISE`

- **ID:** R-037
- **Title:** Section detector does not recognize `WORK HISTORY`, `ACADEMIC QUALIFICATIONS`, or `AREAS OF EXPERTISE`
- **Status:** OPEN
- **Severity:** P1
- **Category:** Section Detection / Information Loss
- **Observed in:** `R10_Alternate_Headings.pdf`

#### Observed Behavior
In `src/configs/header_configs.py`, `SECTION_HEADERS` contains `EXPERIENCE`, `WORK EXPERIENCE`, `PROFESSIONAL EXPERIENCE`, `EDUCATION`, and `SKILLS`, but lacks common synonyms such as:
- `WORK HISTORY`
- `ACADEMIC QUALIFICATIONS`, `ACADEMIC BACKGROUND`
- `AREAS OF EXPERTISE`, `CORE COMPETENCIES`, `TECHNICAL EXPERTISE`
When a resume uses these headings, `section_detector.py` fails to recognize any section transition. The entire body text is absorbed by the preceding section (or preamble), resulting in empty skills, unextracted education, and unextracted experience.

#### Evidence
In `R10_Alternate_Headings.pdf`:
- Detected sections: `['preamble', 'about me', 'projects']`.
- `skills`: `[]` (0 skills extracted).
- `education`: `[]` (0 education entries).
- `experience`: `[]` (0 experience entries).
- All work history, academic qualifications, and areas of expertise were trapped inside the `about me` section.

#### Impact
Complete parsing failure for resumes using standard alternative section headers.

#### Likely Component
`src/configs/header_configs.py` (`SECTION_HEADERS` and `SECTION_ALIASES`).

#### Suggested Future Fix
Add `WORK HISTORY`, `EMPLOYMENT HISTORY` (mapped to `"experience"`), `ACADEMIC QUALIFICATIONS`, `ACADEMIC BACKGROUND` (mapped to `"education"`), and `AREAS OF EXPERTISE`, `CORE COMPETENCIES` (mapped to `"skills"`) to `SECTION_HEADERS` and `SECTION_ALIASES`.

---

### R-038: Multi-page and repeated education sections dropped due to first `SECTION_HEADERS` break

- **ID:** R-038
- **Title:** Multi-page and repeated education sections dropped due to first `SECTION_HEADERS` break
- **Status:** OPEN
- **Severity:** P1
- **Category:** Information Loss / Architectural Gap
- **Observed in:** Multi-page resumes (architectural verification)

#### Observed Behavior
In `src/parsers/education_parser.py`:
```python
for line in lines:
    if not inside_education:
        if contains_keywords(line, EDUCATION_SECTION_HEADERS):
            inside_education = True
        continue
    if contains_keywords(line, SECTION_HEADERS):
        break
```
Because the parser breaks at the very first `SECTION_HEADERS` keyword encountered after entering education, any resume that repeats the education section on a subsequent page or has split education blocks loses all subsequent education content.

#### Evidence
Identical architectural root cause to R-034: `process_education(cleaned_text)` does not leverage `sections` produced by `detect_sections()`, relying on a fragile line-scan that terminates on the first section boundary.

#### Impact
Degrees listed across page boundaries or non-contiguous blocks are permanently dropped.

#### Likely Component
`src/services/resume_service.py` and `src/parsers/education_parser.py`.

#### Suggested Future Fix
Migrate `education_parser` to receive isolated section text from `section_detector`.

---

### R-039: Completeness analyzer enforces `projects` as required for all candidates regardless of seniority

- **ID:** R-039
- **Title:** Completeness analyzer enforces `projects` as required for all candidates regardless of seniority
- **Status:** OPEN
- **Severity:** P2
- **Category:** Domain Logic / False Positive
- **Observed in:** `R03_Senior_Staff_ML.pdf`, `R04_MultiPage_Executive.pdf`, `R07_Certifications_Cloud_DevOps.pdf`, `R08_Summary_Profile_DataScience.pdf`

#### Observed Behavior
In `src/configs/analyzers_configs.py`:
```python
REQUIREMENTS_TABLE = {
    "required": ["name", "email", "education", "projects", "skills"],
    "recommended": ["phone", "linkedin", "experience"]
}
```
`projects` is marked as strictly `required`. Experienced professionals (e.g. Senior Staff Engineers, VPs, Directors with 8–15 years of industry experience) typically omit academic/personal hobby projects in favor of commercial achievements and leadership impact. As a result, 100% of experienced profiles in our corpus are flagged with `"missing_required": ["projects"]`.

#### Evidence
In `R03_Senior_Staff_ML.pdf` (8+ YOE Databricks/Uber/Amazon staff ML engineer):
`"missing_required": ["projects"]`.
In `R04_MultiPage_Executive.pdf` (10+ YOE Engineering Director):
`"missing_required": ["projects"]`.

#### Impact
Distorts completeness scores and triggers false-positive defect warnings for highly qualified senior candidates.

#### Likely Component
`src/configs/analyzers_configs.py` and `src/analyzers/completeness_analyzer.py`.

#### Suggested Future Fix
Introduce conditional completeness logic: candidate must have either `experience` OR `projects` in `required`, or categorize `projects` as `recommended` when `experience` is present.

---

### R-040: Institution detection misses national research institutes and specialized academies

- **ID:** R-040
- **Title:** Institution detection misses national research institutes and specialized academies
- **Status:** OPEN
- **Severity:** P2
- **Category:** Information Loss / Keyword Coverage
- **Observed in:** `R12_No_Experience_BioMed.pdf`

#### Observed Behavior
In `src/configs/education_configs.py`:
```python
INSTITUTION_KEYWORDS = ["SCHOOL", "COLLEGE", "INSTITUTE", "UNIVERSITY", "ACADEMY"]
```
Candidates attending prestigious institutions referenced by acronyms or non-standard designations (such as `IISER Pune`, `BITS Pilani`, `IIIT Hyderabad`, `AIIMS`, `IIM`) fail `contains_keywords(line, INSTITUTION_KEYWORDS)`. In `_extract_education()`, the line is not recognized as an institution boundary, and `institution` is left empty.

#### Evidence
In `R12_No_Experience_BioMed.pdf`:
Line 4: `IISER Pune` -> parsed `"institution": ""` (empty).

#### Impact
Loss of institution reputation and pedigree signals in candidate ranking.

#### Likely Component
`src/configs/education_configs.py` (`INSTITUTION_KEYWORDS`).

#### Suggested Future Fix
Add common premier institution acronyms and designations: `IISER`, `IIT`, `NIT`, `IIIT`, `BITS`, `IIM`, `AIIMS`, `POLYTECHNIC`, `FACULTY`.

---

### R-041: JD Parser `ROLE_KEYWORDS` misses common title labels such as `Title:` and fails on unlabelled top-line job titles

- **ID:** R-041
- **Title:** JD Parser `ROLE_KEYWORDS` misses common title labels such as `Title:` and fails on unlabelled top-line job titles
- **Status:** OPEN
- **Severity:** P1
- **Category:** Information Loss / Generalization
- **Observed in:** JD-01 (Meta), JD-04 (Databricks), JD-06 (Google DeepMind), JD-07 (Siemens), JD-08 (Uber)

#### Observed Behavior
In `src/parsers/jd_parser.py`:
```python
def _extract_role(jd: list[str]) -> str | None:
    for line in jd:
        if ":" in line:
            key, value = line.split(":", 1)
            if key.strip().lower() in ROLE_KEYWORDS:
                return value.strip()
    return None
```
`ROLE_KEYWORDS` only includes `{"role", "position", "job title"}`. If a job posting uses `Title:` (as Google DeepMind does), or places the job title on the first non-empty line without a colon prefix (as Meta, Databricks, Siemens, and Uber do), `_extract_role()` returns `None`.

#### Evidence
Across 9 real job descriptions tested:
- 5 out of 9 (55%) returned `"role": null`.
- DeepMind used `Title: Research Engineer, Foundation Models` -> `role: null`.
- Meta used `Machine Learning Engineer - Ranking & Recommendations` on Line 1 -> `role: null`.

#### Impact
Matching engines cannot compare candidate target roles against job titles for the majority of real-world job descriptions.

#### Likely Component
`src/configs/jd_configs.py` (`ROLE_KEYWORDS`) and `src/parsers/jd_parser.py` (`_extract_role`).

#### Suggested Future Fix
1. Add `"title"` to `ROLE_KEYWORDS`.
2. Implement fallback extraction to inspect the first non-empty substantive line before the first section header.

---

### R-042: JD Experience Parser `YOE_PATTERN` fails to extract required experience when formatted as `Minimum X+ years` with trailing qualifier

- **ID:** R-042
- **Title:** JD Experience Parser `YOE_PATTERN` fails to extract required experience when formatted as `Minimum X+ years` with trailing qualifier
- **Status:** OPEN
- **Severity:** P1
- **Category:** Information Loss / Regex Limitation
- **Observed in:** JD-01 (Meta), JD-04 (Databricks), JD-05 (Stripe), JD-08 (Uber)

#### Observed Behavior
In `src/parsers/jd_parser.py`:
`YOE_PATTERN` has a strict negative lookahead:
```python
YOE_PATTERN = re.compile(
    r"""
    \b(?:minimum|at\s+least)?\s*
    (\d+)\+?
    \s+(?:years?|yrs?)
    \s+(?:of\s+)?
    (?:professional\s+)?
    (?:industry\s+)?
    experience\b
    (?!\s+(?:with|in)\b)
    """,
    re.IGNORECASE | re.VERBOSE,
)
```
When a real JD specifies:
- `Minimum 4+ years of professional experience in applied machine learning` (Meta) -> rejected by `(?!\s+(?:with|in)\b)`
- `Minimum 3 years of software engineering experience` (Databricks) -> rejected because `software engineering` is not matched by `(?:professional\s+)?(?:industry\s+)?`
- `5+ years of software engineering or machine learning experience` (Uber) -> rejected for the same reason.
Consequently, `_extract_experience()` returns `None`.

#### Evidence
In 8 out of 9 real JDs tested (89%), `experience_months` was returned as `None`, despite explicit years of experience requirements in the text.

#### Impact
ATS minimum experience filters fail to extract tenure constraints from the vast majority of real job postings.

#### Likely Component
`src/parsers/jd_parser.py` (`YOE_PATTERN` and `_extract_experience`).

#### Suggested Future Fix
Permit flexible domain modifiers (e.g. `software engineering`, `applied machine learning`, `relevant`, `related`) and allow trailing `in <domain>` clauses when extracting overall experience.

---

## 4. Master Status Matrix (R-001 through R-042)

| Issue ID | Severity | Category | Status | Fixed In | Summary Title |
|---|---|---|---|---|---|
| **R-001** | P0 | Info Loss | **FIXED** | Phase 4.5 Day 1 | Skills parser drops no-colon skills |
| **R-002** | P0 | Info Loss | **OPEN** | — | LinkedIn URL extracted from PDF links is never surfaced |
| **R-003** | P1 | Incorrect Ext | **OPEN** | — | Name parser returns first non-empty line unconditionally |
| **R-004** | P1 | Info Loss | **FIXED** | Phase 4.5 Day 1 | Wrapped experience bullets split into orphan line |
| **R-005** | P1 | Incorrect Ext | **OPEN** | — | Experience parser previous-line company assumption |
| **R-006** | P1 | Date Handling | **OPEN** | — | Duration pattern misses `Month YYYY - Month YYYY` / "Present" |
| **R-007** | P1 | Normalization | **OPEN** | — | Project title retains `\| GitHub` / `\| LIVE` suffix |
| **R-008** | P1 | Info Loss | **FIXED** | Phase 4.5 Day 1 | Experience bullet continuation line dropped |
| **R-009** | P0 | Boundary Det | **PARTIAL** | Phase 4.5 Day 1 | Multi-page PDF phantom projects (`CSS` persists) |
| **R-010** | P2 | Section Det | **FIXED** | Phase 4.5 Day 3 | Skills parser only extracts first skills section |
| **R-011** | P2 | Section Det | **OPEN** | — | Education header misses variants (`ACADEMIC QUALIFICATIONS`) |
| **R-012** | P2 | Section Det | **OPEN** | — | Experience header misses variants (`WORK HISTORY`) |
| **R-013** | P1 | Robustness | **FIXED** | Phase 3 / Day 3 | Quality analyzer `None` year `TypeError` crash |
| **R-014** | P1 | Info Loss | **OPEN** | — | Achievements section content completely discarded |
| **R-015** | P1 | Info Loss | **OPEN** | — | Certifications and publications sections unparsed |
| **R-016** | P2 | Schema Gap | **OPEN** | — | Summary / Profile / Objective section unextracted |
| **R-017** | P2 | Normalization | **OPEN** | — | Skills normalizer wrapped multi-line skill values |
| **R-018** | P3 | Glyphs/Noise | **OPEN** | — | Contact info glyph/icon artifacts in text |
| **R-019** | P2 | Calculation | **OPEN** | — | `total_experience_months` inclusive +1 counting |
| **R-020** | P4 | Noise | **OPEN** | — | Duplicate name artifact in text layer |
| **R-021** | P2 | Normalization | **OPEN** | — | Degree aliases missing secondary / senior secondary / plurals |
| **R-022** | P1 | Tokenization | **OPEN** | — | Skills parser drops skills separated by conjunction `" and "` |
| **R-023** | P0 | Boundary Det | **OPEN** | — | Standalone duration lines in projects become phantom titles |
| **R-024** | P0 | Section Det | **OPEN** | — | "Technologies" header not in `SECTION_HEADERS` |
| **R-025** | P0 | Entity Assoc | **OPEN** | — | Experience parser mistakes bullet with role keyword for role |
| **R-026** | P1 | Entity Assoc | **OPEN** | — | Education parser misses degree when combined on same line |
| **R-027** | P2 | Normalization | **OPEN** | — | Education normalizer fails on fractional CGPA (`8.67/10.0`) |
| **R-028** | P2 | Normalization | **OPEN** | — | Education score lines prefixed with bullet fail type check |
| **R-029** | P1 | Link Assoc | **OPEN** | — | Project parser only associates hyperlinks on title bbox |
| **R-030** | P1 | Calculation | **OPEN** | — | Experience normalizer "Present" yields 0 months experience |
| **R-031** | P1 | Normalization | **OPEN** | — | Regex only matches full month names, fails on abbreviations |
| **R-032** | P2 | Side Effect | **OPEN** | — | In-place modification of `text_blocks` duplicates descriptions |
| **R-033** | P2 | Section Det | **PARTIAL** | Phase 4.5 Day 3 | Non-standard sections (`INTERESTS`, `ABOUT ME`, `SUMMARY`) |
| **R-034** | P0 | Architecture | **OPEN** | — | Multi-page repeated canonical experience sections dropped |
| **R-035** | P0 | Info Loss | **OPEN** | — | Project parser mutates title block into description on bullets |
| **R-036** | P1 | Generalization| **OPEN** | — | `DEGREE_KEYWORDS` missing doctoral degrees (`PhD`, `Doctor`) |
| **R-037** | P1 | Section Det | **OPEN** | — | Section detector misses `WORK HISTORY`, `ACADEMIC QUALIFICATIONS` |
| **R-038** | P1 | Architecture | **OPEN** | — | Multi-page repeated education sections dropped |
| **R-039** | P2 | Domain Logic | **OPEN** | — | Completeness analyzer enforces `projects` as required for all |
| **R-040** | P2 | Keyword Cov | **OPEN** | — | Institution detection misses premier national institutes (`IISER`) |
| **R-041** | P1 | Generalization| **OPEN** | — | JD parser misses `Title:` and unlabeled top-line roles |
| **R-042** | P1 | Regex Limit | **OPEN** | — | JD YOE pattern fails on `Minimum X+ years` with qualifiers |

### Status Ledger Summary
- **Total Documented Issues:** 42
- **FIXED:** 5 (R-001, R-004, R-008, R-010, R-013)
- **PARTIAL:** 2 (R-009, R-033)
- **OPEN:** 35
- **REGRESSIONS:** 0

