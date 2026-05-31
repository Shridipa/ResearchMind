import argparse
import json
import statistics
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    args = parser.parse_args()
    rows = [json.loads(line) for line in Path(args.dataset).read_text(encoding="utf-8").splitlines()]
    metrics = {
        "examples": len(rows),
        "recall_at_5": 0.0,
        "mean_latency_ms": statistics.mean([0.0 for _ in rows]) if rows else 0.0,
        "note": "Wire this script to the FastAPI retriever after indexing benchmark papers.",
    }
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
