# JD Parser Issues

---

## JD-001: Skills extraction entirely depends on a small closed `KNOWN_SKILLS` list — any unlisted skill is silently dropped

- **Source:** All JD inputs
- **Category:** Information Loss
- **Severity:** P0

### Observed
`KNOWN_SKILLS` contains only 17 skills:
```python
{"Python", "C", "C++", "Java", "JavaScript", "TypeScript", "SQL", "MySQL",
 "React", "FastAPI", "Django", "Flask", "Git", "Node.js", "AWS", "Docker", "Kubernetes"}
```

Any skill not in this list — including extremely common ones like `TensorFlow`, `PyTorch`, `Pandas`, `NumPy`, `Scikit-learn`, `Redis`, `Kafka`, `Spark`, `Go`, `Rust`, `Ruby`, `MongoDB`, `PostgreSQL`, `GraphQL`, `REST`, `Spring`, `Angular`, `Vue`, `.NET`, `Azure`, `GCP`, `Terraform`, `Jenkins`, `CI/CD`, `Bash` — is **completely ignored**.

Test (JD9):
```
Role: Data Scientist
Requirements: TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy, Jupyter, Python, SQL
```
Output:
```json
"skills": ["Python", "SQL"]
```
TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy, Jupyter — all lost.

### Source Evidence
JD9 test: 8 skills listed in the JD. Only 2 (`Python`, `SQL`) are in `KNOWN_SKILLS`. The other 6 are entirely absent from the output.

Re-verified on real PDF fixture `jd_ml_engineer_test.pdf`:
The document lists required and preferred skills: `Python`, `Machine Learning`, `scikit-learn`, `SQL`, `FastAPI`, `Docker`, `AWS`, `Kubernetes`, `PyTorch`, `MLflow`.
Output: `['Python', 'SQL', 'FastAPI', 'Docker', 'AWS', 'Kubernetes']`.
`Machine Learning`, `scikit-learn`, `PyTorch`, and `MLflow` are completely lost because they are not present in `KNOWN_SKILLS`.

### Expected
A robust JD parser should extract all mentioned skills, not only those in a pre-defined list. At minimum, the known skills list must be dramatically expanded. Ideally, skill extraction should not rely solely on an exhaustive closed list.

### Impact
JD skill profiles are severely incomplete. Matching between resume skills and JD required skills will produce false negatives for any skill outside the 17-item list. A Data Science JD with TensorFlow and PyTorch would show `skills: [Python, SQL]` — an almost useless extraction.

### Likely Area
`src/configs/skill_configs.py` — `KNOWN_SKILLS`. `src/parsers/jd_parser.py` — `_extract_skills()`.

### Status
OPEN

---

## JD-002: Role extraction only works when a `Role:`, `Position:`, or `Job Title:` label is present — fails for all other formats

- **Source:** JD2 test input
- **Category:** Information Loss / Generalization
- **Severity:** P1

### Observed
`_extract_role()` scans lines for one of three exact key prefixes: `role`, `position`, `job title`. If the job title appears anywhere else (first line, standalone, in a heading, within a paragraph), it returns `None`.

Test (JD2):
```
Backend Engineer - Python/FastAPI
We are looking for a skilled backend developer.
Minimum 5 years of professional experience.
```
Output: `"role": null`

The actual role is `Backend Engineer - Python/FastAPI` (the first line), which is a very common JD format.

Test (JD6) — no labeled role:
```
Responsibilities:
- Build scalable APIs using Python and FastAPI
...
```
Output: `"role": null`

### Source Evidence
JD2 output: `"role": null`. JD6 output: `"role": null`. Both are real-world valid JD formats.

Re-verified on real PDF fixture `jd_ml_engineer_test.pdf`:
Line 1: `Machine Learning Engineer`
Line 2: `Location: Bengaluru, India`
Line 3: `Experience: 3+ years`
Line 4: `Role Overview`
Output: `"role": null`. Because the role is not preceded by `Role:`, `Position:`, or `Job Title:`, `_extract_role()` fails to detect the job title.

Across 9 real job descriptions tested (Meta, Databricks, Google DeepMind, Siemens, Uber, Stripe, etc.):
- 5 out of 9 (55%) returned `"role": null`.
- Google DeepMind used `Title: Research Engineer, Foundation Models` -> `role: null` (fails because `Title:` is not in `ROLE_KEYWORDS`).
- Meta used `Machine Learning Engineer - Ranking & Recommendations` on Line 1 -> `role: null` (unlabeled first line).
- Databricks, Siemens, and Uber also placed the job title on the top line without a label prefix -> all returned `role: null`.

