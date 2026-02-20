# fix-ascii-art

Fix misaligned right edges in ASCII-art box diagrams, in place.

## Instructions

When the user invokes `/fix-ascii-art`, find and fix ASCII art box diagrams so that right edges align properly with their border lines.

### Workflow

1. Identify the file containing the ASCII art:
   - If `$ARGUMENTS` contains a filename, use that file.
   - Otherwise, ask the user which file to fix.
2. Run `fix-ascii-art -i <filename>` to fix the file in place.
   - Add `-m` for markdown files (`.md`) — this only fixes diagrams inside code fences or auto-detected box regions, leaving tables and other content untouched.
   - Add `-n` if the user wants Unicode box-drawing chars normalized to ASCII.
3. Read the fixed file and show the result to the user.

### What it fixes

LLMs frequently miscount characters when generating ASCII box diagrams, causing right border characters (`|`, `│`) to be misaligned with the top/bottom border lines. This tool detects box borders, calculates the correct width, and adjusts spacing so right edges line up.

It handles:
- Simple boxes, stacked boxes, side-by-side boxes, and nested boxes
- Both ASCII (`+`, `-`, `|`) and Unicode (`┌`, `─`, `│`) box-drawing characters
- Optional normalization of Unicode chars to ASCII equivalents (`-n` flag)

## allowed-tools

- Bash
- Read
- Write
