import unittest
from pathlib import Path

from exporter import build_pdf_page_rule, parse_print_directives, enhance_html_components
from media import process_markdown_images, embed_images_as_base64, resolve_media_file, ensure_media_dir, MEDIA_DIR


class TestImageAndCoverEnhancements(unittest.TestCase):
    def test_pdf_cover_transparency_and_no_page_num(self):
        body = '[[page-bg gradient="linear-gradient(135deg, #0d1b2a 0%, #1b3a57 55%, #007788 100%)" pages="1"]]'
        dirs = parse_print_directives(body)
        rule = build_pdf_page_rule("", html_body=body, directives=dirs)
        self.assertIn("background: transparent !important;", rule)
        self.assertIn("@bottom-center { content: none !important; }", rule)

    def test_markdown_image_width_and_align_center(self):
        md = "![signature](signature.png){width=100px align=center}"
        html = process_markdown_images(md)
        self.assertIn('class="img-align-center"', html)
        self.assertIn("width: 100px", html)
        self.assertIn('src="signature.png"', html)

    def test_markdown_image_obsidian_syntax(self):
        md = "![logo|150|center](logo.png)"
        html = process_markdown_images(md)
        self.assertIn('class="img-align-center"', html)
        self.assertIn("width: 150px", html)

    def test_markdown_image_suffix_syntax(self):
        md = "![banner](banner.png =300x120)"
        html = process_markdown_images(md)
        self.assertIn("width: 300px", html)
        self.assertIn("height: 120px", html)

    def test_media_as_root_resolution(self):
        ensure_media_dir()
        test_file = MEDIA_DIR / "test_root_sample.png"
        test_file.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82")
        try:
            # 1. Resolve bang filename truc tiep
            found = resolve_media_file("test_root_sample.png")
            self.assertIsNotNone(found)
            self.assertEqual(found.resolve(), test_file.resolve())

            # 2. Resolve bang media/ prefix
            found_prefix = resolve_media_file("media/test_root_sample.png")
            self.assertIsNotNone(found_prefix)
            self.assertEqual(found_prefix.resolve(), test_file.resolve())

            # 3. Embed base64 trong the img
            html_in = '<img src="test_root_sample.png" alt="sample">'
            embedded = embed_images_as_base64(html_in)
            self.assertIn("data:image/png;base64,", embedded)
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_html_img_align_attribute(self):
        raw = '<img src="media/logo.png" align="center" width="120">'
        enhanced = enhance_html_components(raw)
        self.assertIn('class="img-align-center"', enhanced)
        self.assertIn('src="media/logo.png"', enhanced)

    def test_ol_start_counter_reset_injection(self):
        raw = '<ol start="2"><li>Step two</li></ol>'
        enhanced = enhance_html_components(raw)
        self.assertIn('counter-reset: list-item 1;', enhanced)

        raw_multi = '<ol start="5" style="margin: 0;"><li>Step five</li></ol>'
        enhanced_multi = enhance_html_components(raw_multi)
        self.assertIn('counter-reset: list-item 4;', enhanced_multi)
        self.assertIn('margin: 0;', enhanced_multi)


if __name__ == "__main__":
    unittest.main()
