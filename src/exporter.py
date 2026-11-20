"""Xuat HTML va PDF voi CSS cua theme da chon, nhung inline."""

from __future__ import annotations

import base64
import io
import os
import re
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

from media import embed_images_as_base64, resolve_media_file, process_markdown_images
from settings import APP_DIR, MEDIA_DIR

CHECKBOX_TAG_RE = re.compile(
    r'<input\b[^>]*class=["\'][^"\']*task-list-item-checkbox[^"\']*["\'][^>]*>'
)

UNCHECKED_SVG = (
    '<svg class="task-svg task-unchecked" width="15" height="15" viewBox="0 0 16 16" fill="none" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<rect x="1.5" y="1.5" width="13" height="13" rx="3" stroke="#8c959f" stroke-width="1.8" fill="#ffffff"/>'
    '</svg>'
)

CHECKED_SVG = (
    '<svg class="task-svg task-checked" width="15" height="15" viewBox="0 0 16 16" fill="none" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<rect x="1" y="1" width="14" height="14" rx="3" fill="#0969da" stroke="#0969da" stroke-width="1"/>'
    '<path d="M4.5 8L7 10.5L11.5 5.5" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg>'
)

DEFAULT_DONUT_SVG = (
    '<svg viewBox="0 0 36 36" class="donut-svg-ring" style="width: 110px; height: 110px; position: absolute; top: 0; left: 0; transform: rotate(-90deg); border-radius: 50%;">'
    '<circle cx="18" cy="18" r="15.9155" fill="#ffffff"></circle>'
    '<circle cx="18" cy="18" r="15.9155" fill="transparent" stroke="#3182ce" stroke-width="4.5" stroke-dasharray="40 60" stroke-dashoffset="0"></circle>'
    '<circle cx="18" cy="18" r="15.9155" fill="transparent" stroke="#d69e2e" stroke-width="4.5" stroke-dasharray="40 60" stroke-dashoffset="-40"></circle>'
    '<circle cx="18" cy="18" r="15.9155" fill="transparent" stroke="#dd6b20" stroke-width="4.5" stroke-dasharray="20 80" stroke-dashoffset="-80"></circle>'
    '</svg>'
)

CATEGORY_CONFIG = [
    ("critical", "Critical", "#c53030", "dot-crit", [r"^crit(?:ical)?\b"]),
    ("high", "High", "#dd6b20", "dot-high", [r"^high\b"]),
    ("medium", "Medium", "#d69e2e", "dot-med", [r"^med(?:ium)?\b"]),
    ("low", "Low", "#3182ce", "dot-low", [r"^low\b"]),
    ("info", "Info", "#0284c7", "dot-info", [r"^info\b"]),
]

DONUT_DIRECTIVE_RE = re.compile(r"\[\[donut(?P<body>.*?)\]\]", re.IGNORECASE)


def parse_donut_spec(text: str):
    """Phan tich cu phap donut linh hoat tu code fence hoac directive."""
    total = None
    label = "Issues"
    counts = {}

    lines = [line.strip() for line in re.split(r"[\r\n|,;]+", text) if line.strip()]
    for line in lines:
        m_tot_lbl = re.match(r"^(\d+)\s+([a-zA-Z0-9_\-\s]+)$", line)
        if m_tot_lbl:
            total = int(m_tot_lbl.group(1))
            label = m_tot_lbl.group(2).strip()
            continue

        m_tot = re.match(r"^(?:total|sum)\s*[:=]\s*(\d+)", line, re.IGNORECASE)
        if m_tot:
            total = int(m_tot.group(1))
            continue

        m_lbl = re.match(r"^(?:label|title)\s*[:=]\s*([a-zA-Z0-9_\-\s]+)", line, re.IGNORECASE)
        if m_lbl:
            label = m_lbl.group(1).strip()
            continue

        matched = False
        for key, display_name, color, dot_class, patterns in CATEGORY_CONFIG:
            for pat in patterns:
                m = re.search(pat + r"\s*[:=]\s*(\d+)", line, re.IGNORECASE)
                if m:
                    counts[key] = int(m.group(1))
                    matched = True
                    break
            if matched:
                break

    default_keys = ["critical", "high", "medium", "low"]
    for k in default_keys:
        if k not in counts:
            counts[k] = 0

    sum_counts = sum(counts.values())
    if total is None:
        total = sum_counts

    return total, label, counts


def render_donut_widget(text: str) -> str:
    """Tao HTML Donut Chart vector SVG can giua, khong vien/nen."""
    total, label, counts = parse_donut_spec(text)

    svg_circles = []
    svg_circles.append('<circle cx="18" cy="18" r="15.9155" fill="#ffffff"></circle>')

    if total <= 0:
        svg_circles.append(
            '<circle cx="18" cy="18" r="15.9155" fill="transparent" '
            'stroke="#e2e8f0" stroke-width="4.5"></circle>'
        )
    else:
        current_offset = 0.0
        draw_order = ["low", "medium", "high", "critical", "info"]
        for key in draw_order:
            val = counts.get(key, 0)
            if val <= 0:
                continue
            pct = (val / total) * 100.0
            color = next(c[2] for c in CATEGORY_CONFIG if c[0] == key)
            svg_circles.append(
                f'<circle cx="18" cy="18" r="15.9155" fill="transparent" '
                f'stroke="{color}" stroke-width="4.5" '
                f'stroke-dasharray="{pct:.2f} {100.0 - pct:.2f}" '
                f'stroke-dashoffset="{-current_offset:.2f}"></circle>'
            )
            current_offset += pct

    svg_content = (
        '<svg viewBox="0 0 36 36" class="donut-svg-ring">\n'
        + "\n".join("        " + c for c in svg_circles)
        + "\n      </svg>"
    )

    legend_items = []
    display_order = ["critical", "high", "medium", "low"]
    for key in display_order:
        val = counts.get(key, 0)
        item_cfg = next(c for c in CATEGORY_CONFIG if c[0] == key)
        display_name = item_cfg[1]
        dot_class = item_cfg[3]
        color = item_cfg[2]
        legend_items.append(
            f'<div class="legend-item">'
            f'<span class="dot {dot_class}" style="background-color: {color};"></span> '
            f'{display_name}: <b>{val}</b>'
            f'</div>'
        )

    legend_html = "\n".join("        " + it for it in legend_items)

    return f"""<div class="donut-widget">
  <div class="donut-widget-inner">
    <div class="donut-chart">
      {svg_content}
      <div class="donut-center">
        <b>{total}</b>
        <span>{escape(label)}</span>
      </div>
    </div>
    <div class="donut-legend">
{legend_html}
    </div>
  </div>
</div>"""


def replace_checkboxes_with_svg(html: str) -> str:
    """Thay the checkbox mac dinh bang vector SVG sac net va can le chuan."""
    if not html or "task-list-item-checkbox" not in html:
        return html

    def _repl(m: re.Match) -> str:
        tag = m.group(0)
        return CHECKED_SVG if "checked" in tag else UNCHECKED_SVG

    return CHECKBOX_TAG_RE.sub(_repl, html)


PRINT_DIRECTIVE_RE = re.compile(
    r"\[\[\s*(?P<type>print|page-bg)\b(?P<body>.*?)\]\]",
    re.IGNORECASE | re.DOTALL,
)

