"""Tests for ASCII chart formatter."""

from ascii_chart_formatter.chars import (
    CORNER_CHARS,
    HORIZONTAL_FILL_CHARS,
    VERTICAL_BORDER_CHARS,
    is_vertical_border_char,
    normalize_string,
)
from ascii_chart_formatter.formatter import fix_ascii_art


# ── Character classification ────────────────────────────────────────

class TestCharSets:
    def test_ascii_corner(self):
        assert "+" in CORNER_CHARS

    def test_unicode_corners(self):
        for ch in "┌┐└┘├┤┬┴┼╔╗╚╝╠╣╦╩╬╭╮╰╯┏┓┗┛":
            assert ch in CORNER_CHARS, f"{ch!r} should be in CORNER_CHARS"

    def test_horizontal_fills(self):
        for ch in "─━═-":
            assert ch in HORIZONTAL_FILL_CHARS

    def test_vertical_borders(self):
        for ch in "│║┃|":
            assert ch in VERTICAL_BORDER_CHARS
            assert is_vertical_border_char(ch)

    def test_not_vertical(self):
        assert not is_vertical_border_char("-")
        assert not is_vertical_border_char("+")
        assert not is_vertical_border_char("a")

    def test_mixed_weight_corners(self):
        """Mixed-weight box-drawing corners are recognized."""
        for ch in "╒╕╘╛╓╖╙╜╞╡╤╧╪╟╢╥╨╫┍┎┑┒┕┖┙┚┝┞┟┠┡┢┥┦┧┨┩┪┭┮┯┰┱┲┵┶┷┸┹┺┽┾┿":
            assert ch in CORNER_CHARS, f"{ch!r} should be in CORNER_CHARS"

    def test_dashed_line_chars(self):
        """Dashed horizontal and vertical variants are recognized."""
        for ch in "┄┅┈┉":
            assert ch in HORIZONTAL_FILL_CHARS, f"{ch!r} should be in HORIZONTAL_FILL_CHARS"
        for ch in "┆┇┊┋":
            assert ch in VERTICAL_BORDER_CHARS, f"{ch!r} should be in VERTICAL_BORDER_CHARS"


# ── Normalization ───────────────────────────────────────────────────

class TestNormalization:
    def test_arrow_normalization(self):
        assert normalize_string("→") == "->"
        assert normalize_string("←") == "<-"

    def test_box_normalization(self):
        assert normalize_string("┌──┐") == "+--+"
        assert normalize_string("│") == "|"
        assert normalize_string("└──┘") == "+--+"

    def test_mixed_content(self):
        assert normalize_string("│ hello │") == "| hello |"

    def test_no_normalization_needed(self):
        assert normalize_string("hello") == "hello"

    def test_double_arrow(self):
        assert normalize_string("⇒") == "=>"

    def test_triangle_arrows(self):
        assert normalize_string("▼") == "v"
        assert normalize_string("▲") == "^"


# ── Simple box alignment ───────────────────────────────────────────

