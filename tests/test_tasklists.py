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
from editor import EditorPane
from PySide6.QtWidgets import QApplication

_app = QApplication.instance() or QApplication([])


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

    def test_render_toc_standard_and_no_bullet(self):
        md_std = "[[TOC]]\n\n# Heading 1\n## Heading 2\n"
        html_std = self.renderer.render(md_std)
        self.assertIn('<div class="toc">', html_std)
        self.assertNotIn('<div class="toc no-bullet">', html_std)

        for syntax in [
            "[[TOC]](no-bullet)",
            "[[TOC no-bullet]]",
            "[[TOC(no-bullet)]]",
            '[[TOC="Custom" no-bullet]]',
            '[[TOC="Custom"]](no-bullet)',
        ]:
            md_nb = f"{syntax}\n\n# Heading 1\n## Heading 2\n"
            html_nb = self.renderer.render(md_nb)
            self.assertIn('<div class="toc no-bullet">', html_nb, f"Failed for {syntax}")

    def test_render_toc_alignment_and_custom_title(self):
        cases = [
            ("[[TOC center]]", "Table of Contents", "toc-align-center", False),
            ("[[TOC right]]", "Table of Contents", "toc-align-right", False),
            ("[[TOC left]]", "Table of Contents", "toc-align-left", False),
            ('[[TOC="MỤC LỤC CHÍNH" center]]', "MỤC LỤC CHÍNH", "toc-align-center", False),
            ('[[TOC="MỤC LỤC" align=right]]', "MỤC LỤC", "toc-align-right", False),
            ('[[TOC="BÁO CÁO" center no-bullet]]', "BÁO CÁO", "toc-align-center", True),
            ('[[TOC="BÁO CÁO"]](right, no-bullet)', "BÁO CÁO", "toc-align-right", True),
            ('[[TOC(center, no-bullet)]]', "Table of Contents", "toc-align-center", True),
        ]
        for md_str, expected_label, expected_align_class, is_no_bullet in cases:
            html = self.renderer.render(f"{md_str}\n\n# Heading 1\n## Heading 2\n")
            self.assertIn(expected_label, html)
            self.assertIn(expected_align_class, html)
            if is_no_bullet:
                self.assertIn('<div class="toc no-bullet">', html)
            else:
                self.assertNotIn('<div class="toc no-bullet">', html)

    def test_render_toc_html_and_markdown_headings(self):
        md = (
            "[[TOC center no-bullet]]\n\n"
            '<div class="report">\n'
            "  <h1>Document Overview</h1>\n"
            "  <h2>1. Executive Summary</h2>\n"
            "  <p>Text here</p>\n"
            "</div>\n\n"
            "### 1.1 First Sub-task\n\n"
            "### 1.2 Second Sub-task\n\n"
            "<h2>2. Detailed Methodology</h2>\n\n"
            "### 2.1 Tooling Setup\n"
        )
        html = self.renderer.render(md)
        self.assertIn('<div class="toc no-bullet">', html)
        self.assertIn("Document Overview", html)
        self.assertIn("1. Executive Summary", html)
        self.assertIn("1.1 First Sub-task", html)
        self.assertIn("1.2 Second Sub-task", html)
        self.assertIn("2. Detailed Methodology", html)
        self.assertIn("2.1 Tooling Setup", html)
        # Check injected anchor IDs
        self.assertIn('id="document-overview"', html)
        self.assertIn('id="1-executive-summary"', html)
        self.assertIn('id="2-detailed-methodology"', html)

    def test_render_toc_only_headings_below_toc_and_depth_classes(self):
        md = (
            "# Top Document Title Before TOC\n\n"
            "Author: pentester\n\n"
            "[[TOC='MỤC LỤC' center no-bullet]]\n\n"
            "## 1. Executive Summary\n\n"
            "### 1.1 Target Assets\n\n"
            "#### 1.1.1 Production API\n\n"
            "## 2. Technical Findings\n"
        )
        html = self.renderer.render(md)
        self.assertIn('<div class="toc no-bullet">', html)
        self.assertIn('toc-align-center', html)
        # Top title before TOC gets an anchor ID, but MUST NOT be in TOC list
        self.assertIn('id="top-document-title-before-toc"', html)
        self.assertNotIn('href="#top-document-title-before-toc"', html)
        # Headings below TOC must be present with proper depth classes
        self.assertIn('class="toc-item toc-depth-1"><a href="#1-executive-summary">1. Executive Summary</a>', html)
        self.assertIn('class="toc-item toc-depth-2"><a href="#11-target-assets">1.1 Target Assets</a>', html)
        self.assertIn('class="toc-item toc-depth-3"><a href="#111-production-api">1.1.1 Production API</a>', html)
        self.assertIn('class="toc-item toc-depth-1"><a href="#2-technical-findings">2. Technical Findings</a>', html)

    def test_render_toc_colors_and_customization(self):
        # 1. Default title is bold black (#1f2328) with font-weight 900
        md_default = "[[TOC]]\n\n# Chapter 1\n## Section 1.1\n"
        html_default = self.renderer.render(md_default)
        self.assertIn('color: #1f2328 !important; font-weight: 900 !important;', html_default)
        self.assertIn('<a href="#chapter-1">Chapter 1</a>', html_default)
        self.assertIn('<a href="#section-11">Section 1.1</a>', html_default)

        # 2. Custom title color
        md_custom_title = '[[TOC title-color="#0284c7"]]\n\n# Chapter 1\n'
        html_custom_title = self.renderer.render(md_custom_title)
        self.assertIn('color: #0284c7 !important; font-weight: 900 !important;', html_custom_title)

        # 3. Custom level colors (e.g. c1=black, c2=blue)
        md_level_colors = '[[TOC="MỤC LỤC" title-color="#1e40af" c1="#000000" c2="#0969da"]]\n\n# Chapter 1\n## Section 1.1\n### Sub 1.1.1\n'
        html_level = self.renderer.render(md_level_colors)
        self.assertIn('color: #1e40af !important; font-weight: 900 !important;', html_level)
        html_level_colors = self.renderer.render(md_level_colors)
        self.assertIn('color: #1e40af !important; font-weight: 900 !important;', html_level_colors)
        self.assertIn('<li class="toc-item toc-depth-1"><a href="#chapter-1" style="color: #000000 !important;">Chapter 1</a>', html_level_colors)
        self.assertIn('<li class="toc-item toc-depth-2"><a href="#section-11" style="color: #0969da !important;">Section 1.1</a>', html_level_colors)
        # c3 not defined, so it has no inline style and falls back to theme black
        self.assertIn('<li class="toc-item toc-depth-3"><a href="#sub-111">Sub 1.1.1</a>', html_level_colors)

        # 4. Max depth limitation
        md_max_depth = '[[TOC max-depth=2]]\n\n# Chapter 1\n## Section 1.1\n### Sub 1.1.1\n'
        html_max_depth = self.renderer.render(md_max_depth)
        self.assertIn('href="#chapter-1"', html_max_depth)
        self.assertIn('href="#section-11"', html_max_depth)
        self.assertNotIn('href="#sub-111"', html_max_depth)

    def test_donut_chart_code_fence_and_directive(self):
        md_fence = (
            "```donut\n"
            "5 Issues\n"
            "Critical: 0\n"
            "High: 1\n"
            "Medium: 2\n"
            "Low: 2\n"
            "```\n"
        )
        html_fence = self.renderer.render(md_fence)
        self.assertIn('class="donut-widget"', html_fence)
        self.assertIn('class="donut-chart"', html_fence)
        self.assertIn('class="donut-svg-ring"', html_fence)
        self.assertIn('<b>5</b>', html_fence)
        self.assertIn('<span>Issues</span>', html_fence)
        self.assertIn('Critical: <b>0</b>', html_fence)
        self.assertIn('High: <b>1</b>', html_fence)
        self.assertIn('Medium: <b>2</b>', html_fence)
        self.assertIn('Low: <b>2</b>', html_fence)

        md_directive = "[[donut 5 Issues | Critical: 0 | High: 1 | Medium: 2 | Low: 2]]"
        html_dir = self.renderer.render(md_directive)
        self.assertIn('class="donut-widget"', html_dir)
        self.assertIn('class="donut-svg-ring"', html_dir)
        self.assertIn('<b>5</b>', html_dir)


class TestEditorLineNumbers(unittest.TestCase):
    def test_line_number_area_initialization_and_width(self):
        editor = EditorPane()
        self.assertIsNotNone(editor.lineNumberArea)
        w1 = editor.lineNumberAreaWidth()
        self.assertGreater(w1, 10)

        # Set 150 lines
        editor.setPlainText("\n".join(f"Line {i}" for i in range(150)))
        w2 = editor.lineNumberAreaWidth()
        self.assertGreater(w2, w1)


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
            self.assertIn("overflow-wrap: anywhere", content)
            self.assertIn("white-space: pre-wrap", content)
            self.assertIn("box-decoration-break: clone", content)
            self.assertIn("toc.no-bullet", content)
            self.assertIn("toc-title", content)
            self.assertIn("metrics-dashboard-bar", content)
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
