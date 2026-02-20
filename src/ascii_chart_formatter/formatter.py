"""Core algorithm: box detection, alignment fixing."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from .chars import (
    CORNER_CHARS,
    HORIZONTAL_FILL_CHARS,
    is_vertical_border_char,
    normalize_string,
)


@dataclass
class BorderInfo:
    """Information about a detected border line."""

    line_index: int
    left_col: int   # character index of left corner
    right_col: int  # character index of right corner
    width: int      # character count from left corner to right corner (inclusive)


@dataclass
class BoxRegion:
    """A matched pair of top/bottom borders defining a box."""

    top: BorderInfo
    bottom: BorderInfo


def _find_border_segments(line: str, line_index: int) -> list[BorderInfo]:
    """Find all border segments within a single line.

    A border segment is: corner char + one or more horizontal fill/corner chars + corner char.
    Multiple borders can exist on the same line (side-by-side boxes).

    When a corner char is encountered mid-scan, it ends the current segment
    if the next char is NOT a horizontal fill char (i.e. it's a true right corner,
    not a T-junction). The ending corner can then be re-examined as a new left corner.
    """
    segments: list[BorderInfo] = []
    i = 0
    while i < len(line):
        if line[i] not in CORNER_CHARS:
            i += 1
            continue
        # Found a potential left corner at position i
        left_col = i
        j = i + 1
        # Consume horizontal fill chars and corner chars (T-junctions)
        while j < len(line):
            if line[j] in HORIZONTAL_FILL_CHARS:
                j += 1
            elif line[j] in CORNER_CHARS:
                # Check if this corner is a T-junction (next char is fill)
                # or a true right corner (next char is not fill / end of line)
                if j + 1 < len(line) and line[j + 1] in HORIZONTAL_FILL_CHARS:
                    # T-junction: continue scanning
                    j += 1
                else:
                    # True right corner: end the segment here
                    j += 1
                    break
            else:
                break
        # j is now past the end of the border segment
        right_col = j - 1
        if right_col > left_col + 1 and line[right_col] in CORNER_CHARS:
            width = right_col - left_col + 1
            segments.append(BorderInfo(
                line_index=line_index,
                left_col=left_col,
                right_col=right_col,
                width=width,
            ))
            # Re-examine right_col as a potential new left corner
            i = right_col
        else:
            i += 1
    return segments


def _find_borders(lines: list[str]) -> list[BorderInfo]:
    """Find all border segments across all lines."""
    borders: list[BorderInfo] = []
    for i, line in enumerate(lines):
        borders.extend(_find_border_segments(line, i))
    return borders


def _match_boxes(borders: list[BorderInfo], lines: list[str]) -> list[BoxRegion]:
    """Match top borders with bottom borders to form box regions.

    A top border matches a bottom border if they share the same left_col
    and width, and the bottom is below the top with no intervening border
    at the same left_col and width.

    A border may serve as both a bottom and a top (shared border in stacked
    boxes), but only when the line immediately below it contains a vertical
    border char at left_col — proving it is genuine box content, not an
    arrow or gap line between separate boxes.

    Invariant: overlapping box regions cannot occur because each border is
    used at most once as a top and once as a bottom.
    """
    used_as_top: set[int] = set()
    used_as_bottom: set[int] = set()
    boxes: list[BoxRegion] = []

    # Sort by line index, then left_col
    sorted_borders = sorted(borders, key=lambda b: (b.line_index, b.left_col))

    for i, top in enumerate(sorted_borders):
        if i in used_as_top:
            continue
        # A border already used as a bottom may only be reused as a top
        # if the very next line has a | at left_col (stacked box content).
        if i in used_as_bottom:
            next_line = top.line_index + 1
            if (
                next_line >= len(lines)
                or top.left_col >= len(lines[next_line])
                or not is_vertical_border_char(lines[next_line][top.left_col])
            ):
                continue
        # Look for the nearest matching bottom border
        for j in range(i + 1, len(sorted_borders)):
            if j in used_as_bottom:
                continue
            bottom = sorted_borders[j]
            if (
                bottom.left_col == top.left_col
                and bottom.width == top.width
            ):
                boxes.append(BoxRegion(top=top, bottom=bottom))
                used_as_top.add(i)
                used_as_bottom.add(j)
                break

    return boxes


def _display_width(s: str) -> int:
    """Return the display width of a string, accounting for CJK/fullwidth chars.

    Characters with East Asian Width 'W' (wide) or 'F' (fullwidth) count as
    2 columns; all others count as 1.
    """
    width = 0
    for ch in s:
        eaw = unicodedata.east_asian_width(ch)
        width += 2 if eaw in ("W", "F") else 1
    return width


def _pad_or_trim_to_width(s: str, target: int) -> str:
    """Pad with spaces or trim trailing spaces so display width equals target."""
    current = _display_width(s)
    if current < target:
        return s + " " * (target - current)
    elif current > target:
        # Trim trailing spaces to reduce width
        while current > target and s.endswith(" "):
            s = s[:-1]
            current -= 1
    return s


def _fix_content_line(line: str, box: BoxRegion) -> str:
    """Fix a single content line within a box to align its right edge."""
    left_col = box.top.left_col
    target_width = box.top.width

    if left_col >= len(line):
        return line

    # Find left border char at or near expected position.
    # Search right first (common in side-by-side boxes with extra gap spacing),
    # then left as fallback. Wide search window catches more drift.
    left_idx = None
    for idx in range(left_col, min(len(line), left_col + 16)):
        if is_vertical_border_char(line[idx]):
            left_idx = idx
            break
    if left_idx is None:
        for idx in range(left_col - 1, max(-1, left_col - 12), -1):
            if is_vertical_border_char(line[idx]):
                left_idx = idx
                break
    if left_idx is None:
        return line

    # Find the right border char closest to the expected position.
    # Use left_idx (not left_col) as anchor since the content may be shifted.
    expected_right = left_idx + target_width - 1
    right_idx = None
    best_dist = None
    for idx in range(left_idx + 1, len(line)):
        if is_vertical_border_char(line[idx]):
            dist = abs(idx - expected_right)
            if best_dist is None or dist < best_dist:
                best_dist = dist
                right_idx = idx
            elif dist > best_dist:
                break  # Getting farther away, stop

    if right_idx is None:
        return line

    # Build the fixed box content with exact target_width
    inner = line[left_idx + 1:right_idx]
    target_inner = target_width - 2
    inner = _pad_or_trim_to_width(inner, target_inner)

    fixed_box = line[left_idx] + inner + line[right_idx]

    # Reconstruct the line, placing the fixed box at left_col.
    # Adjust the prefix (content before the box) to end at left_col.
    prefix = line[:left_idx]
    suffix = line[right_idx + 1:]

    if left_idx > left_col:
        # Trim trailing spaces from prefix to shift box left
        prefix = prefix[:left_col]
    elif left_idx < left_col:
        # Pad prefix with spaces to shift box right
        prefix = prefix + " " * (left_col - left_idx)

    return prefix + fixed_box + suffix


def _fix_lines(lines: list[str]) -> list[str]:
    """Fix misaligned right edges in a list of lines containing ASCII art."""
    # Expand tabs before any processing
    lines = [line.expandtabs(4) for line in lines]

    for _iteration in range(2):
        borders = _find_borders(lines)
        boxes = _match_boxes(borders, lines)

        if not boxes:
            return lines

        # Pass 1: check if any box needs border extension (content wider than box)
        extended = False
        for box in boxes:
            max_needed = 0
            for line_idx in range(box.top.line_index + 1, box.bottom.line_index):
                content_line = lines[line_idx]
                # Find the inner content between vertical borders
                left_col = box.top.left_col
                if left_col >= len(content_line):
                    continue
                # Find left |
                li = None
                for idx in range(left_col, min(len(content_line), left_col + 16)):
                    if is_vertical_border_char(content_line[idx]):
                        li = idx
                        break
                if li is None:
                    continue
                # Find right |
                expected_right = li + box.top.width - 1
                ri = None
                best_dist = None
                for idx in range(li + 1, len(content_line)):
                    if is_vertical_border_char(content_line[idx]):
                        dist = abs(idx - expected_right)
                        if best_dist is None or dist < best_dist:
                            best_dist = dist
                            ri = idx
                        elif dist > best_dist:
                            break
                if ri is None:
                    continue
                inner = content_line[li + 1:ri]
                needed = _display_width(inner.rstrip()) + 2  # +2 for borders
                if needed > max_needed:
                    max_needed = needed

            if max_needed > box.top.width:
                # Extend borders
                extra = max_needed - box.top.width
                for border in (box.top, box.bottom):
                    bline = lines[border.line_index]
                    # Find the fill char used in this border
                    fill_char = "-"
                    for ch in bline[border.left_col + 1:border.right_col]:
                        if ch in HORIZONTAL_FILL_CHARS:
                            fill_char = ch
                            break
                    # Insert extra fill chars before the right corner
                    rc = border.right_col
                    lines[border.line_index] = (
                        bline[:rc] + fill_char * extra + bline[rc:]
                    )
                    border.right_col += extra
                    border.width += extra
                extended = True

        if extended:
            # Re-detect after extension
            continue

        # Pass 2: fix content lines normally
        # Sort boxes innermost first (smallest line range first) so nested
        # boxes are fixed before their parents
        boxes.sort(key=lambda b: b.bottom.line_index - b.top.line_index)

        # Build a mapping of line index -> list of boxes that span it,
        # preserving innermost-first order within each line.
        line_boxes: dict[int, list[BoxRegion]] = {}
        for box in boxes:
            for line_idx in range(box.top.line_index + 1, box.bottom.line_index):
                line_boxes.setdefault(line_idx, []).append(box)

        # Fix content lines. For each line, sort boxes by line range ascending
        # (innermost first), then left_col ascending (left-to-right for
        # side-by-side).  Left-to-right ensures that fixing a left box shifts
        # content so the right box's | moves closer to its expected position
        # before we process it.
        for line_idx in sorted(line_boxes):
            for box in sorted(
                line_boxes[line_idx],
                key=lambda b: (b.bottom.line_index - b.top.line_index, b.top.left_col),
            ):
                lines[line_idx] = _fix_content_line(lines[line_idx], box)

        return lines

    return lines


def _has_box_chars(line: str) -> bool:
    """Check if a line contains box-drawing characters (borders or vertical edges)."""
    for ch in line:
        if ch in CORNER_CHARS or ch in HORIZONTAL_FILL_CHARS or is_vertical_border_char(ch):
            return True
    return False


def fix_ascii_art(text: str, normalize: bool = False, markdown: bool = False) -> str:
    """Fix misaligned right edges in ASCII-art box diagrams.

    Args:
        text: The ASCII art text to fix.
        normalize: If True, replace Unicode box-drawing/arrow chars with ASCII.
        markdown: If True, only fix diagrams inside code fences or auto-detected
                  box regions, leaving other markdown content untouched.

    Returns:
        The fixed text with aligned box edges.
    """
    if normalize:
        text = normalize_string(text)

    # Expand tabs before processing
    text = text.expandtabs(4)

    if not markdown:
        lines = text.split("\n")
        lines = _fix_lines(lines)
        return "\n".join(lines)

    # Markdown mode: find diagram regions and fix only those.
    # Note: +--+--+ style tables are structurally identical to boxes, so
    # auto-detection correctly treats them as fixable regions. The -m flag
    # user opted into diagram fixing, and aligned tables are desirable.
    lines = text.split("\n")

    # First pass: find code fence regions (``` or ~~~)
    fence_regions: list[tuple[int, int]] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].lstrip()
        fence_marker = None
        if stripped.startswith("```"):
            fence_marker = "```"
        elif stripped.startswith("~~~"):
            fence_marker = "~~~"
        if fence_marker is not None:
            fence_start = i
            i += 1
            while i < len(lines) and not lines[i].lstrip().startswith(fence_marker):
                i += 1
            if i < len(lines):
                fence_end = i
            else:
                # Unclosed fence: treat everything to end as fenced (CommonMark)
                fence_end = len(lines) - 1
            # Check if this fence contains any box chars
            if i < len(lines):
                fence_content = lines[fence_start + 1 : fence_end]
            else:
                fence_content = lines[fence_start + 1 : fence_end + 1]
            if any(_has_box_chars(line) for line in fence_content):
                if i < len(lines):
                    fence_regions.append((fence_start + 1, fence_end - 1))
                else:
                    fence_regions.append((fence_start + 1, fence_end))
            i = fence_end + 1
        else:
            i += 1

    # Collect all line indices covered by fences
    fenced_lines: set[int] = set()
    for start, end in fence_regions:
        fenced_lines.update(range(start, end + 1))

    # Second pass: auto-detect diagram regions outside fences
    unfenced_lines = [
        i for i in range(len(lines))
        if i not in fenced_lines and _has_box_chars(lines[i])
    ]
    auto_regions: list[tuple[int, int]] = []
    if unfenced_lines:
        start = unfenced_lines[0]
        end = unfenced_lines[0]
        for idx in unfenced_lines[1:]:
            if idx - end <= 3:
                end = idx
            else:
                auto_regions.append((start, end))
                start = idx
                end = idx
        auto_regions.append((start, end))

    # Fix each region independently
    all_regions = fence_regions + auto_regions
    for region_start, region_end in all_regions:
        region_lines = lines[region_start : region_end + 1]
        fixed = _fix_lines(region_lines)
        lines[region_start : region_end + 1] = fixed

    return "\n".join(lines)