class TestSimpleBoxAlignment:
    def test_already_aligned(self):
        text = (
            "+--------+\n"
            "| hello  |\n"
            "+--------+"
        )
        assert fix_ascii_art(text) == text

    def test_right_edge_too_far(self):
        text = (
            "+--------+\n"
            "| hello   |\n"
            "+--------+"
        )
        expected = (
            "+--------+\n"
            "| hello  |\n"
            "+--------+"
        )
        assert fix_ascii_art(text) == expected

    def test_right_edge_too_close(self):
        text = (
            "+--------+\n"
            "| hello|\n"
            "+--------+"
        )
        expected = (
            "+--------+\n"
            "| hello  |\n"
            "+--------+"
        )
        assert fix_ascii_art(text) == expected

    def test_unicode_box_alignment(self):
        text = (
            "┌────────┐\n"
            "│ hello    │\n"
            "└────────┘"
        )
        expected = (
            "┌────────┐\n"
            "│ hello  │\n"
            "└────────┘"
        )
        assert fix_ascii_art(text) == expected

    def test_content_wider_extends_border(self):
        """When content is wider than the box, borders should be extended."""
        text = (
            "+------+\n"
            "| very long content |\n"
            "+------+"
        )
        result = fix_ascii_art(text)
        lines = result.split("\n")
        # The borders should be extended to fit the content
        assert len(lines[0]) == len(lines[2])  # top and bottom same width
        assert len(lines[0]) > 8  # wider than original +------+
        # Content text must be fully preserved (trailing whitespace may be trimmed)
        assert "very long content" in lines[1]
        assert lines[1].startswith("|") and lines[1].endswith("|")

    def test_cjk_content_alignment(self):
        """CJK (fullwidth) characters should be aligned correctly."""
        # CJK chars are 2 columns wide, so "hello" (5) and "日本語" (6) differ
        text = (
            "+----------+\n"
            "| 日本語    |\n"
            "+----------+"
        )
        result = fix_ascii_art(text)
        lines = result.split("\n")
        # The border is 12 chars wide, inner is 10
        # "日本語" is 6 display cols, needs 4 spaces to fill 10
        assert lines[0] == "+----------+"
        assert lines[2] == "+----------+"
        # The content line should have correct display width
        assert lines[1].startswith("| 日本語")
        assert lines[1].endswith("|")

    def test_tab_expansion(self):
        """Tabs should be expanded to spaces before fixing."""
        text = (
            "+--------+\n"
            "|\thello |\n"
            "+--------+"
        )
        result = fix_ascii_art(text)
        # Tabs should be expanded (4 spaces)
        assert "\t" not in result
        lines = result.split("\n")
        assert lines[0] == "+--------+"
        assert lines[2] == "+--------+"

    def test_multiple_content_lines(self):
        text = (
            "+----------+\n"
            "| line one  |\n"
            "| line two   |\n"
            "| ok       |\n"
            "+----------+"
        )
        expected = (
            "+----------+\n"
            "| line one |\n"
            "| line two |\n"
            "| ok       |\n"
            "+----------+"
        )
        assert fix_ascii_art(text) == expected


# ── Multi-box ──────────────────────────────────────────────────────

class TestMultiBox:
    def test_adjacent_boxes_no_gap(self):
        """Adjacent boxes sharing a corner (+---++---+) should be split into two segments."""
        text = (
            "+---++---+\n"
            "| a  || b |\n"
            "+---++---+"
        )
        expected = (
            "+---++---+\n"
            "| a || b |\n"
            "+---++---+"
        )
        assert fix_ascii_art(text) == expected

    def test_t_junction_not_split(self):
        """A T-junction (+---+---+) should stay as one segment, not be split."""
        # +---+---+ is 9 chars wide (single segment with T-junction in middle)
        # Content line should align to width 9
        text = (
            "+---+---+\n"
            "| hello |\n"
            "+---+---+"
        )
        expected = (
            "+---+---+\n"
            "| hello |\n"
            "+---+---+"
        )
        assert fix_ascii_art(text) == expected

    def test_stacked_boxes(self):
        text = (
            "+--------+\n"
            "| box 1   |\n"
            "+--------+\n"
            "+--------+\n"
            "| box 2  |\n"
            "+--------+"
        )
        expected = (
            "+--------+\n"
            "| box 1  |\n"
            "+--------+\n"
            "+--------+\n"
            "| box 2  |\n"
            "+--------+"
        )
        assert fix_ascii_art(text) == expected

    def test_lines_outside_boxes_preserved(self):
        text = (
            "+--------+\n"
            "| box 1  |\n"
            "+--------+\n"
            "    |\n"
            "    v\n"
            "+--------+\n"
            "| box 2  |\n"
            "+--------+"
        )
        assert fix_ascii_art(text) == text

    def test_side_by_side_boxes(self):
        text = (
            "+-------+     +-------+\n"
            "| Start  | --> | End   |\n"
            "+-------+     +-------+"
        )
        expected = (
            "+-------+     +-------+\n"
            "| Start | --> | End   |\n"
            "+-------+     +-------+"
        )
        assert fix_ascii_art(text) == expected

    def test_stacked_boxes_shared_borders(self):
        """Three boxes sharing border lines (Bug 1 scenario)."""
        text = (
            "+--------+\n"
            "| AAA     |\n"
            "+--------+\n"
            "| BBB    |\n"
            "+--------+\n"
            "| CCC      |\n"
            "+--------+"
        )
        expected = (
            "+--------+\n"
            "| AAA    |\n"
            "+--------+\n"
            "| BBB    |\n"
            "+--------+\n"
            "| CCC    |\n"
            "+--------+"
        )
        assert fix_ascii_art(text) == expected

    def test_side_by_side_both_misaligned(self):
        """Both left and right side-by-side boxes have misaligned content (Bug 2 scenario)."""
        text = (
            "+------------------+     +------------------+\n"
            "| Load Balancer    |       | CDN Cache          |\n"
            "+------------------+     +------------------+"
        )
        expected = (
            "+------------------+     +------------------+\n"
            "| Load Balancer    |     | CDN Cache        |\n"
            "+------------------+     +------------------+"
        )
        assert fix_ascii_art(text) == expected

    def test_side_by_side_second_row(self):
        """Two rows of side-by-side boxes separated by arrow lines."""
        text = (
            "+------------------+     +------------------+\n"
            "| Frontend App     |     | Mobile Client    |\n"
            "+------------------+     +------------------+\n"
            "        |                        |\n"
            "        v                        v\n"
            "+------------------+     +------------------+\n"
            "| Load Balancer    |       | CDN Cache          |\n"
            "+------------------+     +------------------+"
        )
        expected = (
            "+------------------+     +------------------+\n"
            "| Frontend App     |     | Mobile Client    |\n"
            "+------------------+     +------------------+\n"
            "        |                        |\n"
            "        v                        v\n"
            "+------------------+     +------------------+\n"
            "| Load Balancer    |     | CDN Cache        |\n"
            "+------------------+     +------------------+"
        )
        assert fix_ascii_art(text) == expected

    def test_stacked_boxes_shared_borders_unicode(self):
        """Shared-border stacked boxes using Unicode box-drawing chars."""
        text = (
            "┌────────┐\n"
            "│ AAA     │\n"
            "├────────┤\n"
            "│ BBB    │\n"
            "├────────┤\n"
            "│ CCC      │\n"
            "└────────┘"
        )
        expected = (
            "┌────────┐\n"
            "│ AAA    │\n"
            "├────────┤\n"
            "│ BBB    │\n"
            "├────────┤\n"
            "│ CCC    │\n"
            "└────────┘"
        )
        assert fix_ascii_art(text) == expected

    def test_side_by_side_both_misaligned_unicode(self):
        """Side-by-side Unicode boxes with both needing alignment."""
        text = (
            "┌──────────────────┐     ┌──────────────────┐\n"
            "│ Load Balancer    │       │ CDN Cache          │\n"
            "└──────────────────┘     └──────────────────┘"
        )
        expected = (
            "┌──────────────────┐     ┌──────────────────┐\n"
            "│ Load Balancer    │     │ CDN Cache        │\n"
            "└──────────────────┘     └──────────────────┘"
        )
        assert fix_ascii_art(text) == expected


