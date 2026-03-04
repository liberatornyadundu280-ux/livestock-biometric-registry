import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.reconciliation import generate_registry_report, reconcile_registry


def main():
    parser = argparse.ArgumentParser(description="Inspect/repair MongoDB <-> FAISS registry drift.")
    parser.add_argument(
        "--repair",
        action="store_true",
        help="Rebuild FAISS index from MongoDB after reporting state.",
    )
    args = parser.parse_args()

    if args.repair:
        result = reconcile_registry()
        print(json.dumps(result, indent=2))
        return

    report = generate_registry_report()
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
