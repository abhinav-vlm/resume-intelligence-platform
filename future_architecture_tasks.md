# Future Architecture Tasks

> **NOTE:** These items are **NOT current defects**. They are architectural enhancements and intelligence-layer concerns for future phases.
> No source code, test files, or parsers need to be modified to address these items in Phase 4.5 or Phase 5.
> Do NOT treat these as bugs in the current implementation.

**Created:** 2026-09-29
**Context:** Phase 4.5 Day 7 -- JD-001 Resolved. Compound skill recognition and semantic validation are explicitly deferred here.

---

## FA-001: Compound Multi-Word Technology Name Recognition

**Category:** NLP / Vocabulary Intelligence
**Priority:** Future (Phase 6 or Phase 7)
**Blocking:** Nothing -- current extraction passes >90% coverage threshold.

### Background
The deterministic JD parser (`jd_parser.py`) and skill vocabulary (`skill_configs.py`) operate token-by-token. When a technology name is a compound of two common words (e.g., `Apache Spark`, `Delta Lake`, `Spring Boot`), the extractor may split it into individual constituent tokens rather than recognizing the compound as a single named entity.

### Evidence from Phase 4.5 Day 7 Validation
During Block 4 real-world JD validation (41/43 expected mentions, 95.3% coverage):
- **`Apache Spark`** -- `Apache` and `Spark` were each extracted individually; the compound phrase was not preserved as a single entity.
- **`Delta Lake`** -- `Delta` and `Lake` were each extracted individually; the compound phrase was not preserved.

Both constituent tokens are extracted correctly. The issue is solely at the compound-name recognition layer.

### Why This Is NOT a Current Defect
1. Individual tokens (`Apache`, `Spark`, `Delta`, `Lake`) are correctly extracted and preserved.
2. The 95.3% extraction coverage exceeds the >90% acceptance threshold.
3. The current parser is intentionally deterministic -- it is not designed to perform named entity recognition (NER) or compound phrase detection.
4. Fixing this requires a fundamentally different approach (NER model, n-gram vocabulary, or phrase dictionary) that belongs to the ML/NLP Intelligence phase.

### Recommended Future Approach
- **Phase 6:** Introduce a compound technology phrase dictionary (e.g., {"Apache Spark", "Delta Lake", "Spring Boot", "Apache Kafka", "Google Cloud", "Amazon Web Services"}) that is matched before tokenization.
- **Phase 7:** Train or fine-tune a NER model for technology entity recognition to handle arbitrary compound names.

---

## FA-002: Semantic Validation of Unknown Skill Candidates

**Category:** NLP / Semantic Intelligence
**Priority:** Future (Phase 6 or Phase 7)
**Blocking:** Nothing.

### Background
The current skill extractor preserves unknown candidates (tokens not in the taxonomy) as "unknown" skills rather than discarding them. This is the correct deterministic behavior. However, it does not validate whether a candidate is actually a technology/skill or is noise (e.g., a verb, an adjective, or a generic business phrase).

### Observed Pattern
When a JD contains phrases like "strong communication skills", the parser may preserve "communication" or "strong" as an unknown candidate because it is not in the known taxonomy. Conversely, a legitimate but rare technology like Zookeeper or Flink may appear as an unknown candidate alongside noise tokens.

### Why This Is NOT a Current Defect
1. Unknown candidates are preserved, not discarded -- no information is lost.
2. Semantic filtering is inherently a probability-based task requiring an ML/NLP layer.
3. Adding heuristic semantic guards risks creating false negatives (incorrectly discarding valid rare technologies).

### Recommended Future Approach
- **Phase 6:** Build a vocabulary confidence scorer using embedding similarity to a "technology name" seed set.
- **Phase 6:** Add a simple noun-phrase filter to prune clearly non-technical candidates via a stoplist.
- **Phase 7:** Use a classifier (logistic regression or fine-tuned BERT) trained on {technology, non-technology} labels to score candidates.

---

## FA-003: Vocabulary Evolution and Taxonomy Maintenance

**Category:** Configuration / Maintenance
**Priority:** Ongoing (Phase 5+)
**Blocking:** Nothing.

### Background
The skill taxonomy in `skill_configs.py` (expanded in Phase 4.5 Day 7) is a snapshot of the technology landscape as of 2026-09-29. Technology stacks evolve rapidly.

### Concerns
1. **Staleness:** Emerging technologies (LangChain, Weaviate, Pinecone, Mamba, etc.) may not be in the current taxonomy.
2. **Coverage gaps:** Domain-specific stacks (bioinformatics, embedded systems, fintech) are likely underrepresented.
3. **Alias conflicts:** Different spellings of the same technology (e.g., `scikit-learn` vs `Scikit-Learn` vs `sklearn`) may produce duplicates or misses.

### Why This Is NOT a Current Defect
The existing taxonomy covers the majority of mainstream JD skills. Coverage gaps for niche or emerging technologies are expected vocabulary limitations, not extraction defects.

### Recommended Future Approach
- **Ongoing:** Quarterly vocabulary review to update `skill_configs.py`.
- **Phase 6:** Self-updating vocabulary pipeline mining technology names from large JD corpora.
- **Phase 6:** Alias normalization rules to map variant spellings to canonical forms.

---

## FA-004: Deterministic Parser Boundary (Architecture Principle)

**Category:** Architecture Philosophy
**Priority:** Documentation / Team Alignment
**Blocking:** Nothing.

### Statement
The `jd_parser.py` is and should remain a **deterministic extraction engine**. Its job is to extract explicitly mentioned structured data from JD text using rules, patterns, and vocabulary lookups. It is NOT responsible for:

- Inferring skills not mentioned in the text.
- Semantically validating whether extracted tokens are true technologies.
- Resolving ambiguous compound names without explicit vocabulary support.
- Scoring or ranking extracted skills by importance.

All probabilistic, inference-based, and model-driven intelligence belongs in the **Phase 6 (ML/NLP Intelligence)** layer.

### Evaluation Guideline
When a new "extraction issue" is raised against the JD parser, evaluate:
1. Is the information **present in the JD text**? If not, the parser cannot extract it -- expected behavior, not a defect.
2. Is the information **explicitly mentioned** vs. implied? Implicit signals require inference, not extraction.
3. Is the failure **deterministic** (pattern gap, vocabulary gap) or **probabilistic** (ambiguous text, compound names)? Pattern/vocabulary gaps may be fixable in Phase 4.5; probabilistic failures belong in Phase 6.

---
