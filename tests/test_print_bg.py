"""Unit tests cho R1: Background paper image va per-page styling cho print va PDF export."""

import sys
import tempfile
import unittest
import io
import base64
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from PIL import Image

from exporter import (
    Exporter,
    PrintDirectiveConfig,
    adjust_image_alpha,
    build_document,
    build_pdf_page_rule,
    generate_page_css,
    parse_page_targets,
    parse_print_directive,
    parse_print_directives,
)
from preview import MarkdownRenderer


class TestPrintDirectiveParsing(unittest.TestCase):
    def test_parse_basic_print_directive(self):
        text = '[[print bg="paper.png" mode=stretch opacity=0.8]]'
        cfg = parse_print_directive(text)
        self.assertEqual(cfg.bg, "paper.png")
        self.assertEqual(cfg.mode, "stretch")
        self.assertAlmostEqual(cfg.opacity, 0.8)
        self.assertEqual(cfg.pages, "all")

    def test_parse_page_bg_directive(self):
        text = '[[page-bg image="media/bg.jpg" fit=cover position="top left" bg-color="#fdf6e3" text-color="#333333" pages="1-2" style="margin: 20mm;"]]'
        cfg = parse_print_directive(text)
        self.assertEqual(cfg.directive_type, "page-bg")
        self.assertEqual(cfg.bg, "media/bg.jpg")
        self.assertEqual(cfg.mode, "cover")
        self.assertEqual(cfg.position, "top left")
        self.assertEqual(cfg.bg_color, "#fdf6e3")
        self.assertEqual(cfg.text_color, "#333333")
        self.assertEqual(cfg.pages, "1-2")
        self.assertIn("margin: 20mm;", cfg.style)

    def test_parse_gradients(self):
        # linear gradient in bg-color
        text1 = '[[print bg-color="linear-gradient(to bottom, #ffffff, #eeeeee)" pages="1,3,5"]]'
        cfg1 = parse_print_directive(text1)
        self.assertEqual(cfg1.gradient, "linear-gradient(to bottom, #ffffff, #eeeeee)")
        self.assertEqual(cfg1.pages, "1,3,5")

        # radial gradient in gradient attribute
        text2 = '[[page-bg gradient="radial-gradient(circle, #f0f0f0, #e0e0e0)" page=1]]'
        cfg2 = parse_print_directive(text2)
        self.assertEqual(cfg2.gradient, "radial-gradient(circle, #f0f0f0, #e0e0e0)")
        self.assertEqual(cfg2.pages, "1")

    def test_parse_alpha_percentage_and_modes(self):
        for mode in ["repeat", "stretch", "cover", "contain"]:
            text = f'[[print mode="{mode}" alpha="75%"]]'
            cfg = parse_print_directive(text)
            self.assertEqual(cfg.mode, mode)
            self.assertAlmostEqual(cfg.opacity, 0.75)

    def test_parse_page_targets(self):
        self.assertEqual(parse_page_targets("all"), ["all"])
        self.assertEqual(parse_page_targets(""), ["all"])
        self.assertEqual(parse_page_targets("1"), [1])
        self.assertEqual(parse_page_targets("first"), [1])
        self.assertEqual(parse_page_targets("1-2"), [1, 2])
        self.assertEqual(parse_page_targets("1,3,5"), [1, 3, 5])
        self.assertEqual(parse_page_targets("odd"), ["odd"])
        self.assertEqual(parse_page_targets("even"), ["even"])

    def test_bare_keywords_and_aliases(self):
        # Bare keywords
        cfg_bare = parse_print_directive("[[print stretch center odd]]")
        self.assertEqual(cfg_bare.mode, "stretch")
        self.assertEqual(cfg_bare.position, "center")
        self.assertEqual(cfg_bare.pages, "odd")

        # Aliases
        cfg_alias = parse_print_directive('[[page-bg src="test.jpg" fit=repeat pos="bottom right" textcolor="red" bgcolor="blue"]]')
        self.assertEqual(cfg_alias.bg, "test.jpg")
        self.assertEqual(cfg_alias.mode, "repeat")
        self.assertEqual(cfg_alias.position, "bottom right")
        self.assertEqual(cfg_alias.text_color, "red")
        self.assertEqual(cfg_alias.bg_color, "blue")

    def test_parse_multiple_directives(self):
        text = (
            '[[page-bg page=1 bg="cover.png" mode=stretch]]\n\n'
            '[[page-bg pages="2-4" bg-color="#f0f0f0" text-color="#111"]]\n\n'
            '[[print pages="5" gradient="linear-gradient(#fff, #000)"]]\n'
        )
        cfgs = parse_print_directives(text)
        self.assertEqual(len(cfgs), 3)
        self.assertEqual(cfgs[0].pages, "1")
        self.assertEqual(cfgs[0].bg, "cover.png")
        self.assertEqual(cfgs[1].pages, "2-4")
        self.assertEqual(cfgs[1].bg_color, "#f0f0f0")
        self.assertEqual(cfgs[2].pages, "5")
        self.assertEqual(cfgs[2].gradient, "linear-gradient(#fff, #000)")


