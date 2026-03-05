"""Command-line interface for tectra-verify."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

from . import verify


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="tectra-verify",
        description="Verify content provenance against the Tectra registry.",
    )
    parser.add_argument("files", nargs="+", metavar="FILE", help="File(s) to verify.")
    parser.add_argument(
        "--api-url",
        default="https://tectra.vision",
        metavar="URL",
        help="Tectra API base URL (default: https://tectra.vision).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON.",
    )
    args = parser.parse_args()

    exit_code = 0
    for path in args.files:
        try:
            result = verify(path, api_url=args.api_url)
            if args.json:
                import json
                import dataclasses
                print(json.dumps(dataclasses.asdict(result), default=str))
            else:
                print(f"\n── {path} ──")
                print(result)
            if not result.authentic:
                exit_code = 1
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            exit_code = 2
        except Exception as e:
            print(f"Error verifying {path}: {e}", file=sys.stderr)
            exit_code = 2

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