PRINT_DIRECTIVE_STRIP_RE = re.compile(
    r"(?:<p>\s*)?\[\[\s*(?P<type>print|page-bg)\b(?P<body>.*?)\]\](?:\s*</p>)?",
    re.IGNORECASE | re.DOTALL,
)

PRINT_ATTR_RE = re.compile(
    r"""(?P<key>[\w-]+)\s*[=:]\s*(?:\"(?P<val_dq>[^\"]*)\"|'(?P<val_sq>[^']*)'|(?P<val_fn>[\w-]+\((?:[^()]+|\([^()]*\))*\))|(?P<val_uq>[^\s,;]+))""",
    re.IGNORECASE,
)


class PrintDirectiveConfig:
    """Cau hinh cho chi thi in an [[print ...]] va [[page-bg ...]]."""

    def __init__(
        self,
        directive_type: str = "print",
        bg: str = "",
        mode: str = "cover",
        position: str = "center",
        opacity: float = 1.0,
        bg_color: str = "",
        gradient: str = "",
        text_color: str = "",
        pages: str = "all",
        style: str = "",
        margin: str = "",
    ):
        self.directive_type = directive_type
        self.bg = bg
        self.mode = mode
        self.position = position
        self.opacity = opacity
        self.bg_color = bg_color
        self.gradient = gradient
        self.text_color = text_color
        self.pages = pages
        self.style = style
        self.margin = margin

    def __repr__(self) -> str:
        return (
            f"PrintDirectiveConfig(type={self.directive_type!r}, bg={self.bg!r}, "
            f"mode={self.mode!r}, position={self.position!r}, opacity={self.opacity!r}, "
            f"bg_color={self.bg_color!r}, gradient={self.gradient!r}, "
            f"text_color={self.text_color!r}, pages={self.pages!r}, style={self.style!r}, "
            f"margin={self.margin!r})"
        )


def parse_page_targets(pages_str: str) -> list[str | int]:
    """Phan tich chuoi trang (all, 1, 1-2, 1,3,5, odd, even) thanh danh sach target."""
    if not pages_str:
        return ["all"]
    s = str(pages_str).strip().lower()
    if s in ("all", "*", ":all"):
        return ["all"]
    if s in ("first", ":first"):
        return [1]
    if s in ("odd", ":right"):
        return ["odd"]
    if s in ("even", ":left"):
        return ["even"]

    results: list[str | int] = []
    parts = re.split(r"[,;]+", s)
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if p in ("all", "*", ":all"):
            return ["all"]
        if p in ("first", ":first"):
            results.append(1)
            continue
        if p in ("odd", ":right"):
            results.append("odd")
            continue
        if p in ("even", ":left"):
            results.append("even")
            continue
        if "-" in p:
            range_match = re.match(r"^(\d+)\s*-\s*(\d+)$", p)
            if range_match:
                start = int(range_match.group(1))
                end = int(range_match.group(2))
                if start <= end:
                    results.extend(range(start, end + 1))
                else:
                    results.extend(range(end, start + 1))
                continue
        try:
            results.append(int(p))
        except ValueError:
            pass

    seen = set()
    deduped: list[str | int] = []
    for item in results:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped if deduped else ["all"]


def parse_directive_attributes(body: str) -> dict[str, str]:
    """Trich xuat cac cap key=val hoac key='...' tu than directive."""
    attrs: dict[str, str] = {}
    for m in PRINT_ATTR_RE.finditer(body):
        k = m.group("key").lower()
        val = (
            m.group("val_dq")
            if m.group("val_dq") is not None
            else (
                m.group("val_sq")
                if m.group("val_sq") is not None
                else (m.group("val_fn") if m.group("val_fn") is not None else m.group("val_uq"))
            )
        )
        if val is not None:
            attrs[k] = val.strip()
    return attrs


def parse_print_directive(text: str) -> PrintDirectiveConfig:
    """Phan tich cu phap directive [[print ...]] hoac [[page-bg ...]]."""
    m = re.search(r"\[\[\s*(?P<type>print|page-bg)\b(?P<body>.*?)\]\]", text, re.IGNORECASE | re.DOTALL)
    if m:
        directive_type = m.group("type").lower()
        body = m.group("body") or ""
    else:
        directive_type = "print"
        body = text

    kv = parse_directive_attributes(body)

    # 1. bg / image / src / paper / watermark
    bg = ""
    for k in ("bg", "image", "src", "bg-image", "background", "background-image", "paper", "watermark"):
        if k in kv:
            bg = kv[k].strip()
            break

    # 2. mode / fit / repeat (repeat, tile, repeat-x, repeat-y, stretch, cover, contain)
    mode = "cover"
    for k in ("mode", "fit", "size", "background-size", "bg-size", "bg-mode", "repeat", "background-repeat"):
        if k in kv:
            mode = kv[k].strip().lower()
            break
    else:
        for bword in ("repeat-x", "repeat-y", "stretch", "cover", "contain", "repeat", "tile"):
            if re.search(r"\b" + re.escape(bword) + r"\b", body, re.IGNORECASE):
                mode = bword.lower()
                break

    if mode in ("tile", "repeat"):
        mode = "repeat"
    elif mode in ("repeat-x", "repeat_x"):
        mode = "repeat-x"
    elif mode in ("repeat-y", "repeat_y"):
        mode = "repeat-y"
    elif mode in ("stretch", "contain", "cover"):
        pass
    else:
        mode = "cover"

    # 3. position
    position = "center"
    for k in ("position", "pos", "background-position", "bg-pos", "bg-position", "align"):
        if k in kv:
            position = kv[k].strip()
            break
    else:
        pos_patterns = [
            r"\b(top\s+left)\b",
            r"\b(top\s+right)\b",
            r"\b(bottom\s+left)\b",
            r"\b(bottom\s+right)\b",
            r"\b(top\s+center)\b",
            r"\b(bottom\s+center)\b",
            r"\b(center\s+left)\b",
            r"\b(center\s+right)\b",
            r"\b(center\s+center)\b",
            r"\b(center)\b",
            r"\b(top)\b",
            r"\b(bottom)\b",
            r"\b(left)\b",
            r"\b(right)\b",
        ]
        for ppat in pos_patterns:
            m_pos = re.search(ppat, body, re.IGNORECASE)
            if m_pos:
                position = m_pos.group(1).lower()
                break

    # 4. opacity / alpha (adjust image alpha via Pillow)
    opacity = 1.0
    for k in ("opacity", "alpha", "bg-opacity", "image-opacity"):
        if k in kv:
            val_str = kv[k].strip()
            if val_str.endswith("%"):
                try:
                    opacity = float(val_str[:-1].strip()) / 100.0
                except ValueError:
                    pass
            else:
                try:
                    val_num = float(val_str)
                    if val_num > 1.0 and val_num <= 100.0:
                        opacity = val_num / 100.0
                    else:
                        opacity = val_num
                except ValueError:
                    pass
            break
    opacity = max(0.0, min(1.0, opacity))

    # 5. bg-color / gradient (linear-gradient/radial-gradient)
    bg_color = ""
    gradient = ""
    for k in ("bg-color", "bgcolor", "bg_color", "background-color", "color-bg"):
        if k in kv:
            val = kv[k].strip()
            if "gradient" in val.lower():
                gradient = val
            else:
                bg_color = val
            break

    for k in ("gradient", "bg-gradient", "background-gradient"):
        if k in kv:
            val = kv[k].strip()
            if "gradient" in val.lower():
                gradient = val
            else:
                bg_color = val
            break

    if bg and "gradient" in bg.lower():
        gradient = bg
        bg = ""

    # 6. text-color
    text_color = ""
    for k in ("text-color", "textcolor", "text_color", "color", "fg", "fg-color"):
        if k in kv:
            text_color = kv[k].strip()
            break

    # 7. pages / page (all, 1, 1-2, 1,3,5)
    pages = "all"
    for k in ("pages", "page", "target-pages", "target-page", "targets"):
        if k in kv:
            pages = kv[k].strip()
            break
    else:
        for pword in ("all", "odd", "even", "first"):
            if re.search(r"\b" + pword + r"\b", body, re.IGNORECASE):
                pages = pword
                break

    # 8. custom CSS style
    style = ""
    for k in ("style", "css", "custom-style", "custom_style"):
        if k in kv:
            style = kv[k].strip()
            break

    # 9. page margin (vi du margin="0" hoac margin="10mm")
    margin = ""
    for k in ("margin", "page-margin", "page_margin"):
        if k in kv:
            margin = kv[k].strip()
            break
    if not margin:
        if re.search(r"\bmargin\s*=\s*(?:\"0\"|'0'|0)\b", body, re.IGNORECASE):
            margin = "0"

    return PrintDirectiveConfig(
        directive_type=directive_type,
        bg=bg,
        mode=mode,
        position=position,
        opacity=opacity,
        bg_color=bg_color,
        gradient=gradient,
        text_color=text_color,
        pages=pages,
        style=style,
        margin=margin,
    )