# ── Nested boxes ───────────────────────────────────────────────────

class TestNestedBoxes:
    def test_nested_inner_misaligned(self):
        # Outer border: +------------------+ = 20 chars
        # Inner border: +--------+ at col 3 = 10 chars
        # Only inner content line is misaligned
        text = (
            "+------------------+\n"
            "|  +--------+      |\n"
            "|  | inner   |      |\n"
            "|  +--------+      |\n"
            "+------------------+"
        )
        # Inner | fixed (col 13→12), outer | stays at col 19 (width 20)
        expected = (
            "+------------------+\n"
            "|  +--------+      |\n"
            "|  | inner  |      |\n"
            "|  +--------+      |\n"
            "+------------------+"
        )
        assert fix_ascii_art(text) == expected

    def test_nested_outer_misaligned(self):
        # Outer border: +------------------+ = 20 chars
        # Outer content lines are 21 chars (1 too wide)
        text = (
            "+------------------+\n"
            "|  +--------+       |\n"
            "|  | inner  |       |\n"
            "|  +--------+       |\n"
            "+------------------+"
        )
        # Outer | pulled in to col 19 (width 20)
        expected = (
            "+------------------+\n"
            "|  +--------+      |\n"
            "|  | inner  |      |\n"
            "|  +--------+      |\n"
            "+------------------+"
        )
        assert fix_ascii_art(text) == expected

    def test_nested_both_misaligned(self):
        # Both inner and outer content are misaligned
        text = (
            "+------------------+\n"
            "|  +--------+       |\n"
            "|  | inner   |       |\n"
            "|  +--------+       |\n"
            "+------------------+"
        )
        expected = (
            "+------------------+\n"
            "|  +--------+      |\n"
            "|  | inner  |      |\n"
            "|  +--------+      |\n"
            "+------------------+"
        )
        assert fix_ascii_art(text) == expected

    def test_deeply_nested_three_levels(self):
        """Three levels of nesting with misalignment at each level."""
        text = (
            "+--------------------------------------+\n"
            "| Outer                                 |\n"
            "|                                      |\n"
            "|  +----------------------------+      |\n"
            "|  | Middle                      |      |\n"
            "|  |                            |      |\n"
            "|  |  +------------------+      |      |\n"
            "|  |  | Inner             |      |      |\n"
            "|  |  +------------------+      |      |\n"
            "|  +----------------------------+      |\n"
            "+--------------------------------------+"
        )
        expected = (
            "+--------------------------------------+\n"
            "| Outer                                |\n"
            "|                                      |\n"
            "|  +----------------------------+      |\n"
            "|  | Middle                     |      |\n"
            "|  |                            |      |\n"
            "|  |  +------------------+      |      |\n"
            "|  |  | Inner            |      |      |\n"
            "|  |  +------------------+      |      |\n"
            "|  +----------------------------+      |\n"
            "+--------------------------------------+"
        )
        assert fix_ascii_art(text) == expected

    def test_nested_both_misaligned_unicode(self):
        """Unicode nested boxes with both inner and outer misaligned."""
        text = (
            "┌──────────────────┐\n"
            "│  ┌────────┐       │\n"
            "│  │ inner   │       │\n"
            "│  └────────┘       │\n"
            "└──────────────────┘"
        )
        expected = (
            "┌──────────────────┐\n"
            "│  ┌────────┐      │\n"
            "│  │ inner  │      │\n"
            "│  └────────┘      │\n"
            "└──────────────────┘"
        )
        assert fix_ascii_art(text) == expected


