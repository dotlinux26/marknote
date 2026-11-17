"""Unit tests cho tinh nang Task List (GFM checklist) va PDF export."""

import sys
import tempfile
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from exporter import Exporter, build_document, replace_checkboxes_with_svg
from preview import MarkdownRenderer, normalize_tasklists


class TestTasklistNormalization(unittest.TestCase):
    def test_normalize_bare_brackets(self):
        md = "[ ] Unchecked task\n[x] Checked task\n[X] Uppercase task"
        norm = normalize_tasklists(md)
        expected = "- [ ] Unchecked task\n- [x] Checked task\n- [x] Uppercase task"
        self.assertEqual(norm, expected)

    def test_normalize_dash_without_space(self):
        md = "-[ ] Task without space\n-[x] Checked without space"
        norm = normalize_tasklists(md)
        expected = "- [ ] Task without space\n- [x] Checked without space"
        self.assertEqual(norm, expected)

    def test_normalize_standard_bullets(self):
        md = "* [ ] Star bullet\n+ [x] Plus bullet\n- [ ] Standard dash"
        norm = normalize_tasklists(md)
        expected = "- [ ] Star bullet\n- [x] Plus bullet\n- [ ] Standard dash"
        self.assertEqual(norm, expected)

    def test_normalize_indented_nested(self):
        md = "- [ ] Parent\n  [ ] Sub 1\n    [x] Sub 2"
        norm = normalize_tasklists(md)
        expected = "- [ ] Parent\n  - [ ] Sub 1\n    - [x] Sub 2"
        self.assertEqual(norm, expected)

    def test_ignore_footnotes_and_links(self):
        md = "[1] Footnote\n[link](https://example.com)\nText with [ ] in the middle"
        norm = normalize_tasklists(md)
        self.assertEqual(norm, md)

    def test_preserve_fenced_code_blocks(self):
        md = (
            "- [ ] Task outside\n"
            "```python\n"
            "[ ] Code comment\n"
            "[x] Another code line\n"
            "```\n"
            "[ ] Task after code"
        )
        norm = normalize_tasklists(md)
        self.assertIn("- [ ] Task outside", norm)
        self.assertIn("```python\n[ ] Code comment\n[x] Another code line\n```", norm)
        self.assertIn("- [ ] Task after code", norm)


class TestSvgCheckboxReplacement(unittest.TestCase):
    def test_replace_unchecked(self):
        html = '<li class="task-list-item"><input class="task-list-item-checkbox" disabled="disabled" type="checkbox"> Task 1</li>'
        out = replace_checkboxes_with_svg(html)
        self.assertNotIn("<input", out)
        self.assertIn('class="task-svg task-unchecked"', out)
        self.assertIn("Task 1</li>", out)

    def test_replace_checked(self):
        html = '<li class="task-list-item"><input class="task-list-item-checkbox" checked="checked" disabled="disabled" type="checkbox"> Done</li>'
        out = replace_checkboxes_with_svg(html)
        self.assertNotIn("<input", out)
        self.assertIn('class="task-svg task-checked"', out)
        self.assertIn("Done</li>", out)

    def test_ignore_other_inputs(self):
        html = '<input type="text" class="search-input" value="[ ] hello">'
        out = replace_checkboxes_with_svg(html)
        self.assertEqual(out, html)


class TestMarkdownRenderer(unittest.TestCase):
    def setUp(self):
        self.renderer = MarkdownRenderer()

    def test_render_checklist(self):
        md = (
            "## Checklist\n\n"
            "- [ ] Item 1\n"
            "[ ] Item 2\n"
            "[x] Item 3\n"
        )
        html = self.renderer.render(md)
        self.assertIn('<ul class="contains-task-list">', html)
        self.assertIn('class="task-svg task-unchecked"', html)
        self.assertIn('class="task-svg task-checked"', html)
        self.assertNotIn("<input", html)
        self.assertIn("Item 1", html)
        self.assertIn("Item 2", html)
        self.assertIn("Item 3", html)


class TestExporter(unittest.TestCase):
    def setUp(self):
        self.exporter = Exporter()
        self.renderer = MarkdownRenderer()

    def test_export_html_contains_svg_and_styles(self):
        md = "- [ ] To Do\n- [x] Done\n\n```python\nlong_code_line = 1\n```\n\n| Col 1 | Col 2 |\n|---|---|\n| A | B |\n"
        html_body = self.renderer.render(md)
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            tmp_path = Path(f.name)
        try:
            self.exporter.toHtml(html_body, "", tmp_path)
            content = tmp_path.read_text(encoding="utf-8")
            self.assertIn("task-svg", content)
            self.assertIn("contains-task-list", content)
            self.assertIn("table-layout: auto", content)
            self.assertIn("white-space: pre-wrap", content)
            self.assertIn("box-decoration-break: clone", content)
            self.assertIn("To Do", content)
            self.assertIn("Done", content)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_export_pdf_creates_file(self):
        md = "- [ ] Task in PDF\n- [x] Completed in PDF"
        html_body = self.renderer.render(md)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            tmp_path = Path(f.name)
        try:
            self.exporter.toPdf(html_body, "", tmp_path)
            self.assertTrue(tmp_path.exists())
            self.assertGreater(tmp_path.stat().st_size, 1000)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


if __name__ == "__main__":
    unittest.main()