def parse_print_directives(text: str) -> list[PrintDirectiveConfig]:
    """Trich xuat toan bo chi thi [[print ...]] va [[page-bg ...]] trong van ban."""
    if not text:
        return []
    configs: list[PrintDirectiveConfig] = []
    for m in PRINT_DIRECTIVE_RE.finditer(text):
        cfg = parse_print_directive(m.group(0))
        configs.append(cfg)
    return configs


def resolve_image_file(path_or_str: str | Path) -> Path | None:
    """Tim kiem file anh hop le, coi thu muc MEDIA_DIR la root."""
    return resolve_media_file(path_or_str)


def adjust_image_alpha(img_input: str | Path | bytes, alpha: float) -> str:
    """Dieu chinh do trong suot (alpha) cua anh bang Pillow va tra ve data URI base64."""
    alpha = max(0.0, min(1.0, float(alpha)))
    img = None
    try:
        from PIL import Image

        if isinstance(img_input, bytes):
            img = Image.open(io.BytesIO(img_input))
        elif isinstance(img_input, (str, Path)):
            str_val = str(img_input).strip()
            if str_val.startswith("data:image/"):
                comma_idx = str_val.find(",")
                if comma_idx != -1:
                    raw_b64 = str_val[comma_idx + 1 :]
                    img = Image.open(io.BytesIO(base64.b64decode(raw_b64)))
            else:
                found_path = resolve_image_file(str_val)
                if found_path:
                    img = Image.open(found_path)

        if img is not None:
            rgba = img.convert("RGBA")
            if alpha < 1.0:
                r, g, b, a = rgba.split()
                a = a.point(lambda p: max(0, min(255, int(round(p * alpha)))))
                rgba.putalpha(a)
            buf = io.BytesIO()
            rgba.save(buf, format="PNG")
            b64_str = base64.b64encode(buf.getvalue()).decode("ascii")
            return f"data:image/png;base64,{b64_str}"
    except Exception:
        pass

    str_val = str(img_input).strip() if isinstance(img_input, (str, Path)) else ""
    return str_val


def generate_page_css(directives: list[PrintDirectiveConfig] | PrintDirectiveConfig) -> str:
    """Tao cac quy tac @page CSS hop le tu danh sach PrintDirectiveConfig."""
    if isinstance(directives, PrintDirectiveConfig):
        directive_list = [directives]
    else:
        directive_list = directives or []

    if not directive_list:
        return ""

    css_blocks: list[str] = []
    print_media_styles: list[str] = []

    for cfg in directive_list:
        image_uri = ""
        if cfg.bg:
            bg_clean = cfg.bg.strip()
            url_match = re.match(r"^url\([\"']?(.*?)[\"']?\)$", bg_clean, re.IGNORECASE)
            if url_match:
                bg_clean = url_match.group(1).strip()

            processed = adjust_image_alpha(bg_clean, cfg.opacity)
            if processed.startswith("data:") or processed.startswith("http://") or processed.startswith("https://"):
                image_uri = f'url("{processed}")'
            elif processed:
                image_uri = f'url("{processed}")'

        props: list[str] = []

        if image_uri and cfg.gradient:
            props.append(f"background-image: {image_uri}, {cfg.gradient};")
        elif image_uri:
            props.append(f"background-image: {image_uri};")
        elif cfg.gradient:
            props.append(f"background-image: {cfg.gradient};")

        if cfg.mode in ("repeat", "tile"):
            props.append("background-repeat: repeat;")
            props.append("background-size: auto;")
        elif cfg.mode == "repeat-x":
            props.append("background-repeat: repeat-x;")
            props.append("background-size: auto;")
        elif cfg.mode == "repeat-y":
            props.append("background-repeat: repeat-y;")
            props.append("background-size: auto;")
        elif cfg.mode == "stretch":
            props.append("background-repeat: no-repeat;")
            props.append("background-size: 100% 100%;")
        elif cfg.mode == "contain":
            props.append("background-repeat: no-repeat;")
            props.append("background-size: contain;")
        else:  # cover
            props.append("background-repeat: no-repeat;")
            props.append("background-size: cover;")

        if cfg.position:
            pos_clean = re.sub(r"[{};]", "", cfg.position).strip()
            if pos_clean:
                props.append(f"background-position: {pos_clean};")

        if cfg.bg_color:
            color_val = cfg.bg_color.strip().rstrip(";")
            color_val = re.sub(r"[{}]", "", color_val).strip()
            if cfg.opacity < 1.0 and color_val.startswith("#") and len(color_val) in (4, 7):
                try:
                    if len(color_val) == 7:
                        r = int(color_val[1:3], 16)
                        g = int(color_val[3:5], 16)
                        b = int(color_val[5:7], 16)
                    else:
                        r = int(color_val[1] * 2, 16)
                        g = int(color_val[2] * 2, 16)
                        b = int(color_val[3] * 2, 16)
                    color_val = f"rgba({r}, {g}, {b}, {cfg.opacity:.2f})"
                except ValueError:
                    pass
            elif cfg.opacity < 1.0 and color_val.lower().startswith("rgb("):
                m_rgb = re.match(r"^rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$", color_val, re.IGNORECASE)
                if m_rgb:
                    color_val = f"rgba({m_rgb.group(1)}, {m_rgb.group(2)}, {m_rgb.group(3)}, {cfg.opacity:.2f})"
            props.append(f"background-color: {color_val};")

        if cfg.text_color:
            tc = re.sub(r"[{};]", "", cfg.text_color).strip()
            if tc:
                props.append(f"color: {tc};")
                props.append(f"@bottom-center {{ color: {tc} !important; }}")
                props.append(f"@top-center {{ color: {tc} !important; }}")
                props.append(f"@bottom-left {{ color: {tc} !important; }}")
                props.append(f"@bottom-right {{ color: {tc} !important; }}")
                props.append(f"@top-left {{ color: {tc} !important; }}")
                props.append(f"@top-right {{ color: {tc} !important; }}")

        if cfg.style:
            clean_style = re.sub(r"[{}]", "", cfg.style).strip()
            decls = [d.strip() for d in re.split(r"[;\n]+", clean_style) if d.strip()]
            for decl in decls:
                if ":" in decl:
                    prop_name, prop_val = decl.split(":", 1)
                    prop_name = prop_name.strip()
                    prop_val = prop_val.strip()
                    if re.match(r"^[a-zA-Z_-][a-zA-Z0-9_-]*$", prop_name) and prop_val:
                        props.append(f"{prop_name}: {prop_val};")

        if cfg.margin:
            props.append(f"margin: {cfg.margin} !important;")

        targets = parse_page_targets(cfg.pages)
        inner_css = "\n".join("  " + p for p in props)

        for target in targets:
            if target == "all":
                css_blocks.append(f"@page {{\n{inner_css}\n}}")
                if cfg.text_color:
                    tc = re.sub(r"[{};]", "", cfg.text_color).strip()
                    if tc:
                        print_media_styles.append(
                            f"body, .markdown-body {{ color: {tc} !important; }}"
                        )
            elif target == 1:
                first_props = list(props)
                # An so trang mac dinh o trang 1 khi co background rieng
                first_props.append("@bottom-center { content: none !important; }")
                first_props.append("@bottom-left { content: none !important; }")
                first_props.append("@bottom-right { content: none !important; }")
                first_inner = "\n".join("  " + p for p in first_props)
                css_blocks.append(f"@page :first {{\n{first_inner}\n}}")
                css_blocks.append(f"@page :nth(1) {{\n{first_inner}\n}}")
            elif target == "odd":
                css_blocks.append(f"@page :right {{\n{inner_css}\n}}")
                css_blocks.append(f"@page :nth(odd) {{\n{inner_css}\n}}")
            elif target == "even":
                css_blocks.append(f"@page :left {{\n{inner_css}\n}}")
                css_blocks.append(f"@page :nth(even) {{\n{inner_css}\n}}")
            else:
                css_blocks.append(f"@page :nth({target}) {{\n{inner_css}\n}}")

    result = "\n" + "\n\n".join(css_blocks) + "\n"
    if print_media_styles:
        result += "\n@media print {\n  " + "\n  ".join(print_media_styles) + "\n}\n"
    return result