# ── Normalization + alignment ──────────────────────────────────────

class TestNormalizeAndAlign:
    def test_normalize_then_fix(self):
        text = (
            "┌────────┐\n"
            "│ hello    │\n"
            "└────────┘"
        )
        result = fix_ascii_art(text, normalize=True)
        expected = (
            "+--------+\n"
            "| hello  |\n"
            "+--------+"
        )
        assert result == expected

    def test_normalize_full_diagram(self):
        text = (
            "┌──────┐\n"
            "│ Input │\n"
            "└──────┘\n"
            "   │\n"
            "   ▼\n"
            "┌──────┐\n"
            "│Output │\n"
            "└──────┘"
        )
        result = fix_ascii_art(text, normalize=True)
        expected = (
            "+------+\n"
            "| Input|\n"
            "+------+\n"
            "   |\n"
            "   v\n"
            "+------+\n"
            "|Output|\n"
            "+------+"
        )
        assert result == expected


# ── Edge cases ─────────────────────────────────────────────────────

class TestEdgeCases:
    def test_empty_input(self):
        assert fix_ascii_art("") == ""

    def test_no_boxes(self):
        text = "Hello, world!\nNo boxes here."
        assert fix_ascii_art(text) == text

    def test_orphan_border(self):
        text = "+--------+\nsome text\nmore text"
        assert fix_ascii_art(text) == text

    def test_single_border_line(self):
        text = "+--------+"
        assert fix_ascii_art(text) == text

    def test_lines_without_borders_inside_box(self):
        text = (
            "+--------+\n"
            "  hello   \n"
            "+--------+"
        )
        # Line without border chars is left unchanged
        assert fix_ascii_art(text) == text

    def test_wider_search_window(self):
        """Right border | found beyond old 8-char search limit."""
        # Content line with | shifted 10 chars to the right of expected position
        text = (
            "+--------+\n"
            "| hello            |\n"
            "+--------+"
        )
        result = fix_ascii_art(text)
        expected = (
            "+--------+\n"
            "| hello  |\n"
            "+--------+"
        )
        assert result == expected

    def test_preserves_trailing_newline(self):
        text = (
            "+--------+\n"
            "| hello   |\n"
            "+--------+\n"
        )
        expected = (
            "+--------+\n"
            "| hello  |\n"
            "+--------+\n"
        )
        assert fix_ascii_art(text) == expected


# ── Real-world diagrams ──────────────────────────────────────────

