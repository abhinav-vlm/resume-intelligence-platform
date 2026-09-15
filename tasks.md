Yes. Based on the audit results we have, one week is realistic, but I would not cram all 36 issues into seven giant "fix everything" sessions. Some issues are symptoms of the same architectural weakness.

For your 2-hour/day, max 5 blocks format, I'd plan 7 working days.

Parser Generalization & Hardening Week

Day	Focus	Main outcome

Day 1	Resume P0/P1 extraction	Fix critical information loss
Day 2	Resume structure & dates	Fix experience, projects, sections
Day 3	Resume schema + downstream contracts	Preserve information + prevent analyzer crashes
Day 4	JD skill extraction	Generalize skill vocabulary + extraction
Day 5	JD sections & requirements	Required/preferred context + section parsing
Day 6	JD role/experience/noise	Generalize role, YOE, filtering
Day 7	Full regression + hardening	Re-run entire corpus, close remaining issues


Day 1: Resume critical extraction

Priorities:

R-001  Skills disappearing
R-002  LinkedIn being discarded
R-009  Phantom projects

These are P0, so they get first priority.

We'll investigate the root causes, not patch individual PDFs.


---

Day 2: Resume structural robustness

Work through things like:

experience parsing
date formats
section detection
project boundaries
empty/missing sections
multi-page documents

This is where issues like R-009 should lead us to examine whether the project parser's assumptions about PDF blocks are fundamentally too brittle.


---

Day 3: Resume contract + information preservation

This is the important architecture day.

We'll examine:

PDF extraction
      ↓
parsers
      ↓
normalizers
      ↓
analyzers
      ↓
Resume Service

For each field:

> Does the information survive the entire pipeline?



And specifically deal with things like:

R-013 → quality analyzer crash
R-014 → achievements loss

We'll also decide which currently unsupported resume sections should become first-class schema fields versus being preserved generically.


---

Day 4: JD skill extraction

This is likely one of the larger fixes.

Starting with:

JD-001

We'll address the vocabulary problem without turning KNOWN_SKILLS into an enormous hand-maintained junk drawer.

Then test:

Python
Machine Learning
scikit-learn
PyTorch
TensorFlow
MLflow
MongoDB
...

against multiple JD formats.


---

Day 5: JD requirement intelligence

This is the big one we've already discovered.

Move from:

_classify_skill_requirement(line)

to something conceptually like:

section context
      ↓
skill extraction
      ↓
requirement association

So:

Required Skills
    Python
    FastAPI
    Docker

Preferred Skills
    AWS
    Kubernetes

becomes:

[
  {"skill": "Python", "requirement": "required"},
  {"skill": "FastAPI", "requirement": "required"},
  {"skill": "Docker", "requirement": "required"},
  {"skill": "AWS", "requirement": "optional"},
  {"skill": "Kubernetes", "requirement": "optional"}
]

rather than classifying every random line in the JD.

This is also the prerequisite for returning to P5D8 scoring.


---

Day 6: JD role + experience + noise

We'll tackle:

JD-002  role extraction
JD-003  experience phrasing
JD-009  noise filtering

plus related issues uncovered while fixing them.

The goal isn't to make 15 special cases.

It's:

different JD formats
        ↓
common intermediate representation


---

Day 7: Regression day

This day is not "fix whatever we forgot."

It's:

All resumes
    +
All JDs
    +
Existing unit tests
    +
Integration tests
        ↓
Current parser
        ↓
Compare outputs
        ↓
Remaining issues

Then we'll classify remaining issues into:

FIX NOW
DEFER TO PHASE 6
SCHEMA DECISION
ACCEPTED LIMITATION

That distinction matters.

For example, if a JD says:

> "Experience building scalable distributed systems"



and we don't have enough deterministic information to map that to a specific skill, that's not necessarily a parser failure. We shouldn't turn the deterministic parser into a fake semantic model just because humans enjoy vague job descriptions.


---

Daily 2-hour structure

We'll keep your normal format:

00:00–00:10  Revision / previous-day issues
00:10–00:30  Root-cause analysis
00:30–01:10  Implementation
01:10–01:40  Tests + regression
01:40–02:00  Review + progress + next-day setup

And after every block:

████░░░░░░ 40%

or whatever the actual progress is.

Expected result after Day 7

Ideally:

issues_resume.md
    P0 → 0
    P1 → 0 or explicitly deferred

issues_jd.md
    P0 → 0
    P1 → 0 or explicitly deferred

But I'm not going to promise zero issues before we've seen the actual fixes. The purpose of generalization is that the corpus can expose new issues while we're fixing the old ones.

Updated roadmap

I'd temporarily make the project roadmap:

PHASE 1  Resume Ingestion              ✅
PHASE 2  Resume Intelligence           ✅
PHASE 3  Resume Quality                ✅
PHASE 4  JD Intelligence               ✅*
         * Hardening sprint
PHASE 4.5 Parser Generalization        🔨 7 days
PHASE 5  Resume ↔ JD Matching          ⏸️
PHASE 6  ML/NLP Intelligence            ⏸️
PHASE 7  Backend + Production           ⏳
PHASE 8  Deployment + MLOps             ⏳

Seven days is the right initial allocation. If Day 7 reveals that we're still fixing foundational issues, we extend it rather than rushing into matching. A production system doesn't become production-ready because the roadmap has a date on it. Tragically, software has not yet learned to obey calendars.