HTML_IMG_TAG_RE = re.compile(r'<img\b(?P<attrs>[^>]*)>', re.IGNORECASE)


def _normalize_html_img_tags(html: str) -> str:
    """Chuan hoa cac the <img> co thuoc tinh align='center|left|right' thanh khoi can le dep."""
    def _repl(m: re.Match) -> str:
        tag = m.group(0)
        attrs = m.group("attrs") or ""
        align_m = re.search(r'\balign=["\']?(center|centre|left|right)["\']?', attrs, re.IGNORECASE)
        if not align_m:
            return tag
        al = align_m.group(1).lower()
        clean_tag = re.sub(r'\s*\balign=["\']?(?:center|centre|left|right)["\']?', '', tag, flags=re.IGNORECASE)
        if al in ("center", "centre"):
            return f'<div class="img-align-center" style="text-align: center; margin: 1.2rem 0;">{clean_tag}</div>'
        elif al == "left":
            return f'<div class="img-align-left" style="text-align: left; margin: 1.2rem 0;">{clean_tag}</div>'
        elif al == "right":
            return f'<div class="img-align-right" style="text-align: right; margin: 1.2rem 0;">{clean_tag}</div>'
        return tag

    return HTML_IMG_TAG_RE.sub(_repl, html)


def enhance_html_components(html: str) -> str:
    """Thay the checkbox bang SVG, ho tro donut directive, xoa raw print tokens, chuan hoa anh."""
    if not html:
        return html
    html = replace_checkboxes_with_svg(html)
    html = _normalize_html_img_tags(html)
    if "[[donut" in html.lower():
        html = DONUT_DIRECTIVE_RE.sub(lambda m: render_donut_widget(m.group("body")), html)
    if "donut-chart" in html and "donut-svg-ring" not in html:
        html = re.sub(
            r'(<div\b[^>]*class=["\'][^"\']*donut-chart[^"\']*["\'][^>]*>)',
            r'\1\n' + DEFAULT_DONUT_SVG,
            html,
            count=0,
            flags=re.IGNORECASE,
        )
    if PRINT_DIRECTIVE_RE.search(html):
        html = PRINT_DIRECTIVE_STRIP_RE.sub("", html)
        html = re.sub(r"<p>\s*</p>", "", html)
    return html