class TestRealWorld:
    def test_architecture_diagram(self):
        text = (
            "┌─────────────┐\n"
            "│   Frontend    │\n"
            "│  (React App)  │\n"
            "└─────────────┘\n"
            "       │\n"
            "       ▼\n"
            "┌─────────────┐\n"
            "│   Backend   │\n"
            "│ (Node.js)   │\n"
            "└─────────────┘"
        )
        expected = (
            "┌─────────────┐\n"
            "│   Frontend  │\n"
            "│  (React App)│\n"
            "└─────────────┘\n"
            "       │\n"
            "       ▼\n"
            "┌─────────────┐\n"
            "│   Backend   │\n"
            "│ (Node.js)   │\n"
            "└─────────────┘"
        )
        assert fix_ascii_art(text) == expected

    def test_flowchart_with_arrows(self):
        text = (
            "+-------+     +-------+\n"
            "| Start  | --> | End   |\n"
            "+-------+     +-------+"
        )
        expected = (
            "+-------+     +-------+\n"
            "| Start | --> | End   |\n"
            "+-------+     +-------+"
        )
        assert fix_ascii_art(text) == expected

    def test_full_sample_diagram(self):
        """Full sample_test.md scenario: stacked shared-border, side-by-side, nested."""
        text = (
            "+------------------------+\n"
            "| API Gateway            |\n"
            "+------------------------+\n"
            "| Authentication    |\n"
            "+------------------------+\n"
            "| Request Router         |\n"
            "+------------------------+\n"
            "\n"
            "+------------------+     +------------------+\n"
            "| Frontend App     |     | Mobile Client    |\n"
            "+------------------+     +------------------+\n"
            "        |                        |\n"
            "        v                        v\n"
            "+------------------+     +------------------+\n"
            "| Load Balancer    |       | CDN Cache          |\n"
            "+------------------+     +------------------+\n"
            "\n"
            "+--------------------------------------+\n"
            "| Kubernetes Cluster                   |\n"
            "|                                      |\n"
            "|  +----------------------------+      |\n"
            "|  | Service Mesh               |      |\n"
            "|  |                            |      |\n"
            "|  |  +------------------+      |      |\n"
            "|  |  | Microservice A   |      |      |\n"
            "|  |  +------------------+      |      |\n"
            "|  |  +------------------+      |      |\n"
            "|  |  | Microservice B   |      |      |\n"
            "|  |  +------------------+      |      |\n"
            "|  +----------------------------+      |\n"
            "+--------------------------------------+"
        )
        expected = (
            "+------------------------+\n"
            "| API Gateway            |\n"
            "+------------------------+\n"
            "| Authentication         |\n"
            "+------------------------+\n"
            "| Request Router         |\n"
            "+------------------------+\n"
            "\n"
            "+------------------+     +------------------+\n"
            "| Frontend App     |     | Mobile Client    |\n"
            "+------------------+     +------------------+\n"
            "        |                        |\n"
            "        v                        v\n"
            "+------------------+     +------------------+\n"
            "| Load Balancer    |     | CDN Cache        |\n"
            "+------------------+     +------------------+\n"
            "\n"
            "+--------------------------------------+\n"
            "| Kubernetes Cluster                   |\n"
            "|                                      |\n"
            "|  +----------------------------+      |\n"
            "|  | Service Mesh               |      |\n"
            "|  |                            |      |\n"
            "|  |  +------------------+      |      |\n"
            "|  |  | Microservice A   |      |      |\n"
            "|  |  +------------------+      |      |\n"
            "|  |  +------------------+      |      |\n"
            "|  |  | Microservice B   |      |      |\n"
            "|  |  +------------------+      |      |\n"
            "|  +----------------------------+      |\n"
            "+--------------------------------------+"
        )
        assert fix_ascii_art(text) == expected

    def test_typical_llm_output(self):
        """A typical misaligned diagram an LLM might produce."""
        # Border +-------------------+ = 21 chars (+ 19 dashes +)
        # "User Request" too wide, "Parse & Validate" too narrow, "Process" correct
        text = (
            "+-------------------+\n"
            "| User Request       |\n"
            "+-------------------+\n"
            "         |\n"
            "         v\n"
            "+-------------------+\n"
            "| Parse & Validate |\n"
            "+-------------------+\n"
            "         |\n"
            "         v\n"
            "+-------------------+\n"
            "| Process           |\n"
            "+-------------------+"
        )
        expected = (
            "+-------------------+\n"
            "| User Request      |\n"
            "+-------------------+\n"
            "         |\n"
            "         v\n"
            "+-------------------+\n"
            "| Parse & Validate  |\n"
            "+-------------------+\n"
            "         |\n"
            "         v\n"
            "+-------------------+\n"
            "| Process           |\n"
            "+-------------------+"
        )
        assert fix_ascii_art(text) == expected


# ── Markdown mode ─────────────────────────────────────────────────

