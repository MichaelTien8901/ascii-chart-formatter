"""CLI for fix-ascii-art: read from stdin or file, fix alignment, write output."""

import argparse
import sys

from .formatter import fix_ascii_art


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="fix-ascii-art",
        description="Fix misaligned right edges in ASCII-art box diagrams.",
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="Input file (reads from stdin if omitted)",
    )
    parser.add_argument(
        "-n",
        "--normalize",
        action="store_true",
        help="Normalize Unicode box-drawing/arrow chars to ASCII equivalents",
    )
    parser.add_argument(
        "-m",
        "--markdown",
        action="store_true",
        help="Markdown mode: only fix diagrams inside code fences or auto-detected box regions",
    )
    parser.add_argument(
        "-i",
        "--in-place",
        action="store_true",
        help="Edit file in place (requires a file argument)",
    )

    args = parser.parse_args()

    if args.in_place and not args.file:
        parser.error("--in-place requires a file argument")

    if args.file:
        with open(args.file) as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    result = fix_ascii_art(text, normalize=args.normalize, markdown=args.markdown)

    if args.in_place:
        with open(args.file, "w") as f:
            f.write(result)
    else:
        sys.stdout.write(result)
