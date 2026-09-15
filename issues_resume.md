# Resume Parser Issues

---

## R-001: Skills parser silently drops all skills on lines without a colon

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
OPEN

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

## R-004: Wrapped/continued bullet lines are split into a new orphan line in the description

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
OPEN

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

## R-008: First experience bullet continuation line lost — `10 percent page loading` dropped completely

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
OPEN

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
OPEN

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
OPEN

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
OPEN

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

1. **R-009 (P0)** — Multi-page PDF creates phantom project entries (`HTML, CSS`, `CSS`) — confirmed incorrect extraction from `resume_without_experience.pdf`.
2. **R-002 (P0)** — LinkedIn URL extracted but hard-coded as `None` — confirmed information loss in `HARSHIT_WEBDEV.pdf`.
3. **R-001 (P0)** — Skills parser drops all skills when lines lack a colon — generalization failure.
4. **R-013 (P1)** — `quality_analyzer` crashes with `TypeError` when `start_year`/`end_year` is `None`.
5. **R-014 (P1)** — `ACHIEVEMENTS` section not extracted from either test document — confirmed information loss.