DOCUMENT_BASE_CSS = (
    "\n/* MarkNote Base Document Styles: Tasklists, Tables, Code Blocks, and TOC */\n"
    ".markdown-body ul.contains-task-list,\n"
    ".markdown-body ol.contains-task-list {\n"
    "  list-style: none !important;\n"
    "  list-style-type: none !important;\n"
    "  padding-left: 0 !important;\n"
    "  margin-left: 0 !important;\n"
    "}\n"
    ".markdown-body li.task-list-item > ul.contains-task-list,\n"
    ".markdown-body li.task-list-item > ol.contains-task-list {\n"
    "  padding-left: 24px !important;\n"
    "  margin-left: 0 !important;\n"
    "}\n"
    ".markdown-body li.task-list-item {\n"
    "  list-style: none !important;\n"
    "  list-style-type: none !important;\n"
    "  padding-left: 24px !important;\n"
    "  text-indent: -24px !important;\n"
    "  margin-top: 5px;\n"
    "  margin-bottom: 5px;\n"
    "  line-height: 1.6;\n"
    "}\n"
    ".markdown-body li.task-list-item > input.task-list-item-checkbox {\n"
    "  margin: 0 6px 0 0;\n"
    "  vertical-align: middle;\n"
    "}\n"
    ".markdown-body .task-svg {\n"
    "  vertical-align: -2px;\n"
    "  margin-right: 6px;\n"
    "  display: inline-block;\n"
    "  flex-shrink: 0;\n"
    "}\n"
    "/* Bo cuc va can le anh Markdown / HTML */\n"
    ".img-align-center, .markdown-body .img-align-center {\n"
    "  text-align: center !important;\n"
    "  margin: 1.2rem 0 !important;\n"
    "  clear: both !important;\n"
    "}\n"
    ".img-align-center img, img.align-center, .markdown-body img.align-center {\n"
    "  display: inline-block !important;\n"
    "  margin: 0 auto !important;\n"
    "}\n"
    ".img-align-left, .markdown-body .img-align-left {\n"
    "  text-align: left !important;\n"
    "  margin: 1.2rem 0 !important;\n"
    "}\n"
    ".img-align-left img, img.align-left, .markdown-body img.align-left {\n"
    "  display: inline-block !important;\n"
    "}\n"
    ".img-align-right, .markdown-body .img-align-right {\n"
    "  text-align: right !important;\n"
    "  margin: 1.2rem 0 !important;\n"
    "}\n"
    ".img-align-right img, img.align-right, .markdown-body img.align-right {\n"
    "  display: inline-block !important;\n"
    "}\n"
    ".markdown-body img, img {\n"
    "  max-width: 100%;\n"
    "  box-sizing: border-box;\n"
    "  background-color: transparent !important;\n"
    "  background: transparent !important;\n"
    "}\n"
    "/* Phan cap tieu de H1, H2, H3, H4 chuan dep, dong nhat Markdown va HTML */\n"
    ".markdown-body h1, .markdown-body .report h1 {\n"
    "  font-size: 2.1rem !important;\n"
    "  font-weight: 700 !important;\n"
    "  margin: 0.6rem 0 1rem !important;\n"
    "  line-height: 1.3 !important;\n"
    "  letter-spacing: -0.02em !important;\n"
    "}\n"
    ".markdown-body h2, .markdown-body .report h2 {\n"
    "  font-size: 1.45rem !important;\n"
    "  font-weight: 600 !important;\n"
    "  border-bottom: 2px solid var(--line, var(--border-muted, #d8dee4)) !important;\n"
    "  padding-bottom: 0.4rem !important;\n"
    "  margin-top: 2rem !important;\n"
    "  margin-bottom: 0.8rem !important;\n"
    "  line-height: 1.35 !important;\n"
    "  letter-spacing: -0.01em !important;\n"
    "}\n"
    ".markdown-body h3, .markdown-body .report h3 {\n"
    "  font-size: 1.15rem !important;\n"
    "  font-weight: 600 !important;\n"
    "  margin-top: 1.4rem !important;\n"
    "  margin-bottom: 0.6rem !important;\n"
    "  line-height: 1.4 !important;\n"
    "}\n"
    ".markdown-body h4, .markdown-body .report h4 {\n"
    "  font-size: 1.02rem !important;\n"
    "  font-weight: 600 !important;\n"
    "  margin-top: 1.1rem !important;\n"
    "  margin-bottom: 0.4rem !important;\n"
    "}\n"
    "/* Ep bang luon fit 100% chieu rong va tu dong wrap noi dung thong minh */\n"
    ".markdown-body table {\n"
    "  display: table !important;\n"
    "  width: 100% !important;\n"
    "  max-width: 100% !important;\n"
    "  table-layout: auto !important;\n"
    "  border-collapse: collapse !important;\n"
    "  margin: 1.2em 0 !important;\n"
    "  page-break-inside: auto;\n"
    "}\n"
    ".markdown-body table thead {\n"
    "  display: table-header-group !important;\n"
    "}\n"
    ".markdown-body table tr {\n"
    "  page-break-inside: avoid !important;\n"
    "  break-inside: avoid !important;\n"
    "}\n"
    ".markdown-body table th,\n"
    ".markdown-body table td {\n"
    "  word-break: normal !important;\n"
    "  overflow-wrap: anywhere !important;\n"
    "  word-wrap: break-word !important;\n"
    "  white-space: normal !important;\n"
    "  hyphens: auto;\n"
    "}\n"
    ".markdown-body table code {\n"
    "  white-space: pre-wrap !important;\n"
    "  word-break: normal !important;\n"
    "  overflow-wrap: anywhere !important;\n"
    "}\n"
    "/* Ep code block va inline code tu dong xuong dong */\n"
    ".markdown-body pre,\n"
    ".markdown-body pre code {\n"
    "  white-space: pre-wrap !important;\n"
    "  word-break: break-word !important;\n"
    "  overflow-wrap: break-word !important;\n"
    "}\n"
    "/* Bo goc va can le cho Table of Contents (TOC) */\n"
    ".markdown-body .toc {\n"
    "  box-decoration-break: clone !important;\n"
    "  -webkit-box-decoration-break: clone !important;\n"
    "}\n"
    "/* Tieu de Table of Contents (TOC Title) */\n"
    ".markdown-body .toc .toc-title,\n"
    ".markdown-body .toc > strong:first-child {\n"
    "  display: block !important;\n"
    "  font-size: 1.35rem !important;\n"
    "  font-weight: 900 !important;\n"
    "  margin-top: 2px !important;\n"
    "  margin-bottom: 12px !important;\n"
    "  letter-spacing: -0.01em;\n"
    "  color: var(--fg-default, #1f2328);\n"
    "}\n"
    ".markdown-body .toc .toc-title.toc-align-left {\n"
    "  text-align: left !important;\n"
    "}\n"
    ".markdown-body .toc .toc-title.toc-align-center {\n"
    "  text-align: center !important;\n"
    "}\n"
    ".markdown-body .toc .toc-title.toc-align-right {\n"
    "  text-align: right !important;\n"
    "}\n"
    "/* Phan cap phong chu ro rang cho Table of Contents (TOC) */\n"
    "/* Cap 1: In dam, chu thang, ro net, mac dinh mau den */\n"
    ".markdown-body .toc li.toc-depth-1 > a,\n"
    ".markdown-body .toc > ul > li > a {\n"
    "  font-weight: 700 !important;\n"
    "  font-style: normal !important;\n"
    "  font-size: 0.98rem !important;\n"
    "  color: var(--fg-default, #1f2328) !important;\n"
    "}\n"
    "/* Cap 2: Dam nghieng, mac dinh mau den (1.2 ...) */\n"
    ".markdown-body .toc li.toc-depth-2 > a,\n"
    ".markdown-body .toc > ul > li > ul > li > a {\n"
    "  font-weight: 600 !important;\n"
    "  font-style: italic !important;\n"
    "  font-size: 0.94rem !important;\n"
    "  color: var(--fg-default, #1f2328) !important;\n"
    "}\n"
    "/* Cap 3: Nghieng binh thuong, mac dinh mau den (1.1.2 ...) */\n"
    ".markdown-body .toc li.toc-depth-3 > a,\n"
    ".markdown-body .toc > ul > li > ul > li > ul > li > a {\n"
    "  font-weight: 400 !important;\n"
    "  font-style: italic !important;\n"
    "  font-size: 0.90rem !important;\n"
    "  color: var(--fg-default, #1f2328) !important;\n"
    "}\n"
    "/* Cap 4+: Binh thuong, thang */\n"
    ".markdown-body .toc li.toc-depth-4 > a,\n"
    ".markdown-body .toc ul ul ul ul li a {\n"
    "  font-weight: 400 !important;\n"
    "  font-style: normal !important;\n"
    "  font-size: 0.88rem !important;\n"
    "  color: var(--fg-muted, #656d76) !important;\n"
    "}\n"
    ".markdown-body .toc a::after {\n"
    "  font-style: normal !important;\n"
    "  font-weight: 400 !important;\n"
    "}\n"
    "/* Tuy chon no-bullet cho TOC */\n"
    ".markdown-body .toc.no-bullet ul,\n"
    ".markdown-body .toc.no-bullet ol {\n"
    "  list-style: none !important;\n"
    "  list-style-type: none !important;\n"
    "  padding-left: 0 !important;\n"
    "  margin-left: 0 !important;\n"
    "}\n"
    ".markdown-body .toc.no-bullet li {\n"
    "  list-style: none !important;\n"
    "  list-style-type: none !important;\n"
    "  padding-left: 0 !important;\n"
    "  margin-left: 0 !important;\n"
    "}\n"
    ".markdown-body .toc.no-bullet ul ul {\n"
    "  padding-left: 18px !important;\n"
    "  margin-left: 0 !important;\n"
    "}\n"
    "/* Bo cuc Donut Chart Widget can giua, khong vien/nen */\n"
    ".donut-widget {\n"
    "  width: 100% !important;\n"
    "  margin: 1.8rem 0 !important;\n"
    "  text-align: center !important;\n"
    "  background: transparent !important;\n"
    "  border: none !important;\n"
    "  box-shadow: none !important;\n"
    "  padding: 0 !important;\n"
    "}\n"
    ".donut-widget-inner {\n"
    "  display: inline-flex !important;\n"
    "  align-items: center !important;\n"
    "  justify-content: center !important;\n"
    "  gap: 28px !important;\n"
    "  margin: 0 auto !important;\n"
    "  text-align: left !important;\n"
    "  background: transparent !important;\n"
    "  border: none !important;\n"
    "  box-shadow: none !important;\n"
    "  padding: 0 !important;\n"
    "}\n"
    ".metrics-dashboard-bar .donut-chart,\n"
    ".donut-widget .donut-chart,\n"
    ".donut-chart {\n"
    "  position: relative !important;\n"
    "  width: 110px !important;\n"
    "  height: 110px !important;\n"
    "  display: block !important;\n"
    "  flex-shrink: 0 !important;\n"
    "  margin: 0 !important;\n"
    "  background: transparent !important;\n"
    "  border: none !important;\n"
    "}\n"
    ".donut-chart .donut-svg-ring {\n"
    "  width: 110px !important;\n"
    "  height: 110px !important;\n"
    "  position: absolute !important;\n"
    "  top: 0 !important;\n"
    "  left: 0 !important;\n"
    "  transform: rotate(-90deg) !important;\n"
    "  border-radius: 50% !important;\n"
    "}\n"
    ".metrics-dashboard-bar .donut-chart .donut-center,\n"
    ".donut-widget .donut-center,\n"
    ".donut-center {\n"
    "  position: absolute !important;\n"
    "  top: 19px !important;\n"
    "  left: 19px !important;\n"
    "  width: 72px !important;\n"
    "  height: 72px !important;\n"
    "  background: #ffffff !important;\n"
    "  border-radius: 50% !important;\n"
    "  display: flex !important;\n"
    "  flex-direction: column !important;\n"
    "  align-items: center !important;\n"
    "  justify-content: center !important;\n"
    "  box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;\n"
    "  z-index: 2 !important;\n"
    "}\n"
    ".donut-center b {\n"
    "  font-size: 1.6rem !important;\n"
    "  font-weight: 800 !important;\n"
    "  line-height: 1 !important;\n"
    "  color: #1e293b !important;\n"
    "}\n"
    ".donut-center span {\n"
    "  font-size: 0.72rem !important;\n"
    "  font-weight: 700 !important;\n"
    "  text-transform: uppercase !important;\n"
    "  letter-spacing: 0.05em !important;\n"
    "  color: #64748b !important;\n"
    "  margin-top: 2px !important;\n"
    "}\n"
    ".donut-legend {\n"
    "  display: flex !important;\n"
    "  flex-direction: column !important;\n"
    "  justify-content: center !important;\n"
    "  gap: 6px !important;\n"
    "  text-align: left !important;\n"
    "}\n"
    ".donut-legend .legend-item {\n"
    "  display: flex !important;\n"
    "  align-items: center !important;\n"
    "  gap: 8px !important;\n"
    "  font-size: 0.95rem !important;\n"
    "  color: #334155 !important;\n"
    "  line-height: 1.4 !important;\n"
    "}\n"
    ".donut-legend .legend-item b {\n"
    "  font-weight: 700 !important;\n"
    "  color: #0f172a !important;\n"
    "}\n"
    ".donut-legend .legend-item .dot {\n"
    "  width: 10px !important;\n"
    "  height: 10px !important;\n"
    "  border-radius: 50% !important;\n"
    "  display: inline-block !important;\n"
    "  flex-shrink: 0 !important;\n"
    "}\n"
    "/* Ho tro tuong thich cho Metrics Dashboard va KPI Widgets khi in/xuat PDF */\n"
    "@media print {\n"
    "  .donut-widget {\n"
    "    display: block !important;\n"
    "    text-align: center !important;\n"
    "    margin: 1.6rem 0 !important;\n"
    "    page-break-inside: avoid !important;\n"
    "    break-inside: avoid !important;\n"
    "    background: transparent !important;\n"
    "    border: none !important;\n"
    "  }\n"
    "  .donut-widget-inner {\n"
    "    display: inline-block !important;\n"
    "    vertical-align: middle !important;\n"
    "    text-align: left !important;\n"
    "    margin: 0 auto !important;\n"
    "    background: transparent !important;\n"
    "    border: none !important;\n"
    "  }\n"
    "  .metrics-dashboard-bar {\n"
    "    display: block !important;\n"
    "    width: 100% !important;\n"
    "    box-sizing: border-box !important;\n"
    "    clear: both !important;\n"
    "    overflow: hidden !important;\n"
    "    margin: 1.2rem 0 1.5rem !important;\n"
    "    page-break-inside: avoid !important;\n"
    "    break-inside: avoid !important;\n"
    "  }\n"
    "  .metrics-dashboard-bar::after {\n"
    "    content: '' !important;\n"
    "    display: table !important;\n"
    "    clear: both !important;\n"
    "  }\n"
    "  .metrics-dashboard-bar .donut-group {\n"
    "    float: left !important;\n"
    "    width: 44% !important;\n"
    "    box-sizing: border-box !important;\n"
    "    display: block !important;\n"
    "  }\n"
    "  .metrics-dashboard-bar .donut-chart,\n"
    "  .donut-widget .donut-chart,\n"
    "  .donut-chart {\n"
    "    position: relative !important;\n"
    "    width: 110px !important;\n"
    "    height: 110px !important;\n"
    "    display: block !important;\n"
    "    float: left !important;\n"
    "    margin-right: 24px !important;\n"
    "    background: transparent !important;\n"
    "    border: none !important;\n"
    "  }\n"
    "  .metrics-dashboard-bar .donut-chart .donut-center,\n"
    "  .donut-widget .donut-center,\n"
    "  .donut-center {\n"
    "    position: absolute !important;\n"
    "    top: 19px !important;\n"
    "    left: 19px !important;\n"
    "    width: 72px !important;\n"
    "    height: 72px !important;\n"
    "    background: #ffffff !important;\n"
    "    border-radius: 50% !important;\n"
    "    text-align: center !important;\n"
    "    z-index: 2 !important;\n"
    "  }\n"
    "  .donut-center b {\n"
    "    font-size: 16pt !important;\n"
    "    display: block !important;\n"
    "    padding-top: 14px !important;\n"
    "  }\n"
    "  .donut-center span {\n"
    "    font-size: 7.5pt !important;\n"
    "    display: block !important;\n"
    "  }\n"
    "  .metrics-dashboard-bar .donut-legend,\n"
    "  .donut-widget .donut-legend,\n"
    "  .donut-legend {\n"
    "    float: left !important;\n"
    "    display: block !important;\n"
    "    width: auto !important;\n"
    "    padding-top: 8px !important;\n"
    "  }\n"
    "  .metrics-dashboard-bar .legend-item,\n"
    "  .donut-widget .legend-item,\n"
    "  .legend-item {\n"
    "    display: block !important;\n"
    "    margin-bottom: 4px !important;\n"
    "    font-size: 9.5pt !important;\n"
    "  }\n"
    "  .metrics-dashboard-bar .v-divider {\n"
    "    float: left !important;\n"
    "    width: 1% !important;\n"
    "    margin: 0 1% !important;\n"
    "    display: block !important;\n"
    "  }\n"
    "  .metrics-dashboard-bar .retest-strip {\n"
    "    float: right !important;\n"
    "    width: 53% !important;\n"
    "    display: block !important;\n"
    "    box-sizing: border-box !important;\n"
    "  }\n"
    "  .metrics-dashboard-bar .strip-header {\n"
    "    display: block !important;\n"
    "    margin-bottom: 6px !important;\n"
    "    clear: both !important;\n"
    "    overflow: hidden !important;\n"
    "  }\n"
    "  .metrics-dashboard-bar .strip-title {\n"
    "    float: left !important;\n"
    "  }\n"
    "  .metrics-dashboard-bar .sev-badge {\n"
    "    float: right !important;\n"
    "  }\n"
    "  .metrics-dashboard-bar .strip-kpis {\n"
    "    display: table !important;\n"
    "    width: 100% !important;\n"
    "    table-layout: fixed !important;\n"
    "    box-sizing: border-box !important;\n"
    "  }\n"
    "  .metrics-dashboard-bar .mini-kpi {\n"
    "    display: table-cell !important;\n"
    "    width: 33.33% !important;\n"
    "    vertical-align: middle !important;\n"
    "    text-align: center !important;\n"
    "    padding: 6px 4px !important;\n"
    "    margin: 0 2px !important;\n"
    "  }\n"
    "}\n"
)
TASKLIST_BASE_CSS = DOCUMENT_BASE_CSS