ROLE_KEYWORDS:
```python
{"role", "position", "job title"}
```
Any JD that doesn't use one of these three exact label words cannot have its role extracted.

### Expected
A robust parser should attempt to extract the role from:
1. Recognized label prefixes: add `"title"`, `"opening"`, `"vacancy"`, `"we are hiring"` to `ROLE_KEYWORDS`.
2. Positional heuristics: if no labeled prefix is found, inspect the first non-empty substantive line before the first section header (e.g. before `About the Role`, `Responsibilities`, etc.).

### Impact
For the majority of real-world JDs (55% failure rate), `role` is `null`. Downstream matching has no role to compare against. ATS-style filtering by role/title cannot function.

### Likely Area
`src/configs/jd_configs.py` — `ROLE_KEYWORDS`. `src/parsers/jd_parser.py` — `_extract_role()`.

### Status
OPEN

---

## JD-003: `skill_specific_experience` pattern misses `X years of experience in <skill>` format — only captures two specific phrasings

- **Source:** JD7 test input
- **Category:** Incorrect Extraction
- **Severity:** P1

### Observed
`SKILL_YOE_PATTERN` supports only two phrasings:
1. `N years of <SKILL> experience`
2. `N years of experience with <SKILL>`

The phrasing `N years of experience in <SKILL>` is NOT captured:
```
5 years of experience in Python   → not captured
3 years of experience in SQL      → not captured
2 years of AWS experience         → captured (pattern 1 variant)
```

Test (JD7) output:
```json
"skill_specific_experience": [{"skill": "AWS", "experience_months": 24}]
```
Python and SQL (with `in` phrasing) are completely missed.

### Source Evidence
JD7 test confirmed: `_extract_skill_specific_experience(['5 years of experience in Python', '3 years of experience in SQL']) => []`

Re-verified on real PDF fixture `jd_ml_engineer_test.pdf`:
The document has an explicit `Skill-Specific Experience` section:
```
• Python: 3+ years
• Machine Learning: 2+ years
• FastAPI: 1+ year
• SQL: 2+ years
```
Output: `[]`. None of these requirements are extracted because `SKILL_YOE_PATTERN` requires suffix syntax (`N years of <skill> experience`), completely missing key-value syntax (`<skill>: N+ years`).

### Expected
The pattern should also handle `N years of experience in <SKILL>`. This is a very common phrasing in real JDs.

### Impact
Skill-specific experience requirements are under-reported. Downstream matching uses `skill_specific_experience` to compare candidate skill tenure against JD requirements — if requirements are missed, the comparison is incomplete and potentially misleading.

### Likely Area
`src/parsers/jd_parser.py` — `SKILL_YOE_PATTERN` regex. The `in` preposition variant is not covered.

### Status
OPEN

---

## JD-004: `skill_requirements` classifier operates on individual lines — context from section headers is not inherited by child lines

- **Source:** JD1, JD2 test inputs
- **Category:** Incorrect Extraction
- **Severity:** P1

### Observed
When a JD has a section header like `Required:` or `Nice to have:`, all subsequent bullet lines under that section should inherit the parent requirement type. Instead, each line is classified independently:

```json
{"line": "Required:", "requirement": "required"},
{"line": "- Python", "requirement": "unknown"},    ← should be "required"
{"line": "- FastAPI", "requirement": "unknown"},   ← should be "required"
{"line": "Nice to have:", "requirement": "optional"},
{"line": "- Docker", "requirement": "unknown"},    ← should be "optional"
{"line": "- Kubernetes", "requirement": "unknown"} ← should be "optional"
```

The section header `Required:` is classified correctly, but the child items `-  Python`, `- FastAPI` are classified as `unknown` because they don't contain the keyword themselves.

### Source Evidence
JD1 output:
```json
{"line": "Requirements:", "requirement": "unknown"},   ← header itself not matching
{"line": "- Must have knowledge of Git", "requirement": "required"},  ← inline match works
{"line": "- Docker", "requirement": "unknown"}         ← context not inherited
```

JD2 output shows `"- Python": "unknown"` under `Required:` section.

