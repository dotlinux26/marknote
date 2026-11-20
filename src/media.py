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

# Regex bat tat ca cac the <img ...> va thuoc tinh src
ALL_IMG_TAG_RE = re.compile(r'<img\b(?P<attrs>[^>]*)>', re.IGNORECASE)
SRC_ATTR_RE = re.compile(r'''src=["'](?P<src>[^"']+)["']''', re.IGNORECASE)


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


def resolve_media_file(src: str | Path) -> Path | None:
    """Tim kiem file anh tren may voi thu muc MEDIA_DIR duoc coi la goc (root).

    Ho tro:
    - filename.png (ngam dinh tim trong MEDIA_DIR)
    - media/filename.png
    - ./filename.png
    - file:///...
    - Absolute path C:/...
    - APP_DIR / filename
    """
    if not src:
        return None
    ensure_media_dir()
    str_src = str(src).strip().replace("\\", "/")
    if str_src.startswith("file:///"):
        qurl = QUrl(str_src)
        local = qurl.toLocalFile()
        if local and Path(local).is_file():
            return Path(local).resolve()
        str_src = local or str_src

    clean_name = str_src
    if clean_name.startswith("media/"):
        clean_name = clean_name[6:]
    elif clean_name.startswith("./"):
        clean_name = clean_name[2:]

    p_direct = Path(str_src)
    p_name = Path(clean_name).name

    candidates = [
        MEDIA_DIR / clean_name,
        MEDIA_DIR / p_name,
        p_direct,
        APP_DIR / clean_name,
        APP_DIR / "media" / p_name,
        Path.cwd() / clean_name,
        Path(__file__).resolve().parent.parent / clean_name,
        Path(__file__).resolve().parent.parent / "assets" / clean_name,
    ]
    for cand in candidates:
        try:
            if cand.is_file():
                return cand.resolve()
        except Exception:
            pass
    return None


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
    """Tao doan ma Markdown chen anh truc tiep tu root (ngam dinh nam trong MEDIA_DIR)."""
    if not alt:
        stem = Path(filename).stem
        alt = stem.replace("_", " ").replace("-", " ").strip() or "image"
    clean_name = filename[6:] if filename.startswith("media/") else filename
    return f"![{alt}]({clean_name})"


def embed_images_as_base64(html: str) -> str:
    """Nhung tat ca anh cuc bo (media/*, file:///, root filename, v.v.) thanh data URI base64 doc lap."""
    ensure_media_dir()

    def _repl_img(match: re.Match) -> str:
        attrs = match.group("attrs") or ""
        src_match = SRC_ATTR_RE.search(attrs)
        if not src_match:
            return match.group(0)
        src = src_match.group("src").strip()
        if src.lower().startswith(("data:", "http://", "https://")):
            return match.group(0)

        found_path = resolve_media_file(src)
        if found_path and found_path.is_file():
            mime, _ = mimetypes.guess_type(str(found_path))
            if not mime:
                ext = found_path.suffix.lower()
                if ext == ".svg":
                    mime = "image/svg+xml"
                elif ext in (".jpg", ".jpeg"):
                    mime = "image/jpeg"
                elif ext == ".webp":
                    mime = "image/webp"
                elif ext == ".gif":
                    mime = "image/gif"
                else:
                    mime = "image/png"
            try:
                data = base64.b64encode(found_path.read_bytes()).decode("ascii")
                new_src_attr = f'src="data:{mime};base64,{data}"'
                new_attrs = attrs[:src_match.start()] + new_src_attr + attrs[src_match.end():]
                return f'<img{new_attrs}>'
            except Exception:
                pass
        return match.group(0)

    return ALL_IMG_TAG_RE.sub(_repl_img, html)


def normalize_size_val(val: str | None) -> str:
    """Chuan hoa gia tri kich thuoc: 100 -> 100px, 50% -> 50%, 100px -> 100px."""
    if not val:
        return ""
    v = str(val).strip()
    if re.match(r"^\d+$", v):
        return f"{v}px"
    return v


MD_IMAGE_EXT_RE = re.compile(
    r'!\[(?P<alt>[^\]]*)\]\((?P<src>[^\s\)]+)(?:\s+(?P<extra>[^\)]*))?\)(?:[ \t]*\{(?P<attrs>[^\}]+)\})?',
    re.IGNORECASE,
)
SIZE_PAIR_RE = re.compile(r"^(\d+(?:px|%|em|rem)?)x(\d+(?:px|%|em|rem)?)$", re.IGNORECASE)
ATTR_KV_RE = re.compile(r"""(?P<key>[\w-]+)\s*=\s*(?:["'](?P<val1>[^"']*)["']|(?P<val2>[^\s]+))""")