def _extract_theme_page_colors(css: str) -> tuple[str | None, str]:
    """Trich xuat mau nen (--canvas) va mau chu mo (--fg-muted) tu CSS cua theme."""
    bg_color = None
    muted_color = "#59636e"
    if css:
        m_bg = re.search(r"--canvas\s*:\s*([^;\n}]+);", css)
        if m_bg:
            val = m_bg.group(1).strip()
            if val and not val.lower().startswith("var("):
                bg_color = val
        if not bg_color:
            m_body = re.search(
                r"body\s*\{[^}]*background(?:-color)?\s*:\s*([^;\n}]+);",
                css,
                re.IGNORECASE | re.DOTALL,
            )
            if m_body:
                val = m_body.group(1).strip()
                if val and not val.lower().startswith("var("):
                    bg_color = val
        m_muted = re.search(r"--fg-muted\s*:\s*([^;\n}]+);", css)
        if m_muted:
            val = m_muted.group(1).strip()
            if val and not val.lower().startswith("var("):
                muted_color = val
    return bg_color, muted_color


def build_pdf_page_rule(
    css: str = "",
    html_body: str = "",
    directives: list[PrintDirectiveConfig] | None = None,
) -> str:
    """Tao quy tac @page A4 dong bo mau nen khap kho giay, kem theo chi thi in an neu co."""
    bg_color, muted_color = _extract_theme_page_colors(css)
    bg_line = f"  background-color: {bg_color};\n" if bg_color else ""
    base_rule = (
        "\n"
        "@page {\n"
        "  size: A4;\n"
        "  margin: 18mm 16mm 22mm 16mm;\n"
        f"{bg_line}"
        "  @bottom-center {\n"
        "    content: counter(page) \" / \" counter(pages);\n"
        "    font-size: 9pt;\n"
        f"    color: {muted_color};\n"
        "  }\n"
        "}\n"
    )

    # Đảm bảo khi in PDF, html, body và markdown-body luôn trong suốt để background của @page hiển thị toàn diện
    print_transparent_rule = (
        "\n"
        "@media print {\n"
        "  html, body, .markdown-body, .report {\n"
        "    background: transparent !important;\n"
        "    background-color: transparent !important;\n"
        "  }\n"
        "}\n"
    )

    # Auto-detect cover page: neu co .cover-page hoac comment COVER PAGE hoac class .cover trong HTML
    cover_rule = ""
    is_cover_detected = bool(
        html_body
        and (
            re.search(r'class=["\'][^"\']*\b(?:cover-page|cover)\b', html_body, re.IGNORECASE)
            or re.search(r'<!--\s*={3,}\s*COVER PAGE\s*={3,}', html_body, re.IGNORECASE)
        )
    )

    if is_cover_detected:
        cover_rule = (
            "\n"
            "/* Cover page: full-bleed, no margin, no page number */\n"
            "@page :first {\n"
            "  margin: 0 !important;\n"
            "  @bottom-center { content: none !important; }\n"
            "  @bottom-left   { content: none !important; }\n"
            "  @bottom-right  { content: none !important; }\n"
            "  @top-center    { content: none !important; }\n"
            "  @top-left      { content: none !important; }\n"
            "  @top-right     { content: none !important; }\n"
            "}\n"
            ".cover-page {\n"
            "  width: 210mm;\n"
            "  min-height: 297mm;\n"
            "  margin: 0 !important;\n"
            "  padding: 0 !important;\n"
            "  box-sizing: border-box !important;\n"
            "  page-break-after: always !important;\n"
            "  break-after: page !important;\n"
            "}\n"
        )

    if directives is not None:
        all_directives = list(directives)
    elif html_body:
        all_directives = parse_print_directives(html_body)
    else:
        all_directives = []

    if all_directives:
        custom_page_css = generate_page_css(all_directives)
        return base_rule + print_transparent_rule + cover_rule + custom_page_css

    return base_rule + print_transparent_rule + cover_rule


