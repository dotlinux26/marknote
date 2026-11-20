import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_dir))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage, QTextCursor
from PySide6.QtCore import QMimeData, QUrl
import tempfile

app = QApplication.instance() or QApplication(sys.argv)

from settings import MEDIA_DIR, APP_DIR
from media import (
    ensure_media_dir,
    copy_file_to_media,
    save_qimage_to_media,
    make_markdown_image_tag,
    embed_images_as_base64,
    is_image_path,
)
from editor import EditorPane
from exporter import Exporter

print("--- Test 1: Media directory ---")
m_dir = ensure_media_dir()
assert m_dir.exists(), "Media dir must exist"
print("OK:", m_dir)

print("--- Test 2: Copy file to media ---")
with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
    f.write(b"sample png content 123")
    tmp_path = Path(f.name)

name1 = copy_file_to_media(tmp_path)
print("Copied name 1:", name1)
assert (MEDIA_DIR / name1).exists()

# Copy same content again -> should return same name
name2 = copy_file_to_media(tmp_path)
assert name1 == name2, f"Expected same name for identical file, got {name2}"

# Copy different content with same stem -> should return _1
tmp_path.write_bytes(b"different content 456")
name3 = copy_file_to_media(tmp_path)
print("Copied name 3 (different content):", name3)
assert name3 != name1, "Should have different name for different content"
assert (MEDIA_DIR / name3).exists()
tmp_path.unlink()

print("--- Test 3: Save QImage to media ---")
qimg = QImage(10, 10, QImage.Format.Format_ARGB32)
qimg.fill(0xFFFF0000)
qname = save_qimage_to_media(qimg)
print("Saved QImage name:", qname)
assert (MEDIA_DIR / qname).exists()

print("--- Test 4: Editor cursor insertion ---")
editor = EditorPane()
editor.setText("Hello World")

# Place cursor between 'Hello ' and 'World' (position 6)
cursor = editor.textCursor()
cursor.setPosition(6)
editor.setTextCursor(cursor)

inserted_name = editor.insertImageFromFile(MEDIA_DIR / qname)
assert inserted_name == qname
expected_text = f"Hello {make_markdown_image_tag(qname)}World"
assert editor.getText() == expected_text, f"Got: {editor.getText()}"
print("Cursor insertion OK!")

print("--- Test 5: Paste QImage (Ctrl+V) via insertFromMimeData ---")
editor.setText("Before After")
c = editor.textCursor()
c.setPosition(7)  # Between 'Before ' and 'After'
editor.setTextCursor(c)

mime = QMimeData()
mime.setImageData(qimg)
editor.insertFromMimeData(mime)
text = editor.getText()
assert "img_" in text, f"Expected img_ in text, got: {text}"
print("Paste QImage OK! Result text:", text)

print("--- Test 6: Paste Image File URLs ---")
editor.setText("Start End")
c = editor.textCursor()
c.setPosition(6)
editor.setTextCursor(c)

mime2 = QMimeData()
mime2.setUrls([QUrl.fromLocalFile(str(MEDIA_DIR / name1))])
editor.insertFromMimeData(mime2)
text2 = editor.getText()
assert name1 in text2, f"Expected {name1} in text2, got: {text2}"
print("Paste File URLs OK! Result text:", text2)

print("--- Test 7: HTML Base64 Embedding (Root filename & media/ prefix) ---")
html_input = f'<p>Note</p><img alt="pic" src="media/{qname}"><img alt="pic2" src="{name1}">'
html_embedded = embed_images_as_base64(html_input)
assert html_embedded.count("data:image/png;base64,") == 2, f"Expected 2 embedded images, got: {html_embedded}"
print("HTML Base64 Embedding OK!")

print("--- Test 8: Markdown Image Dimensions and Align Formatting ---")
from media import process_markdown_images
md_test = f"![signature]({qname}){{width=100px align=center}}"
processed_md = process_markdown_images(md_test)
assert '<div class="img-align-center"' in processed_md, f"Expected center div, got: {processed_md}"
assert 'width: 100px' in processed_md, f"Expected width: 100px, got: {processed_md}"
assert f'src="{qname}"' in processed_md, f"Expected src {qname}, got: {processed_md}"

md_obsidian = f"![signature|150|center]({qname})"
processed_obsidian = process_markdown_images(md_obsidian)
assert '<div class="img-align-center"' in processed_obsidian
assert 'width: 150px' in processed_obsidian

md_suffix = f"![pic]({name1} =200x100)"
processed_suffix = process_markdown_images(md_suffix)
assert 'width: 200px' in processed_suffix and 'height: 100px' in processed_suffix
print("Markdown Image Dimensions & Align OK!")

print("--- ALL TESTS PASSED! ---")