def process_markdown_images(md: str) -> str:
    """Xu ly cu phap anh Markdown nang cao:

    1. Thuoc tinh ngoac nhon:
       ![alt](path){width=100px}
       ![alt](path){width=100px height=50px align=center}
       ![alt](path){100px} hoac {100x50} hoac {center} hoac {align=center}
    2. Cú pháp Obsidian / Wiki-style trong alt:
       ![alt|100](path)
       ![alt|100x50](path)
       ![alt|center](path)
       ![alt|100|center](path)
    3. Cú pháp suffix sau URL:
       ![alt](path =100x50) hoac ![alt](path =100x)
    """
    if not md or "![" not in md:
        return md

    lines = md.splitlines(keepends=True)
    out: list[str] = []
    in_code_block = False
    fence_char = ""
    fence_len = 0

    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            char = stripped[0]
            count = len(stripped) - len(stripped.lstrip(char))
            if not in_code_block:
                in_code_block = True
                fence_char = char
                fence_len = count
                out.append(line)
                continue
            elif in_code_block and char == fence_char and count >= fence_len:
                in_code_block = False
                fence_char = ""
                fence_len = 0
                out.append(line)
                continue

        if in_code_block:
            out.append(line)
            continue

        if "![" not in line:
            out.append(line)
            continue

        def _repl(match: re.Match) -> str:
            raw_alt = match.group("alt") or ""
            src = match.group("src") or ""
            extra = (match.group("extra") or "").strip()
            attrs_str = (match.group("attrs") or "").strip()

            width = ""
            height = ""
            align = ""
            title = ""
            custom_style = ""
            alt = raw_alt

            # 1. Parse tu extra sau URL (ví dụ: =100x50 hoặc "title")
            if extra:
                m_dim = re.search(r"=([0-9]+(?:px|%)?)x([0-9]+(?:px|%)?)", extra, re.IGNORECASE)
                if m_dim:
                    width = m_dim.group(1)
                    height = m_dim.group(2)
                else:
                    m_w = re.search(r"=([0-9]+(?:px|%)?)x", extra, re.IGNORECASE)
                    if m_w:
                        width = m_w.group(1)
                    else:
                        m_h = re.search(r"=x([0-9]+(?:px|%)?)", extra, re.IGNORECASE)
                        if m_h:
                            height = m_h.group(1)
                m_title = re.search(r'''["']([^"']+)["']''', extra)
                if m_title:
                    title = m_title.group(1)

            # 2. Parse tu alt dạng Obsidian (alt|100, alt|100x50, alt|center, alt|100|center)
            if "|" in alt:
                parts = [p.strip() for p in alt.split("|")]
                alt = parts[0]
                for p in parts[1:]:
                    p_lower = p.lower()
                    if p_lower in ("center", "centre", "left", "right"):
                        align = "center" if p_lower in ("center", "centre") else p_lower
                    elif SIZE_PAIR_RE.match(p):
                        sm = SIZE_PAIR_RE.match(p)
                        width = sm.group(1)
                        height = sm.group(2)
                    elif re.match(r"^\d+(?:px|%|em|rem)?$", p):
                        width = p

            # 3. Parse tu {attrs}
            has_explicit_attrs = bool(match.group("attrs") is not None)
            if attrs_str:
                for km in ATTR_KV_RE.finditer(attrs_str):
                    k = km.group("key").lower()
                    v = km.group("val1") if km.group("val1") is not None else km.group("val2")
                    v = v.strip() if v else ""
                    if k in ("width", "w"):
                        width = v
                    elif k in ("height", "h"):
                        height = v
                    elif k in ("align", "text-align"):
                        align = "center" if v.lower() in ("center", "centre") else v.lower()
                    elif k == "style":
                        custom_style = v

                # Parse cac token dung doc lap trong {attrs} (vi du: {center}, {100px}, {100x50}, {#center})
                tokens = re.split(r"[\s,]+", attrs_str)
                for tok in tokens:
                    tok_clean = tok.strip().lstrip("#.").lower()
                    if tok_clean in ("center", "centre", "left", "right"):
                        align = "center" if tok_clean in ("center", "centre") else tok_clean
                    elif SIZE_PAIR_RE.match(tok):
                        sm = SIZE_PAIR_RE.match(tok)
                        width = sm.group(1)
                        height = sm.group(2)
                    elif re.match(r"^\d+(?:px|%|em|rem)?$", tok) and not width:
                        width = tok

            # Neu khong co thuoc tinh dac biet va khong co {...}, giu nguyen Markdown
            if not width and not height and not align and not custom_style and not has_explicit_attrs:
                return match.group(0)

            # Chuan hoa width, height
            width_norm = normalize_size_val(width)
            height_norm = normalize_size_val(height)

            style_list = ["max-width: 100%"]
            if width_norm:
                style_list.append(f"width: {width_norm}")
            if height_norm:
                style_list.append(f"height: {height_norm}")
            if custom_style:
                style_list.append(custom_style.strip(";"))

            title_attr = f' title="{title}"' if title else ""
            alt_attr = f' alt="{alt}"' if alt else ' alt=""'

            if align == "center":
                style_list.append("display: inline-block")
                style_list.append("margin: 0 auto")
                style_str = "; ".join(style_list)
                return (
                    f'<div class="img-align-center" style="text-align: center; margin: 1.2rem 0;">'
                    f'<img src="{src}"{alt_attr}{title_attr} style="{style_str}">'
                    f'</div>'
                )
            elif align == "left":
                style_list.append("display: inline-block")
                style_str = "; ".join(style_list)
                return (
                    f'<div class="img-align-left" style="text-align: left; margin: 1.2rem 0;">'
                    f'<img src="{src}"{alt_attr}{title_attr} style="{style_str}">'
                    f'</div>'
                )
            elif align == "right":
                style_list.append("display: inline-block")
                style_str = "; ".join(style_list)
                return (
                    f'<div class="img-align-right" style="text-align: right; margin: 1.2rem 0;">'
                    f'<img src="{src}"{alt_attr}{title_attr} style="{style_str}">'
                    f'</div>'
                )
            else:
                style_str = "; ".join(style_list)
                return f'<img src="{src}"{alt_attr}{title_attr} style="{style_str}">'

        new_line = MD_IMAGE_EXT_RE.sub(_repl, line)
        out.append(new_line)

    return "".join(out)