PDF_PAGE_RULE = build_pdf_page_rule("")

TOC_PRINT_RULE = (
    "\n"
    "@media print {\n"
    "  .markdown-body .toc {\n"
    "    box-decoration-break: clone !important;\n"
    "    -webkit-box-decoration-break: clone !important;\n"
    "  }\n"
    "  .markdown-body .toc a {\n"
    "    color: var(--fg-default, #1f2328) !important;\n"
    "    text-decoration: none;\n"
    "  }\n"
    "  .markdown-body .toc .toc-title,\n"
    "  .markdown-body .toc > strong:first-child {\n"
    "    display: block !important;\n"
    "    font-size: 14pt !important;\n"
    "    font-weight: 900 !important;\n"
    "    margin-top: 2pt !important;\n"
    "    margin-bottom: 9pt !important;\n"
    "    color: var(--fg-default, #1f2328);\n"
    "  }\n"
    "  .markdown-body .toc .toc-title.toc-align-left {\n"
    "    text-align: left !important;\n"
    "  }\n"
    "  .markdown-body .toc .toc-title.toc-align-center {\n"
    "    text-align: center !important;\n"
    "  }\n"
    "  .markdown-body .toc .toc-title.toc-align-right {\n"
    "    text-align: right !important;\n"
    "  }\n"
    "  /* Cap 1: In dam, chu thang, mau den */\n"
    "  .markdown-body .toc li.toc-depth-1 > a,\n"
    "  .markdown-body .toc > ul > li > a {\n"
    "    font-weight: 700 !important;\n"
    "    font-style: normal !important;\n"
    "    font-size: 10.5pt !important;\n"
    "    color: var(--fg-default, #1f2328) !important;\n"
    "  }\n"
    "  /* Cap 2: Dam nghieng, mau den (1.2 ...) */\n"
    "  .markdown-body .toc li.toc-depth-2 > a,\n"
    "  .markdown-body .toc > ul > li > ul > li > a {\n"
    "    font-weight: 600 !important;\n"
    "    font-style: italic !important;\n"
    "    font-size: 10pt !important;\n"
    "    color: var(--fg-default, #1f2328) !important;\n"
    "  }\n"
    "  /* Cap 3: Nghieng binh thuong, mau den (1.1.2 ...) */\n"
    "  .markdown-body .toc li.toc-depth-3 > a,\n"
    "  .markdown-body .toc > ul > li > ul > li > ul > li > a {\n"
    "    font-weight: 400 !important;\n"
    "    font-style: italic !important;\n"
    "    font-size: 9.5pt !important;\n"
    "    color: var(--fg-default, #1f2328) !important;\n"
    "  }\n"
    "  /* Cap 4+: Binh thuong, thang */\n"
    "  .markdown-body .toc li.toc-depth-4 > a,\n"
    "  .markdown-body .toc ul ul ul ul li a {\n"
    "    font-weight: 400 !important;\n"
    "    font-style: normal !important;\n"
    "    font-size: 9pt !important;\n"
    "    color: var(--fg-muted, #59636e) !important;\n"
    "  }\n"
    "  .markdown-body .toc a::after {\n"
    "    content: leader('. ') target-counter(attr(href), page);\n"
    "    color: var(--fg-muted, #59636e);\n"
    "    padding-left: 6px;\n"
    "    font-style: normal !important;\n"
    "    font-weight: 400 !important;\n"
    "  }\n"
    "  .markdown-body .toc.no-bullet ul,\n"
    "  .markdown-body .toc.no-bullet ol {\n"
    "    list-style: none !important;\n"
    "    list-style-type: none !important;\n"
    "    padding-left: 0 !important;\n"
    "    margin-left: 0 !important;\n"
    "  }\n"
    "  .markdown-body .toc.no-bullet li {\n"
    "    list-style: none !important;\n"
    "    list-style-type: none !important;\n"
    "    padding-left: 0 !important;\n"
    "    margin-left: 0 !important;\n"
    "  }\n"
    "  .markdown-body .toc.no-bullet ul ul {\n"
    "    padding-left: 18px !important;\n"
    "    margin-left: 0 !important;\n"
    "  }\n"
    "}\n"
)

