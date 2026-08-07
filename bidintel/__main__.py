"""CLI entry: python -m bidintel build-kb | answer | answer-all."""

from __future__ import annotations

import sys


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: python -m bidintel <build-kb|answer|answer-all> [args...]",
            file=sys.stderr,
        )
        sys.exit(1)

    cmd = sys.argv[1]
    sys.argv = [sys.argv[0]] + sys.argv[2:]

    if cmd in ("build-kb", "build_kb"):
        from bidintel.build_kb import main as build_main

        build_main()
    elif cmd == "answer":
        from bidintel.answer import main as answer_main

        answer_main()
    elif cmd in ("answer-all", "answer_all"):
        from bidintel.answer_all import main as answer_all_main

        answer_all_main()
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