### Expected
Once a section header matches `required` or `optional`, all subsequent lines until the next section header should inherit that classification. The parser should maintain a "current section mode" to propagate context.

### Impact
The `skill_requirements` output is misleading: skills listed under `Required:` are classified as `unknown`. Any downstream component relying on this field to distinguish required vs. optional skills cannot function correctly when skills are listed as section children rather than inline.

### Likely Area
`src/parsers/jd_parser.py` — `parse_jd()` calls `_classify_skill_requirement(line)` for each line independently with no state carryover from preceding section headers.

### Status
OPEN

---

## JD-005: Overall experience extraction fails for range-format `4-6 years` — picks only the higher number

- **Source:** JD8 test input
- **Category:** Incorrect Extraction
- **Severity:** P1

### Observed
`YOE_PATTERN` matches `\d+\+?` before `years?`. For `4-6 years of experience required`:

```
_extract_experience(['4-6 years of experience required.']) => 72  (i.e., 6 years)
```

The regex matches `6` (the number immediately before `years`), ignoring the range `4-6`. The minimum experience (`4` years) is discarded. The output says `experience_months: 72` (6 years) when the JD actually says "4 to 6 years".

### Source Evidence
JD8 test verified: `experience_months: 72` for `"4-6 years of experience required"`.

### Expected
Range-format experience requirements (`4-6 years`, `4 to 6 years`, `4–6 years`) should be represented as a range, not a single value. At minimum, the **minimum** of the range should be extracted (i.e., 4 years = 48 months), as it represents the threshold. Alternatively, both `min_experience_months` and `max_experience_months` should be stored.

### Impact
Matching logic using `experience_months` as a hard threshold may reject candidates with 4-5 years of experience when the JD says `4-6 years`. The schema cannot represent that experience is a range.

### Likely Area
`src/parsers/jd_parser.py` — `YOE_PATTERN` and `_extract_experience()`. `src/configs/jd_configs.py` — no range support.

### Status
OPEN

---

## JD-006: `_filter_noise_sections` requires exact lowercase match for noise headers — does not handle trailing colon variants or partial matches

- **Source:** JD tests
- **Category:** Generalization
- **Severity:** P2

### Observed
`_filter_noise_sections` normalizes the line as `line.lower().strip().rstrip(":")` and checks exact membership in `NOISE_SECTION_HEADERS`. This means:

- `About Us:` → normalized to `about us` → matches (`:` stripped). ✓
- `About Us` → `about us` → matches. ✓  
- `ABOUT THE COMPANY` → `about the company` → matches. ✓
- `About Our Company` → `about our company` → **does NOT match** (not in list).
- `Company Information` → **does NOT match**.
- `Why Join Us` → **does NOT match**.
- `What Makes Us Different` → **does NOT match**.
- `Life at [Company]` → **does NOT match**.

Verified: `_filter_noise_sections(['Role: Backend Engineer', 'About Us:', ...])` correctly filters `About Us:`. But many real noise headers are not covered.

### Source Evidence
`NOISE_SECTION_HEADERS` contains 15 specific strings. Common real-world noise headers not included: `company information`, `our culture`, `life at [company]`, `why join us`, `interview process`, `diversity and inclusion`, `our team`, `meet the team`, `about [company name]`.

### Expected
Noise section detection should be more flexible — pattern-based or using a wider vocabulary.

### Impact
Noise content from unrecognized headers leaks into the processed JD content. Skills mentioned in `About Our Company` sections (which are noise) may be incorrectly extracted. Overall experience mentioned in marketing text may pollute `experience_months`.

### Likely Area
`src/configs/jd_configs.py` — `NOISE_SECTION_HEADERS`. `src/parsers/jd_parser.py` — `_filter_noise_sections()`.

### Status
OPEN

---

## JD-007: `_extract_experience` returns `None` when only skill-specific experience exists — does not use skill-specific data as a fallback

- **Source:** JD7, JD3 test inputs
- **Category:** Information Loss
- **Severity:** P2

### Observed
When a JD has no overall experience requirement but has multiple skill-specific ones (e.g., `5 years of Python experience`, `3 years of SQL experience`), `_extract_experience` returns `None`:

```
_extract_experience(['5 years of experience in Python', '3 years of experience in SQL']) => None
```

This is by design (the YOE_PATTERN has a negative lookahead `(?!\s+(?:with|in)\b)` to avoid skill-specific matches). However, the output has:
```json
"experience_months": null,
"skill_specific_experience": [{"skill": "Python", "experience_months": 60}, ...]
```

