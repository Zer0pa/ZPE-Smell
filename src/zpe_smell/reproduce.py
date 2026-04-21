from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evaluation import AUTHORITY_SOURCE_COMMIT, evaluate_public_surface


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproduce the public smell evaluation artifact.")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "validation" / "results" / "latest_public_eval.json",
        help="Path to the output JSON file.",
    )
    args = parser.parse_args()

    result = evaluate_public_surface(source_commit=AUTHORITY_SOURCE_COMMIT)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