HTML_HEADER = (
    "<!DOCTYPE html>\n"
    '<html lang="vi">\n'
    "<head>\n"
    '<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    "<title>%s</title>\n"
    "<style>\n"
)
HTML_FOOTER = (
    "\n</style>\n"
    "</head>\n"
    "<body>\n"
    '<main class="markdown-body">\n'
    "\n</main>\n"
    "</body>\n"
    "</html>\n"
)


def build_document(html_body: str, css: str, title: str = "MarkNote") -> str:
    """Ghep HTML da render voi CSS inline thanh mot trang doc lap."""
    directives = parse_print_directives(html_body)
    directive_css = generate_page_css(directives) if directives else ""
    full_css = (css or "") + "\n" + TASKLIST_BASE_CSS + ("\n" + directive_css if directive_css else "")
    enhanced_body = enhance_html_components(html_body)
    return (
        HTML_HEADER % title
        + full_css
        + HTML_FOOTER.replace("\n</main>\n", "\n" + enhanced_body + "\n</main>\n")
    )


def find_windows_weasyprint() -> Path | None:
    """Tim ban weasyprint.exe da dong goi san (kem Pango) tren Windows.

    Chay direct bang ban pre-built cua chinh noi WeasyPrint
    (release weasyprint-windows.zip) => KHONG can cai Pango qua pacman/MSYS2.
    """
    if sys.platform != "win32":
        return None
    candidates: list[Path] = []
    env_exe = os.environ.get("WEASYPRINT_EXE")
    if env_exe:
        candidates.append(Path(env_exe))
    root = Path(sys.executable).resolve().parent
    candidates.extend(
        [
            root / "bin" / "weasyprint" / "weasyprint.exe",
            root / "weasyprint" / "weasyprint.exe",
            root / "_internal" / "bin" / "weasyprint" / "weasyprint.exe",
            root / "_internal" / "weasyprint" / "weasyprint.exe",
        ]
    )
    # Project root khi chay source truc tiep
    project_root = Path(__file__).resolve().parent.parent
    candidates.extend(
        [
            project_root / "dist" / "marknote" / "bin" / "weasyprint" / "weasyprint.exe",
            project_root.parent / "dist" / "marknote" / "bin" / "weasyprint" / "weasyprint.exe",
            project_root.parent / "dist" / "apps" / "marknote" / "bin" / "weasyprint" / "weasyprint.exe",
            project_root / "build" / "weasyprint-windows" / "dist" / "weasyprint.exe",
            project_root / "build" / "weasyprint-windows" / "weasyprint.exe",
            project_root / "build" / "weasyprint-test" / "weasyprint.exe",
            Path.cwd() / "dist" / "marknote" / "bin" / "weasyprint" / "weasyprint.exe",
            Path.cwd() / "bin" / "weasyprint" / "weasyprint.exe",
            Path.cwd().parent / "dist" / "marknote" / "bin" / "weasyprint" / "weasyprint.exe",
        ]
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def render_pdf_via_cli(document: str, path: str) -> None:
    """Xuat PDF bang weasyprint.exe (gom san Pango) qua command line."""
    exe = find_windows_weasyprint()
    if exe is None:
        raise RuntimeError("weasyprint-libs")
    with tempfile.TemporaryDirectory() as tmp:
        html_file = Path(tmp) / "marknote-export.html"
        html_file.write_text(document, encoding="utf-8")
        run_kwargs = {
            "capture_output": True,
            "text": True,
        }
        if sys.platform == "win32":
            run_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        result = subprocess.run(
            [str(exe), str(html_file), str(path)],
            **run_kwargs,
        )
        if result.returncode != 0:
            raise RuntimeError("weasyprint-failed")


class Exporter:
    """Ghi ra file HTML hoac PDF dung chung mot theme (UC13)."""

    def toHtml(self, html_body: str, css: str, path) -> None:
        html_body = replace_checkboxes_with_svg(html_body)
        html_body = embed_images_as_base64(html_body)
        directives = parse_print_directives(html_body)
        page_rules = generate_page_css(directives) if directives else ""
        enhanced_body = enhance_html_components(html_body)
        Path(path).write_text(
            build_document(enhanced_body, css + ("\n" + page_rules if page_rules else "")),
            encoding="utf-8",
        )

    def toPdf(self, html_body: str, css: str, path) -> None:
        html_body = replace_checkboxes_with_svg(html_body)
        html_body = embed_images_as_base64(html_body)
        directives = parse_print_directives(html_body)
        page_rule = build_pdf_page_rule(css, html_body=html_body, directives=directives)
        enhanced_body = enhance_html_components(html_body)
        document = build_document(
            enhanced_body, css + page_rule + TOC_PRINT_RULE
        )
        cli_exe = find_windows_weasyprint()

        try:
            from weasyprint import HTML
            HTML(string=document).write_pdf(str(path))
            return
        except (ImportError, OSError, Exception) as exc:
            # Neu co ban weasyprint.exe dong goi san (kem Pango) tren Windows, uu tien fallback ngay
            if sys.platform == "win32" and cli_exe:
                render_pdf_via_cli(document, path)
                return

            msg = str(exc).lower()
            if isinstance(exc, ImportError) and "weasyprint" in msg:
                raise RuntimeError("weasyprint-missing") from exc
            if "cannot load library" in msg and any(
                lib in msg for lib in ("libgobject", "libpango", "gobject", "pango")
            ):
                raise RuntimeError("weasyprint-libs") from exc
            raise