The overall experience field is `null` even though there is rich skill-specific experience data.

Also confirmed for JD3:
```
We require candidates with 4 to 6 years of relevant experience.
```
This does not match `YOE_PATTERN` at all (it uses "relevant experience" not just "experience", and "4 to 6" is a range). So `experience_months: null` is returned even though the JD clearly states an experience requirement.

### Source Evidence
JD7 output: `"experience_months": null` despite having `5 years Python`, `3 years SQL`, `2 years AWS`.
JD3 output: `"experience_months": null` for `4 to 6 years of relevant experience`.

### Expected
`YOE_PATTERN` should cover more phrasings: `X to Y years`, `X-Y years of relevant experience`, `X years of relevant experience`, `X+ years of hands-on experience`, etc. When overall experience is null but skill-specific experience exists, this should be surfaced or at least noted.

### Impact
`experience_months: null` is an incomplete representation when the JD clearly has experience requirements. Downstream matching using `experience_months` as a filter will treat these JDs as having no experience requirement, accepting under-qualified candidates.

### Likely Area
`src/parsers/jd_parser.py` — `YOE_PATTERN`, `_extract_experience()`.

### Status
OPEN

---

## JD-008: Skills are not associated with their requirement level in a single unified structure — `skills` and `skill_requirements` are separate lists with no link

- **Source:** All JD inputs
- **Category:** Schema Limitation
- **Severity:** P2

### Observed
The JD parser returns two separate lists:
1. `skills` — a deduplicated list of skill names (e.g., `["Python", "FastAPI", "SQL"]`)
2. `skill_requirements` — a list of all lines with their classified requirement levels

There is no field that says "Python is required" or "Docker is optional" as a unified, per-skill object. To determine if a specific skill is required, a consumer must:
1. Find lines in `skill_requirements` where the skill name appears.
2. Read the `requirement` field of those lines.
3. Handle the case where the skill appears on multiple lines with different requirements.

But as shown in JD-004, most skill lines under a `Required:` section header are classified as `unknown`, making this join useless in practice.

### Source Evidence
JD1 output:
```json
"skills": ["React", "JavaScript", "TypeScript", "Node.js", "Git", "Docker", "AWS", "Kubernetes"],
"skill_requirements": [
  {"line": "- Strong proficiency in React and JavaScript", "requirement": "unknown"},
  ...
  {"line": "- AWS experience preferred", "requirement": "optional"},
  ...
]
```

There's no output saying `{"skill": "React", "requirement": "required"}`.

### Expected
A unified skill object: `{"skill": "React", "requirement": "required", "min_experience_months": null}` would allow downstream matching to directly compare candidate skills against typed JD requirements.

### Impact
Any downstream component wanting to distinguish required vs. optional skills must implement its own (fragile) join logic. The current schema cannot correctly answer "Is Python required for this JD?" without re-implementing classification logic.

### Likely Area
`src/parsers/jd_parser.py` — `parse_jd()` output schema. No per-skill requirement resolution.

### Status
OPEN

---

## JD-009: Noise section filtering is state-based and non-reentrant — if noise section has no following JD section, everything after it is silently dropped

- **Source:** JD tests
- **Category:** Information Loss
- **Severity:** P1

### Observed
`_filter_noise_sections()` uses a `noise_mode` flag. Once `noise_mode = True`, only lines that match `JD_SECTION_HEADERS` can turn it off. If a noise section appears at the **end** of the JD (after all requirement sections), everything from that point is correctly discarded — which is the intended behavior.

However, if a JD has:
```
Responsibilities:
...requirements here...

About the company
...noise...

Some non-standard section:
...more requirements here...
```

The `Some non-standard section:` would not be in `JD_SECTION_HEADERS`, so `noise_mode` stays `True` and the requirements after the noise section are dropped.

Verified:
```python
_filter_noise_sections([
    'Role: Backend Engineer',
    'Python',
    'About the company',
    'We build nice things.',
    'Compensation Details',   # not in JD_SECTION_HEADERS
    'Python 3 years'          # silently dropped
]) 
# => ['Role: Backend Engineer', 'Python']
```

### Source Evidence
Verified in the edge case test: once noise mode is activated, only `JD_SECTION_HEADERS` re-entry lines escape it. `Compensation Details` or `Applicant Requirements` or any non-standard section title would keep noise mode active.