class TestPillowAlphaAdjustment(unittest.TestCase):
    def test_adjust_image_alpha_creates_transparent_png(self):
        # Create a solid red image in memory
        im = Image.new("RGB", (20, 20), (255, 0, 0))
        buf = io.BytesIO()
        im.save(buf, format="PNG")
        raw_bytes = buf.getvalue()

        # Adjust alpha to 50%
        uri = adjust_image_alpha(raw_bytes, alpha=0.5)
        self.assertTrue(uri.startswith("data:image/png;base64,"))

        # Decode and verify alpha channel
        b64_data = uri.split(",", 1)[1]
        decoded = base64.b64decode(b64_data)
        out_im = Image.open(io.BytesIO(decoded))
        self.assertEqual(out_im.mode, "RGBA")
        pixel = out_im.getpixel((10, 10))
        self.assertEqual(pixel[0], 255)
        self.assertEqual(pixel[1], 0)
        self.assertEqual(pixel[2], 0)
        self.assertEqual(pixel[3], 128)  # 50% of 255 rounded

    def test_adjust_image_alpha_from_file(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            tmp_path = Path(f.name)
            im = Image.new("RGBA", (15, 15), (0, 128, 255, 200))
            im.save(tmp_path, format="PNG")

        try:
            uri = adjust_image_alpha(tmp_path, alpha=0.5)
            self.assertTrue(uri.startswith("data:image/png;base64,"))
            b64_data = uri.split(",", 1)[1]
            out_im = Image.open(io.BytesIO(base64.b64decode(b64_data)))
            pixel = out_im.getpixel((5, 5))
            self.assertEqual(pixel[3], 100)  # 200 * 0.5 = 100
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


class TestPageCssGeneration(unittest.TestCase):
    def test_generate_page_css_all_pages(self):
        cfg = PrintDirectiveConfig(
            bg_color="#fdf6e3",
            text_color="#1a202c",
            style="margin: 25mm 20mm;",
            pages="all",
        )
        css = generate_page_css(cfg)
        self.assertIn("@page {", css)
        self.assertIn("background-color: #fdf6e3;", css)
        self.assertIn("color: #1a202c;", css)
        self.assertIn("margin: 25mm 20mm;", css)

    def test_generate_page_css_specific_pages(self):
        cfg = PrintDirectiveConfig(
            gradient="linear-gradient(to bottom, #ffffff, #eeeeee)",
            mode="cover",
            pages="1-2",
        )
        css = generate_page_css(cfg)
        self.assertIn("@page :first", css)
        self.assertIn("@page :nth(1)", css)
        self.assertIn("@page :nth(2)", css)
        self.assertIn("background-image: linear-gradient(to bottom, #ffffff, #eeeeee);", css)
        self.assertIn("background-size: cover;", css)
        self.assertIn("background-repeat: no-repeat;", css)

    def test_generate_page_css_modes(self):
        # repeat mode
        cfg_rep = PrintDirectiveConfig(bg="sample.png", mode="repeat")
        css_rep = generate_page_css(cfg_rep)
        self.assertIn("background-repeat: repeat;", css_rep)

        # stretch mode
        cfg_str = PrintDirectiveConfig(bg="sample.png", mode="stretch")
        css_str = generate_page_css(cfg_str)
        self.assertIn("background-size: 100% 100%;", css_str)
        self.assertIn("background-repeat: no-repeat;", css_str)

        # contain mode
        cfg_cnt = PrintDirectiveConfig(bg="sample.png", mode="contain")
        css_cnt = generate_page_css(cfg_cnt)
        self.assertIn("background-size: contain;", css_cnt)
        self.assertIn("background-repeat: no-repeat;", css_str)


class TestMarkdownRendererHidesTokens(unittest.TestCase):
    def setUp(self):
        self.renderer = MarkdownRenderer()

    def test_hide_print_token_from_preview(self):
        md = (
            "# My Document\n\n"
            '[[print bg="paper.png" mode=stretch opacity=0.8]]\n\n'
            "This is visible text."
        )
        html = self.renderer.render(md)
        self.assertNotIn("[[print", html)
        self.assertIn("My Document", html)
        self.assertIn("This is visible text.", html)

    def test_hide_page_bg_token_from_preview(self):
        md = (
            "# Page 1\n\n"
            '[[page-bg page=1 bg-color="#fdf6e3" text-color="#333"]]\n\n'
            "Page 1 content."
        )
        html = self.renderer.render(md)
        self.assertNotIn("[[page-bg", html)
        self.assertIn("Page 1", html)
        self.assertIn("Page 1 content.", html)


class TestExporterPdfIntegration(unittest.TestCase):
    def setUp(self):
        self.exporter = Exporter()
        self.renderer = MarkdownRenderer()

    def test_export_pdf_with_print_directive(self):
        # Create a small temp background image
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as img_f:
            im = Image.new("RGBA", (50, 50), (240, 230, 200, 255))
            im.save(img_f, format="PNG")
            img_path = Path(img_f.name)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as pdf_f:
            pdf_path = Path(pdf_f.name)

        try:
            md = (
                f'[[print bg="{img_path.as_posix()}" mode=stretch opacity=0.7 bg-color="#fafafa" text-color="#222222"]]\n\n'
                "# Document with Paper Background\n\n"
                "Testing PDF export with paper background image and per-page styling."
            )
            html_body = self.renderer.render(md)
            self.exporter.toPdf(html_body, "", pdf_path)
            self.assertTrue(pdf_path.exists())
            self.assertGreater(pdf_path.stat().st_size, 1000)
        finally:
            if img_path.exists():
                img_path.unlink()
            if pdf_path.exists():
                pdf_path.unlink()

    def test_export_html_with_print_directive(self):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            html_path = Path(f.name)

        try:
            md = (
                '[[page-bg bg-color="#fdf6e3" text-color="#1a202c" style="margin: 20mm;"]]\n\n'
                "# HTML Export Note\n\n"
                "Testing HTML export."
            )
            html_body = self.renderer.render(md)
            self.exporter.toHtml(html_body, "", html_path)
            content = html_path.read_text(encoding="utf-8")
            self.assertIn("background-color: #fdf6e3;", content)
            self.assertIn("color: #1a202c;", content)
            self.assertIn("margin: 20mm;", content)
            self.assertNotIn("[[page-bg", content)
            self.assertIn("HTML Export Note", content)
        finally:
            if html_path.exists():
                html_path.unlink()

    def test_build_document_with_raw_directive(self):
        raw_html = '<p>[[print bg-color="#123456" text-color="#654321"]]</p><p>Some content</p>'
        doc = build_document(raw_html, "")
        self.assertIn("background-color: #123456;", doc)
        self.assertIn("color: #654321;", doc)
        self.assertNotIn("[[print", doc)
        self.assertIn("Some content", doc)


if __name__ == "__main__":
    unittest.main()
