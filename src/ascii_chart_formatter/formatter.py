"""Core algorithm: box detection, alignment fixing."""

from __future__ import annotations

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
        # Consume horizontal fill and corner chars
        while j < len(line) and (line[j] in HORIZONTAL_FILL_CHARS or line[j] in CORNER_CHARS):
            j += 1
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
            i = right_col + 1
        else:
            i += 1
    return segments


def _find_borders(lines: list[str]) -> list[BorderInfo]:
    """Find all border segments across all lines."""
    borders: list[BorderInfo] = []
    for i, line in enumerate(lines):
        borders.extend(_find_border_segments(line, i))
    return borders


def _match_boxes(borders: list[BorderInfo]) -> list[BoxRegion]:
    """Match top borders with bottom borders to form box regions.

    A top border matches a bottom border if they share the same left_col
    and width, and the bottom is below the top with no intervening border
    at the same left_col and width.
    """
    used: set[int] = set()
    boxes: list[BoxRegion] = []

    # Sort by line index, then left_col
    sorted_borders = sorted(borders, key=lambda b: (b.line_index, b.left_col))

    for i, top in enumerate(sorted_borders):
        if i in used:
            continue
        # Look for the nearest matching bottom border
        for j in range(i + 1, len(sorted_borders)):
            if j in used:
                continue
            bottom = sorted_borders[j]
            if (
                bottom.left_col == top.left_col
                and bottom.width == top.width
            ):
                boxes.append(BoxRegion(top=top, bottom=bottom))
                used.add(i)
                used.add(j)
                break

    return boxes


def _fix_content_line(line: str, box: BoxRegion) -> str:
    """Fix a single content line within a box to align its right edge."""
    left_col = box.top.left_col
    target_width = box.top.width

    # Find left border char
    if left_col >= len(line):
        return line
    if not is_vertical_border_char(line[left_col]):
        return line

    # Find the right border char closest to the expected position.
    # This correctly handles side-by-side and nested boxes by not
    # grabbing a | that belongs to a different box.
    expected_right = left_col + target_width - 1
    right_idx = None
    best_dist = None
    for idx in range(left_col + 1, len(line)):
        if is_vertical_border_char(line[idx]):
            dist = abs(idx - expected_right)
            if best_dist is None or dist < best_dist:
                best_dist = dist
                right_idx = idx
            elif dist > best_dist:
                break  # Getting farther away, stop

    if right_idx is None:
        return line

    # Current width from left border to right border (inclusive) = character count
    current_width = right_idx - left_col + 1

    if current_width == target_width:
        return line  # Already aligned

    diff = target_width - current_width

    before_right = line[left_col:right_idx]
    after_right = line[right_idx:]

    if diff > 0:
        # Need more spaces before the right border
        return line[:left_col] + before_right + (" " * diff) + after_right
    else:
        # Need fewer spaces — remove spaces just before the right border
        remove = -diff
        trailing_spaces = len(before_right) - len(before_right.rstrip(" "))
        if trailing_spaces >= remove:
            trimmed = before_right[:len(before_right) - remove]
            return line[:left_col] + trimmed + after_right
        else:
            # Can't remove enough spaces; remove what we can
            trimmed = before_right.rstrip(" ")
            return line[:left_col] + trimmed + after_right


def _fix_lines(lines: list[str]) -> list[str]:
    """Fix misaligned right edges in a list of lines containing ASCII art."""
    borders = _find_borders(lines)
    boxes = _match_boxes(borders)

    if not boxes:
        return lines

    # Sort boxes innermost first (smallest line range first) so nested
    # boxes are fixed before their parents
    boxes.sort(key=lambda b: b.bottom.line_index - b.top.line_index)

    # Fix content lines within each box
    for box in boxes:
        for line_idx in range(box.top.line_index + 1, box.bottom.line_index):
            lines[line_idx] = _fix_content_line(lines[line_idx], box)

    return lines


def _has_box_chars(line: str) -> bool:
    """Check if a line contains box-drawing characters (borders or vertical edges)."""
    for ch in line:
        if ch in CORNER_CHARS or ch in HORIZONTAL_FILL_CHARS or is_vertical_border_char(ch):
            return True
    return False


def _find_diagram_regions(lines: list[str]) -> list[tuple[int, int]]:
    """Auto-detect regions of consecutive lines that contain box-drawing characters.

    Returns list of (start, end) line index pairs (inclusive).
    Gaps of up to 2 non-box lines (arrows, labels between boxes) are bridged.
    """
    # Find lines that have box chars
    box_lines: set[int] = set()
    for i, line in enumerate(lines):
        if _has_box_chars(line):
            box_lines.add(i)

    if not box_lines:
        return []

    # Build regions, bridging small gaps (up to 2 lines without box chars)
    sorted_indices = sorted(box_lines)
    regions: list[tuple[int, int]] = []
    start = sorted_indices[0]
    end = sorted_indices[0]

    for idx in sorted_indices[1:]:
        if idx - end <= 3:  # bridge gaps of up to 2 lines
            end = idx
        else:
            regions.append((start, end))
            start = idx
            end = idx
    regions.append((start, end))

    return regions


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

    if not markdown:
        lines = text.split("\n")
        lines = _fix_lines(lines)
        return "\n".join(lines)

    # Markdown mode: find diagram regions and fix only those
    lines = text.split("\n")

    # First pass: find code fence regions
    fence_regions: list[tuple[int, int]] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].lstrip()
        if stripped.startswith("```"):
            fence_start = i
            i += 1
            while i < len(lines) and not lines[i].lstrip().startswith("```"):
                i += 1
            if i < len(lines):
                fence_end = i
                # Check if this fence contains any box chars
                fence_content = lines[fence_start + 1 : fence_end]
                if any(_has_box_chars(line) for line in fence_content):
                    fence_regions.append((fence_start + 1, fence_end - 1))
            i += 1
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