### Expected
The noise filter should be more conservative: if it cannot determine whether content after a noise section is signal or noise, it should err on the side of preserving it, or use a timeout heuristic (e.g., "if N consecutive non-noise lines appear, exit noise mode").

### Impact
Requirements stated after a noise section (e.g., after an "About Us" block, then a "Compensation" block, then back to "Technical Requirements") are silently lost. Skills and experience requirements in those sections are not extracted.

### Likely Area
`src/parsers/jd_parser.py` — `_filter_noise_sections()`, lines 117-133.

### Status
OPEN

---

## JD-010: `TypeScript` is in `KNOWN_SKILLS` but not in `SKILL_YOE_PATTERN` or `skill_configs.py` — inconsistent between skill extraction and skill-specific experience

- **Source:** JD1 test
- **Category:** Other
- **Severity:** P3

### Observed
`TypeScript` appears in `KNOWN_SKILLS` and is correctly extracted as a skill. However, `SKILL_YOE_PATTERN` uses `KNOWN_SKILLS` to build its pattern. Since `TypeScript` is in `KNOWN_SKILLS`, it should be captured in skill-specific experience. Tested:

```
"2 years of TypeScript experience" → SKILL_YOE_PATTERN should match, skill_specific_experience should contain TypeScript
```

This works correctly for skills in `KNOWN_SKILLS`. The deeper issue is that `KNOWN_SKILLS` is the single source of truth for both skill detection AND skill-specific experience — which means any skill added to one is automatically added to both. This coupling is architecturally intentional but creates brittleness: a skill that should only be detected (not tracked for experience) cannot be added to skill detection alone.

Also: `React` is in `KNOWN_SKILLS` but the JD1 document uses `React` (matching), while the skills parser (resume side) uses `ReactJS` (normalized to `React`). The JD side correctly extracts `React` from `"React and JavaScript"`.

### Source Evidence
JD1 output: `"skills": ["React", "JavaScript", "TypeScript", "Node.js", "Git", "Docker", "AWS", "Kubernetes"]` — all correct.

### Expected
Minor: document the tight coupling between `KNOWN_SKILLS` and `SKILL_YOE_PATTERN`. Medium: provide a mechanism to add detection-only skills without making them eligible for YOE extraction.

### Impact
Low for current functionality. Becomes a problem if skills like `HTML` or `CSS` are added to `KNOWN_SKILLS` — they would be matched in `N years of HTML experience` sentences, which is unusual.

### Likely Area
`src/configs/skill_configs.py` — `KNOWN_SKILLS`. `src/parsers/jd_parser.py` — `SKILL_YOE_PATTERN` construction.

### Status
OPEN

---

## JD-011: `_extract_experience` joins all JD lines into a single string — can produce false matches from split contexts

- **Source:** All JD inputs
- **Category:** Incorrect Extraction
- **Severity:** P2

### Observed
```python
def _extract_experience(jd: list[str]) -> int | None:
    text = " ".join(jd)
    match = re.search(YOE_PATTERN, text)
```

All lines are joined with a space before applying the regex. This means if a line ends with `"3 years"` and the next line starts with `"of experience"`, the join creates `"3 years of experience"` which would match — even though these were separate lines with different semantic contexts. Conversely, a phrase spanning two lines in the original JD (before PDF extraction joins them) might be split differently.

Also: the first match is returned, ignoring any other matches. If a JD states multiple experience requirements (e.g., `"3+ years of Python experience"` AND `"5+ years of industry experience"`), only the first overall match is returned (whichever appears first in the joined text).

### Source Evidence
`text = " ".join(jd)` — line 85. Only `re.search` (first match) is used.

### Expected
Scan line-by-line for overall experience (like `_extract_skill_specific_experience` does) to avoid cross-line false matches. Return the maximum or the specifically-stated minimum, with documentation of the choice.

### Impact
Cross-line false matches may produce an experience requirement number from unrelated content. Single-match logic means multi-stated experience requirements are partially lost.

### Likely Area
`src/parsers/jd_parser.py` — `_extract_experience()` lines 84-98.

### Status
OPEN

---

## JD-012: `skill_requirements` is applied to every line including section headers and boilerplate — produces noisy output

- **Source:** All JD inputs
- **Category:** Information Loss / False Positive
- **Severity:** P2

