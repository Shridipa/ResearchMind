import argparse
import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    args = parser.parse_args()
    rows = load_jsonl(Path(args.dataset))
    print(json.dumps({"examples": len(rows), "status": "evaluation harness ready"}, indent=2))


if __name__ == "__main__":
    main()
