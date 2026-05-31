.PHONY: backend frontend test benchmark

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && pytest ../tests tests

benchmark:
	python benchmarks/retrieval_benchmark.py --dataset data/eval/sample_qa.jsonl
