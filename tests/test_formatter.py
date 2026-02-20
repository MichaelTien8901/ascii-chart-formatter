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

    def test_no_diagrams_in_markdown(self):
        text = "# Just a heading\n\nSome paragraph text.\n"
        assert fix_ascii_art(text, markdown=True) == text