### Observed
```python
"skill_requirements": [
    {"line": line, "requirement": _classify_skill_requirement(line)}
    for line in jd  # ALL lines, including headers, boilerplate
]
```

Every single line in the JD (after noise filtering) is included in `skill_requirements`, including:
- Section headers: `{"line": "Requirements:", "requirement": "unknown"}`
- General descriptions: `{"line": "We are looking for a skilled backend developer.", "requirement": "unknown"}`
- Experience lines: `{"line": "Minimum 5 years of professional experience.", "requirement": "unknown"}`

This produces large, noisy arrays where the vast majority of entries are `"requirement": "unknown"`.

JD2 output: 11 entries in `skill_requirements`, 9 of which are `"unknown"`.

### Source Evidence
JD2 output `skill_requirements` has 11 items for a short JD. Only 2 items (`Required:`, `Preferred:`) are not `unknown`. All individual skill lines (`- Python`, `- FastAPI`, etc.) are `unknown` despite being under `Required:`.

### Expected
`skill_requirements` should only contain lines that are skill-related, or at minimum filter out section headers and pure boilerplate. The requirement classification should be context-aware (see JD-004).

### Impact
Consumers of `skill_requirements` receive a large noisy array where `unknown` is the dominant value, making the field nearly useless for automated processing. The signal-to-noise ratio is very low.

### Likely Area
`src/parsers/jd_parser.py` — `parse_jd()` lines 208-214.

### Status
OPEN

---

## JD-013: JD service does not clean or normalize text before parsing — em-dashes, encoding artifacts, and PDF whitespace pass through unmodified

- **Source:** All JD inputs from PDF
- **Category:** Generalization
- **Severity:** P2

### Observed
For PDF-sourced JDs, `jd_service.py` calls `extract_text(content)` and immediately passes the result to `parse_jd(text)`. Unlike the resume service which calls `clean_text()` to normalize whitespace, tabs, and carriage returns, the JD service performs no text cleaning.

PDF text extraction may produce:
- Em-dashes (`–`) instead of hyphens
- Non-breaking spaces
- Ligature characters
- Encoding artifacts similar to those seen in `HARSHIT_WEBDEV.pdf`

### Source Evidence
`jd_service.py` lines 11-18:
```python
text = extract_text(content)
# ← no clean_text() call
jd = parse_jd(text)
```

vs. `resume_service.py` which calls `cleaned_text = clean_text(text)`.

### Expected
The JD service should apply the same `clean_text()` normalization before parsing, ensuring consistent behavior between text-input and PDF-input JDs.

### Impact
JDs submitted as PDFs may produce different (degraded) results compared to JDs submitted as plain text, due to unstripped whitespace or encoding artifacts. Duration patterns that rely on exact `-` or `–` characters may fail for PDF-extracted text with non-standard dashes.

### Likely Area
`src/services/jd_service.py` — no `clean_text()` call after `extract_text()`.

### Status
OPEN

---

## JD-014: No representation for education requirements in JD output schema

- **Source:** All JD inputs
- **Category:** Schema Limitation
- **Severity:** P2

### Observed
The JD parser output has no field for education requirements. Common JD statements like:
```
Bachelor's degree in Computer Science required
Master's degree preferred
B.Tech/B.E. in any engineering discipline
```
are never extracted or structured. They appear in `skill_requirements` as `"requirement": "unknown"` lines but are not parsed as education requirements.

### Source Evidence
`parse_jd()` returns:
```python
{"role", "experience_months", "skills", "skill_specific_experience", "skill_requirements"}
```
No `education_requirement` field.

### Expected
A field like `education_requirement: {"degree": "Bachelor's", "field": "Computer Science", "required": true}` would allow matching a candidate's education against the JD's requirement.

### Impact
Education requirements from JDs are not structured, so candidate-education vs. JD-requirement matching is impossible using the structured output. This is a significant gap for ATS-style filtering.

### Likely Area
`src/parsers/jd_parser.py` — no education requirement extraction. `src/services/jd_service.py` — schema gap.

### Status
OPEN

---

## JD-015: `_filter_noise_sections` comparison is exact-match after stripping — `"About Us:"` works but `"About Us - Our Story"` does not

- **Source:** Generalization
- **Category:** Generalization
- **Severity:** P3

