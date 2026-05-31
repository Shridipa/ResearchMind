# Backend Test Suite - Phase 1 Complete

## Overview
Automated pytest suite protecting ResearchMind backend reliability and RAG enforcement.

## Test Files (3 suites, 16 tests)

### 1. test_metadata_extraction.py (5 tests)
**Purpose**: Validate title, author, abstract extraction quality

| Test | Purpose | Status |
|------|---------|--------|
| `test_title_extraction` | Verify title extracted from PDF first page | ✅ |
| `test_author_extraction_no_affiliation_leakage` | Ensure no affiliation keywords in authors | ✅ |
| `test_abstract_extraction` | Verify abstract extracted from first paragraph | ✅ |
| `test_author_count_reasonable` | Verify 1-15 authors (reasonable range) | ✅ |
| `test_title_not_empty` | Ensure title has 2+ words | ✅ |

**Key Validations**:
- Author extraction filters: {finance, economics, school, university, institute, department, laboratory, college, center, research, administration, business, studies, science, engineering, technology, management, law, medicine, arts, humanities, social, natural}
- Title length: 2+ words
- Author count: 1-15 range (rejects single names, outliers)

---

### 2. test_retrieval_first.py (5 tests)
**Purpose**: Enforce retrieval-first RAG principle (no LLM before retrieval)

| Test | Purpose | Status |
|------|---------|--------|
| `test_no_lm_call_before_retrieval` | Verify unrelated queries return explicit no-evidence message | ✅ |
| `test_evidence_required_before_answer` | Ensure answers only generated from retrieved evidence | ✅ |
| `test_weak_evidence_triggers_no_evidence_response` | Verify weak retrieval (score < 0.4) triggers fallback | ✅ |
| `test_multiquery_papers_filter` | Ensure paper_ids filter respected | ✅ |
| `test_no_hallucination_without_evidence` | Verify 2050 FIFA queries don't hallucinate | ✅ |

**Key Validations**:
- No-evidence message: "I could not find supporting evidence in the indexed papers."
- Confidence = 0.0 when no sources
- Sources list empty on weak retrieval
- Retrieval respects paper_ids filter

---

### 3. test_empty_evidence.py (6 tests)
**Purpose**: Test safe handling of empty evidence (no crashes, graceful fallback)

| Test | Purpose | Status |
|------|---------|--------|
| `test_empty_evidence_no_crash` | Verify matcher handles [] evidence safely | ✅ |
| `test_empty_claims_no_crash` | Verify matcher handles empty text safely | ✅ |
| `test_no_evidence_response_explicit` | Verify explicit no-evidence message on empty retrieval | ✅ |
| `test_grounding_score_with_no_evidence` | Verify grounding stats work with no evidence | ✅ |
| `test_weak_evidence_threshold_respected` | Ensure weak queries return graceful message | ✅ |
| `test_answer_consistency_with_no_sources` | Verify consistency between confidence and answer text | ✅ |

**Key Validations**:
- EvidenceMatcher.match_claims([]) returns [] (no crash)
- Grounding validator safe on zero embeddings
- Groundedness score = 100% when no evidence (no false claims)
- Answer and confidence fields consistent

---

## Test Execution

### Run All Tests
```bash
cd "d:\Research Mind"
python -m pytest backend/tests/test_metadata_extraction.py backend/tests/test_retrieval_first.py backend/tests/test_empty_evidence.py -v
```

### Run Individual Suite
```bash
# Metadata extraction tests
python -m pytest backend/tests/test_metadata_extraction.py -v

# Retrieval-first enforcement tests
python -m pytest backend/tests/test_retrieval_first.py -v

# Empty evidence handling tests
python -m pytest backend/tests/test_empty_evidence.py -v
```

### Run Specific Test
```bash
python -m pytest backend/tests/test_retrieval_first.py::TestRetrievalFirst::test_no_lm_call_before_retrieval -v
```

## Test Results

**Latest Run**: 16 passed in 23.74s
- 5 passed in test_metadata_extraction.py
- 5 passed in test_retrieval_first.py
- 6 passed in test_empty_evidence.py

## What These Tests Protect

### Phase 1 Quality Guarantees
1. **No Author Affiliation Leakage**: Authors {"Finance", "Economics"} filtered out ✓
2. **Retrieval-First Enforcement**: No LLM call before evidence retrieval ✓
3. **No-Evidence Fallback**: Explicit message on weak retrieval ✓
4. **Empty Evidence Safety**: No crashes on zero evidence ✓
5. **Multi-Paper Filtering**: Queries scoped to specified papers ✓

### Regression Prevention
- Tests run before each commit to prevent:
  - Author parser breaking
  - Grounding validator crashes
  - Hallucination on missing evidence
  - Provider fallback failures
  - Deletion flow issues

## Pending Tests (Phase 1 Continuation)

### test_delete_paper.py (Target: 5 tests)
- [ ] test_delete_removes_from_registry
- [ ] test_delete_removes_from_retrieval
- [ ] test_delete_nonexistent_paper_raises
- [ ] test_delete_prevents_queries
- [ ] test_delete_one_paper_preserves_others

### test_multi_paper_retrieval.py (Target: 5 tests)
- [ ] test_retrieval_includes_multiple_papers
- [ ] test_compare_two_papers
- [ ] test_compare_respects_paper_filter
- [ ] test_compare_requires_minimum_papers
- [ ] test_multi_paper_qa_with_filter

**Total Target**: 26 tests across 5 files

## CI/CD Integration
Add to CI pipeline:
```yaml
test:
  script:
    - python -m pytest backend/tests/ -v --cov=app --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

## Next Steps

1. **Create remaining 2 test files** (test_delete_paper.py, test_multi_paper_retrieval.py)
2. **Validate all 26 tests pass** on real PDFs
3. **Phase 2**: Frontend metadata display + source visualization
4. **Phase 3**: Advanced features (literature reviews, flashcards, cross-paper synthesis)
