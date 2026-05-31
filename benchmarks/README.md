# Benchmarks

ResearchMind benchmark scripts are designed to make RAG quality measurable.

## Metrics

- Retrieval Recall@K
- Mean Reciprocal Rank
- Semantic answer similarity
- Response latency
- Citation coverage
- Unsupported claim rate
- Chunking strategy comparison
- Embedding model comparison

## Commands

```bash
python benchmarks/retrieval_benchmark.py --dataset data/eval/sample_qa.jsonl
```