### Observed
Noise filtering strips trailing `:` and lowercases, then checks exact membership in `NOISE_SECTION_HEADERS`. This means:
- `"About Us:"` → `"about us"` → match ✓
- `"About Us - Our Story"` → `"about us - our story"` → **no match** ✗
- `"About Us (Founded 2010)"` → `"about us (founded 2010)"` → **no match** ✗

Verified: `_filter_noise_sections(['Role: Backend Engineer', 'About Us:', ...])` works. But decorated variants do not.

### Source Evidence
`NOISE_SECTION_HEADERS` check: `normalized_line in NOISE_SECTION_HEADERS` — pure string equality after `lower().strip().rstrip(":")`.

### Expected
Noise section matching should use prefix/substring matching or keyword detection rather than exact equality.

### Impact
Noise content under decorated headers (`About Us - Company Overview`) is not filtered, leaking into skill extraction and requirement classification.

### Likely Area
`src/parsers/jd_parser.py` — `_filter_noise_sections()` line 122.

### Status
OPEN

---

## JD-016: Overall experience extraction fails for labeled `Experience: N+ years` format

- **Source:** `jd_ml_engineer_test.pdf`
- **Category:** Information Loss / Generalization
- **Severity:** P1

### Observed
In `jd_ml_engineer_test.pdf`, the experience requirement is stated as a dedicated metadata line:
```
Experience: 3+ years
```
`_extract_experience()` evaluates `YOE_PATTERN` and returns `None`.

### Source Evidence
Tested on `jd_ml_engineer_test.pdf`:
Line 3: `Experience: 3+ years`
Parser execution:
`_extract_experience(jd_lines)` evaluates `re.search(YOE_PATTERN, text)`.
Output: `None`. `experience_months` is recorded as `null`.

### Expected
The parser should recognize `Experience: <N>+ years` as an overall experience requirement and extract `36` months.

### Impact
Standard JDs that specify required experience in a header block (`Experience: 3+ years`, `Years of Experience: 5+`) fail overall experience extraction. Candidate matching and ATS filters cannot enforce seniority requirements.

### Root Cause
`YOE_PATTERN` in `src/parsers/jd_parser.py` (lines 31-51) only matches suffix phrasings like `\b\d+\+?\s+years?\s+of\s+experience\b` or `\d+\+?\s+years?\s+in\s+the\s+industry`. It lacks support for prefix label phrasings like `Experience:\s*\d+\+?\s*years`.

### Likely Area
`src/parsers/jd_parser.py` — `YOE_PATTERN` and `_extract_experience()`.

### Status
OPEN

---

## JD-017: `YOE_PATTERN` fails to extract required experience when formatted as `Minimum X+ years` with trailing qualifier or domain modifier

- **Source:** Real JDs — JD-01 (Meta), JD-04 (Databricks), JD-05 (Stripe), JD-08 (Uber) (Migrated from R-042)
- **Category:** Information Loss / Regex Limitation
- **Severity:** P1

### Observed
In `src/parsers/jd_parser.py`:
`YOE_PATTERN` has a strict negative lookahead `(?!\s+(?:with|in)\b)`:
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
- `Minimum 4+ years of professional experience in applied machine learning` (Meta) -> rejected by `(?!\s+(?:with|in)\b)` because of trailing `in applied machine learning`.
- `Minimum 3 years of software engineering experience` (Databricks) -> rejected because `software engineering` is not matched by `(?:professional\s+)?(?:industry\s+)?`.
- `5+ years of software engineering or machine learning experience` (Uber) -> rejected for the same reason.
Consequently, `_extract_experience()` returns `None`.

### Source Evidence
In 8 out of 9 real JDs tested (89%), `experience_months` was returned as `None`, despite explicit years of experience requirements in the text.

### Expected
The regex should permit flexible domain modifiers (e.g. `software engineering`, `applied machine learning`, `relevant`, `related`) and allow trailing `in <domain>` or `with <domain>` clauses when extracting overall experience requirements.

### Impact
ATS minimum experience filters fail to extract tenure constraints from the vast majority of real job postings (89% failure rate).

### Likely Area
`src/parsers/jd_parser.py` — `YOE_PATTERN` and `_extract_experience()`.

### Status
OPEN

---

## JD-018: JD Parser lacks structured section detector — flattens document into raw lines causing context loss across sections

- **Source:** Multi-section JDs (Synthetic & Real)
- **Category:** Architecture / Section Detection
- **Severity:** P1

