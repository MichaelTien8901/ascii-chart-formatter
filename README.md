# ASCII Chart Formatter

Fixes misaligned right edges in ASCII-art box diagrams caused by LLM character counting errors.

## The Problem

LLMs frequently miscount characters when generating ASCII box diagrams, causing right border characters to be misaligned:

```
+-------------------+
| User Request       |   <-- right edge too far
+-------------------+
| Parse & Validate |     <-- right edge too close
+-------------------+
```

## The Fix

```bash
fix-ascii-art diagram.txt
```

```
+-------------------+
| User Request      |   <-- aligned
+-------------------+
| Parse & Validate  |   <-- aligned
+-------------------+
```

## Installation

```bash
# Install as a global CLI tool (recommended)
uv tool install /path/to/ascii-chart-formatter

# Or install into another project
uv add /path/to/ascii-chart-formatter

# Or install from git
uv add git+https://github.com/MichaelTien8901/ascii-chart-formatter
```

## Usage

```bash
fix-ascii-art [file]             # read file or stdin, print to stdout
fix-ascii-art -i file.txt        # edit file in place
fix-ascii-art -m doc.md          # markdown mode: only fix diagrams, skip tables
fix-ascii-art -m -i doc.md       # fix markdown file in place
fix-ascii-art -n [file]          # normalize Unicode box chars to ASCII
python -m ascii_chart_formatter  # alternative invocation
```

### Markdown Mode (`-m`)

When processing markdown files, only diagrams are fixed — markdown tables and other content are left untouched. Diagrams are found inside code fences or auto-detected by looking for clusters of box-drawing characters.

## What It Handles

- Simple boxes, stacked boxes, side-by-side boxes, and nested boxes
- Both ASCII (`+`, `-`, `|`) and Unicode (`┌`, `─`, `│`) box-drawing characters
- Optional normalization of Unicode chars to ASCII equivalents (`-n`)
- Markdown files with mixed content (`-m`)

## Claude Code Skill

This project includes a `/fix-ascii-art` skill for Claude Code. It fixes ASCII art diagrams in place within your files.

## Development

```bash
uv sync --extra dev   # install with dev deps
uv run pytest         # run all tests
uv run pytest -x      # stop on first failure
```