class TestMarkdownMode:
    def test_code_fence_diagram_fixed(self):
        text = (
            "# Architecture\n"
            "\n"
            "Here is the diagram:\n"
            "\n"
            "```\n"
            "+--------+\n"
            "| hello   |\n"
            "+--------+\n"
            "```\n"
            "\n"
            "Some text after.\n"
        )
        expected = (
            "# Architecture\n"
            "\n"
            "Here is the diagram:\n"
            "\n"
            "```\n"
            "+--------+\n"
            "| hello  |\n"
            "+--------+\n"
            "```\n"
            "\n"
            "Some text after.\n"
        )
        assert fix_ascii_art(text, markdown=True) == expected

    def test_markdown_table_not_touched(self):
        """Markdown tables use | but should not be altered in markdown mode."""
        text = (
            "# Data\n"
            "\n"
            "| Name  | Age |\n"
            "|-------|-----|\n"
            "| Alice | 30  |\n"
        )
        assert fix_ascii_art(text, markdown=True) == text

    def test_unfenced_diagram_auto_detected(self):
        text = (
            "# Design\n"
            "\n"
            "+--------+\n"
            "| hello   |\n"
            "+--------+\n"
            "\n"
            "End of doc.\n"
        )
        expected = (
            "# Design\n"
            "\n"
            "+--------+\n"
            "| hello  |\n"
            "+--------+\n"
            "\n"
            "End of doc.\n"
        )
        assert fix_ascii_art(text, markdown=True) == expected

    def test_multiple_fenced_diagrams(self):
        text = (
            "```\n"
            "+------+\n"
            "| one   |\n"
            "+------+\n"
            "```\n"
            "\n"
            "Text between.\n"
            "\n"
            "```\n"
            "+------+\n"
            "| two   |\n"
            "+------+\n"
            "```\n"
        )
        expected = (
            "```\n"
            "+------+\n"
            "| one  |\n"
            "+------+\n"
            "```\n"
            "\n"
            "Text between.\n"
            "\n"
            "```\n"
            "+------+\n"
            "| two  |\n"
            "+------+\n"
            "```\n"
        )
        assert fix_ascii_art(text, markdown=True) == expected

    def test_markdown_stacked_shared_borders(self):
        """Shared-border stacked boxes inside a code fence."""
        text = (
            "# Stacked\n"
            "\n"
            "```\n"
            "+------------------------+\n"
            "| API Gateway            |\n"
            "+------------------------+\n"
            "| Authentication    |\n"
            "+------------------------+\n"
            "| Request Router         |\n"
            "+------------------------+\n"
            "```\n"
        )
        expected = (
            "# Stacked\n"
            "\n"
            "```\n"
            "+------------------------+\n"
            "| API Gateway            |\n"
            "+------------------------+\n"
            "| Authentication         |\n"
            "+------------------------+\n"
            "| Request Router         |\n"
            "+------------------------+\n"
            "```\n"
        )
        assert fix_ascii_art(text, markdown=True) == expected

    def test_markdown_side_by_side_both_fixed(self):
        """Side-by-side boxes inside a code fence with both needing alignment."""
        text = (
            "```\n"
            "+------------------+     +------------------+\n"
            "| Load Balancer    |       | CDN Cache          |\n"
            "+------------------+     +------------------+\n"
            "```\n"
        )
        expected = (
            "```\n"
            "+------------------+     +------------------+\n"
            "| Load Balancer    |     | CDN Cache        |\n"
            "+------------------+     +------------------+\n"
            "```\n"
        )
        assert fix_ascii_art(text, markdown=True) == expected

    def test_tilde_fence(self):
        """Tilde fences (~~~) should be detected like backtick fences."""
        text = (
            "# Title\n"
            "\n"
            "~~~\n"
            "+--------+\n"
            "| hello   |\n"
            "+--------+\n"
            "~~~\n"
            "\n"
            "End.\n"
        )
        expected = (
            "# Title\n"
            "\n"
            "~~~\n"
            "+--------+\n"
            "| hello  |\n"
            "+--------+\n"
            "~~~\n"
            "\n"
            "End.\n"
        )
        assert fix_ascii_art(text, markdown=True) == expected

    def test_unclosed_fence(self):
        """Unclosed fence should treat remaining lines as fenced content."""
        text = (
            "# Title\n"
            "\n"
            "```\n"
            "+--------+\n"
            "| hello   |\n"
            "+--------+"
        )
        expected = (
            "# Title\n"
            "\n"
            "```\n"
            "+--------+\n"
            "| hello  |\n"
            "+--------+"
        )
        assert fix_ascii_art(text, markdown=True) == expected

    def test_no_diagrams_in_markdown(self):
        text = "# Just a heading\n\nSome paragraph text.\n"
        assert fix_ascii_art(text, markdown=True) == text