### Observed
Unlike the resume processing pipeline which employs a dedicated `section_detector.py` to identify canonical section boundaries (`detect_sections()`), the JD parser (`src/parsers/jd_parser.py`) processes the entire job description as an unsegmented list of strings (`list[str]`).
The only section mechanism is `_filter_noise_sections()`, a brittle state machine looking for `NOISE_SECTION_HEADERS` and `JD_SECTION_HEADERS`.

As a consequence:
1. **Context Loss for Requirements (JD-004):** Lines under `Requirements:`, `Minimum Qualifications:`, and `Preferred Qualifications:` are not associated with a parent section object. The parser must guess line-by-line using `_classify_skill_requirement(line)`, leading to widespread misclassification or `unknown` tags.
2. **Brittle Noise Filtering (JD-006, JD-009, JD-015):** Because there is no structured AST/section hierarchy, noise filtering relies on exact string equality on line headers. If a noise section uses decorated text (`About Us - Our Story`), noise mode fails to activate. If valid content appears after a noise section with an unlisted header, valid content is silently dropped.
3. **Unstructured Output (JD-008, JD-014):** Skills, requirements, and qualifications cannot be related back to their respective sections (e.g., distinguishing "Required Skills" from "Nice-to-Have Skills" or extracting education requirements from an "Education & Certifications" section).

### Source Evidence
In `src/parsers/jd_parser.py`:
`parse_jd(text)` splits `text.splitlines()` into `jd_lines` and passes the flat list to `_filter_noise_sections(jd_lines)`, `_extract_role(clean_jd)`, `_extract_skills(clean_jd)`, `_extract_experience(clean_jd)`. No section boundaries or tokens are constructed.

### Expected
Implement a dedicated section detector for JDs (`detect_jd_sections()` or adapt `detect_sections()`) with canonical headers:
- `ROLE_OVERVIEW` / `ABOUT_THE_ROLE`
- `REQUIREMENTS` / `BASIC_QUALIFICATIONS` / `MINIMUM_QUALIFICATIONS`
- `PREFERRED_QUALIFICATIONS` / `BONUS` / `DESIRED`
- `RESPONSIBILITIES` / `WHAT_YOU_WILL_DO`
- `BENEFITS` / `PERKS`
- `COMPANY_INFO` / `ABOUT_US` (Noise)
- `EQUAL_OPPORTUNITY` (Noise)

Parsed sections should form an intermediate representation where downstream extractors (skills, role, experience, education) operate on their designated section scopes.

### Impact
JD parsing remains fragile, context-blind, and incapable of reliably distinguishing required from optional qualifications.

### Likely Area
`src/parsers/jd_parser.py`, `src/configs/jd_configs.py`, and a new or shared section detector.

### Status
OPEN

---

## Audit Summary — JD Parser

| | |
|---|---|
| **Documents tested** | 10 synthetic JD inputs + 1 real-world PDF fixture (`jd_ml_engineer_test.pdf`) + 9 real production JDs |
| **Unique issues found** | 18 |

### Issues by Severity

| Severity | Count | IDs |
|---|---|---|
| P0 | 1 | JD-001 |
| P1 | 7 | JD-002, JD-003, JD-004, JD-009, JD-016, JD-017, JD-018 |
| P2 | 8 | JD-005, JD-006, JD-007, JD-008, JD-011, JD-012, JD-013, JD-014 |
| P3 | 2 | JD-010, JD-015 |

### Top 5 Highest-Priority Issues

1. **JD-001 (P0)** — Only 17 skills recognized; any other skill (TensorFlow, PyTorch, MongoDB, scikit-learn, MLflow, etc.) is silently dropped — verified with Data Science JD and `jd_ml_engineer_test.pdf`.
2. **JD-018 (P1)** — Lack of structured section detection architecture causes total context loss between requirements, responsibilities, and noise.
3. **JD-004 (P1)** — `skill_requirements` classifier does not inherit context from section headers — items under `Required:` are classified `unknown`.
4. **JD-002 (P1)** — Role extraction only works with labeled `Role:`/`Position:`/`Job Title:` prefixes — fails for 55% of real-world JD formats (Meta, DeepMind, Databricks, Uber).
5. **JD-017 / JD-016 (P1)** — Labeled experience format (`Experience: 3+ years`) and domain qualifiers (`4+ years in ML`, `software engineering`) unparsed by `YOE_PATTERN` (89% failure rate on real JDs).

