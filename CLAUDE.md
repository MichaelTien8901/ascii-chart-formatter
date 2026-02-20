# CLAUDE.md

## Project

ASCII Chart Formatter — fixes misaligned right edges in ASCII-art box diagrams caused by LLM character counting errors.

## Installation

```bash
# Install as a global CLI tool (recommended)
uv tool install /path/to/ascii-chart-formatter

# Or install into another project
uv add /path/to/ascii-chart-formatter

# Or install from a git repo
uv add git+https://github.com/youruser/ascii-chart-formatter
```

## Build & Test

```bash
uv sync --extra dev   # install with dev deps
uv run pytest         # run all tests
uv run pytest -x      # stop on first failure
```

## CLI Usage

```bash
fix-ascii-art [file]             # read file or stdin
fix-ascii-art -n [file]          # normalize Unicode to ASCII first
fix-ascii-art -m [file]          # markdown mode: only fix diagrams, skip tables
fix-ascii-art -i file.txt        # edit in place
fix-ascii-art -m -i doc.md       # fix markdown file in place
python -m ascii_chart_formatter  # alternative invocation
```

## Architecture

- `src/ascii_chart_formatter/chars.py` — character classification, Unicode-to-ASCII normalization maps
- `src/ascii_chart_formatter/formatter.py` — core algorithm: border detection, box matching, right-edge alignment fixing
- `src/ascii_chart_formatter/cli.py` — argparse CLI (stdin/file input, normalize flag, in-place edit)
- `tests/test_formatter.py` — comprehensive tests

### Core Algorithm

1. Optionally normalize Unicode chars to ASCII equivalents
2. Detect border segments on each line (corner + horizontal-fills + corner); supports multiple borders per line (side-by-side boxes)
3. Match top/bottom borders into box regions (same left column and character width)
4. Process innermost boxes first for nested structures
5. Fix content lines by finding the right `|` closest to expected position and adjusting padding
6. Pass through lines outside boxes unchanged
