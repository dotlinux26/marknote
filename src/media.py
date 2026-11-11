"""Quan ly thu muc media dung chung (anh nhung, paste tu clipboard, keo tha)."""

from __future__ import annotations

import base64
import mimetypes
import re
import shutil
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices, QImage

from settings import APP_DIR, MEDIA_DIR

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico"}

IMG_TAG_RE = re.compile(
    r'<img\s+([^>]*?)src=["\'](media/[^"\']+|file:///[^"\']+)["\']',
    re.IGNORECASE,
)


def ensure_media_dir() -> Path:
    """Dam bao thu muc media dung chung ton tai tren may."""
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    return MEDIA_DIR


def is_image_path(path: Path | str) -> bool:
    """Kiem tra duoi mo rong cua file co phai la anh khong."""
    return Path(path).suffix.lower() in IMAGE_EXTENSIONS


def is_image_url(url: QUrl) -> bool:
    """Kiem tra QUrl co tro den file anh cuc bo khong."""
    if not url.isLocalFile():
        return False
    return is_image_path(url.toLocalFile())


def open_media_folder() -> bool:
    """Mo thu muc media dung chung trong trinh quan ly file he thong (Explorer)."""
    ensure_media_dir()
    return QDesktopServices.openUrl(QUrl.fromLocalFile(str(MEDIA_DIR.resolve())))


def copy_file_to_media(src: Path | str) -> str:
    """Sao chep file anh tu ngoai vao MEDIA_DIR, xu ly trung ten va tra ve filename."""
    ensure_media_dir()
    src_path = Path(src).resolve()
    if not src_path.is_file():
        raise FileNotFoundError(f"File not found: {src_path}")

    # Neu da nam san trong MEDIA_DIR thi giu nguyen ten
    try:
        if src_path.parent.resolve() == MEDIA_DIR.resolve():
            return src_path.name
    except Exception:
        pass

    stem = src_path.stem
    ext = src_path.suffix.lower() or ".png"
    clean_stem = re.sub(r"[^\w\-.]+", "_", stem).strip("_") or "image"
    dest = MEDIA_DIR / f"{clean_stem}{ext}"

    if not dest.exists():
        shutil.copy2(src_path, dest)
        return dest.name

    # Kiem tra neu trung noi dung voi file da co
    src_bytes = src_path.read_bytes()
    if dest.read_bytes() == src_bytes:
        return dest.name

    # Trung ten nhung noi dung khac: them hau to _1, _2,...
    i = 1
    while True:
        candidate = MEDIA_DIR / f"{clean_stem}_{i}{ext}"
        if not candidate.exists():
            candidate.write_bytes(src_bytes)
            return candidate.name
        if candidate.read_bytes() == src_bytes:
            return candidate.name
        i += 1


def save_qimage_to_media(qimage: QImage) -> str:
    """Luu doi tuong QImage (paste tu clipboard / chup man hinh) thanh PNG trong MEDIA_DIR."""
    ensure_media_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate_name = f"img_{timestamp}.png"
    dest = MEDIA_DIR / candidate_name
    i = 1
    while dest.exists():
        candidate_name = f"img_{timestamp}_{i}.png"
        dest = MEDIA_DIR / candidate_name
        i += 1
    qimage.save(str(dest), "PNG")
    return candidate_name


def make_markdown_image_tag(filename: str, alt: str = "") -> str:
    """Tao doan ma Markdown chen anh theo quy uoc media/<filename>."""
    if not alt:
        stem = Path(filename).stem
        alt = stem.replace("_", " ").replace("-", " ").strip() or "image"
    return f"![{alt}](media/{filename})"


def embed_images_as_base64(html: str) -> str:
    """Nhung tat ca anh cuc bo (media/* hoac file:///) thanh data URI base64 doc lap."""
    ensure_media_dir()

    def _repl(match):
        attrs = match.group(1)
        src = match.group(2)
        target_path = None
        if src.startswith("media/"):
            target_path = MEDIA_DIR / src[6:]
        elif src.startswith("file:///"):
            qurl = QUrl(src)
            local = qurl.toLocalFile()
            if local:
                target_path = Path(local)

        if target_path and target_path.is_file():
            mime, _ = mimetypes.guess_type(str(target_path))
            if not mime:
                mime = "image/png"
            data = base64.b64encode(target_path.read_bytes()).decode("ascii")
            return f'<img {attrs}src="data:{mime};base64,{data}"'
        return match.group(0)

    return IMG_TAG_RE.sub(_repl, html)

