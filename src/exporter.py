"""Xuat HTML va PDF voi CSS cua theme da chon, nhung inline."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

from media import embed_images_as_base64

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


def enhance_html_components(html: str) -> str:
    """Thay the checkbox bang SVG, ho tro donut directive va bo sung vector cho donut chart neu thieu."""
    if not html:
        return html
    html = replace_checkboxes_with_svg(html)
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
    "  font-size: 1.25rem !important;\n"
    "  font-weight: 700 !important;\n"
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
    "/* Cap 1: In dam, chu thang, ro net */\n"
    ".markdown-body .toc li.toc-depth-1 > a,\n"
    ".markdown-body .toc > ul > li > a {\n"
    "  font-weight: 700 !important;\n"
    "  font-style: normal !important;\n"
    "  font-size: 0.98rem !important;\n"
    "  color: var(--fg-default, #1f2328) !important;\n"
    "}\n"
    "/* Cap 2: Dam nghieng (1.2 ...) */\n"
    ".markdown-body .toc li.toc-depth-2 > a,\n"
    ".markdown-body .toc > ul > li > ul > li > a {\n"
    "  font-weight: 600 !important;\n"
    "  font-style: italic !important;\n"
    "  font-size: 0.94rem !important;\n"
    "}\n"
    "/* Cap 3: Nghieng binh thuong (1.1.2 ...) */\n"
    ".markdown-body .toc li.toc-depth-3 > a,\n"
    ".markdown-body .toc > ul > li > ul > li > ul > li > a {\n"
    "  font-weight: 400 !important;\n"
    "  font-style: italic !important;\n"
    "  font-size: 0.90rem !important;\n"
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

PDF_PAGE_RULE = (
    "\n"
    "@page {\n"
    "  size: A4;\n"
    "  margin: 18mm 16mm 22mm 16mm;\n"
    "  @bottom-center {\n"
    "    content: counter(page) \" / \" counter(pages);\n"
    "    font-size: 9pt;\n"
    "    color: #59636e;\n"
    "  }\n"
    "}\n"
)

TOC_PRINT_RULE = (
    "\n"
    "@media print {\n"
    "  .markdown-body .toc {\n"
    "    box-decoration-break: clone !important;\n"
    "    -webkit-box-decoration-break: clone !important;\n"
    "  }\n"
    "  .markdown-body .toc a {\n"
    "    color: var(--fg-default, #1f2328);\n"
    "    text-decoration: none;\n"
    "  }\n"
    "  .markdown-body .toc .toc-title,\n"
    "  .markdown-body .toc > strong:first-child {\n"
    "    display: block !important;\n"
    "    font-size: 13.5pt !important;\n"
    "    font-weight: 700 !important;\n"
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
    "  /* Cap 1: In dam, chu thang */\n"
    "  .markdown-body .toc li.toc-depth-1 > a,\n"
    "  .markdown-body .toc > ul > li > a {\n"
    "    font-weight: 700 !important;\n"
    "    font-style: normal !important;\n"
    "    font-size: 10.5pt !important;\n"
    "  }\n"
    "  /* Cap 2: Dam nghieng (1.2 ...) */\n"
    "  .markdown-body .toc li.toc-depth-2 > a,\n"
    "  .markdown-body .toc > ul > li > ul > li > a {\n"
    "    font-weight: 600 !important;\n"
    "    font-style: italic !important;\n"
    "    font-size: 10pt !important;\n"
    "  }\n"
    "  /* Cap 3: Nghieng binh thuong (1.1.2 ...) */\n"
    "  .markdown-body .toc li.toc-depth-3 > a,\n"
    "  .markdown-body .toc > ul > li > ul > li > ul > li > a {\n"
    "    font-weight: 400 !important;\n"
    "    font-style: italic !important;\n"
    "    font-size: 9.5pt !important;\n"
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
    full_css = (css or "") + "\n" + TASKLIST_BASE_CSS
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
            project_root / "build" / "weasyprint-windows" / "weasyprint.exe",
            project_root / "build" / "weasyprint-test" / "weasyprint.exe",
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
        Path(path).write_text(
            build_document(html_body, css), encoding="utf-8"
        )

    def toPdf(self, html_body: str, css: str, path) -> None:
        html_body = replace_checkboxes_with_svg(html_body)
        html_body = embed_images_as_base64(html_body)
        document = build_document(
            html_body, css + PDF_PAGE_RULE + TOC_PRINT_RULE
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
