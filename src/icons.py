"""Bo icon Font Awesome chuan vector SVG cho MarkNote."""

from __future__ import annotations

import io
import os
import sys
from pathlib import Path
from PySide6.QtCore import QByteArray, QSize, Qt
from PySide6.QtGui import QColor, QGuiApplication, QIcon, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

_HEADLESS_APP = None


def _ensure_qapp():
    global _HEADLESS_APP
    if not QGuiApplication.instance():
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        _HEADLESS_APP = QGuiApplication([])


# Font Awesome 6 Free SVG Icons (Path data)
ICONS_SVG = {
    # App Logo (Modern document with bookmark and pen)
    "app": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">\n  <defs>\n    <!-- Vibrant Cyan-Blue-Indigo Gradient identical to user sample -->\n    <linearGradient id="bookmarkGrad" x1="0%" y1="0%" x2="0%" y2="100%">\n      <stop offset="0%" stop-color="#00d2ff"/>\n      <stop offset="35%" stop-color="#0ea5e9"/>\n      <stop offset="70%" stop-color="#3b82f6"/>\n      <stop offset="100%" stop-color="#6366f1"/>\n    </linearGradient>\n\n    <!-- Subtle Top Fold / Shading for Depth -->\n    <linearGradient id="topFold" x1="0%" y1="0%" x2="0%" y2="100%">\n      <stop offset="0%" stop-color="#0284c7" stop-opacity="0.3"/>\n      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>\n    </linearGradient>\n\n    <!-- Ambient Glow / Drop Shadow -->\n    <filter id="ribbonShadow" x="-20%" y="-10%" width="140%" height="130%">\n      <feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#0284c7" flood-opacity="0.4"/>\n      <feDropShadow dx="0" dy="24" stdDeviation="28" flood-color="#000000" flood-opacity="0.35"/>\n    </filter>\n\n    <!-- Inner Highlight -->\n    <linearGradient id="highlightEdge" x1="0%" y1="0%" x2="100%" y2="0%">\n      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.4"/>\n      <stop offset="8%" stop-color="#ffffff" stop-opacity="0.1"/>\n      <stop offset="92%" stop-color="#000000" stop-opacity="0"/>\n      <stop offset="100%" stop-color="#000000" stop-opacity="0.25"/>\n    </linearGradient>\n  </defs>\n\n  <!-- Bookmark Ribbon Body with V-Tail Notch -->\n  <g filter="url(#ribbonShadow)">\n    <!-- Main Ribbon Path -->\n    <path d="M128 32 C128 20, 138 12, 150 12 L362 12 C374 12, 384 20, 384 32 L384 456 C384 472, 365 481, 352 470 L256 392 L160 470 C147 481, 128 472, 128 456 Z" fill="url(#bookmarkGrad)"/>\n\n    <!-- Subtle Edge Bevel Highlight -->\n    <path d="M128 32 C128 20, 138 12, 150 12 L362 12 C374 12, 384 20, 384 32 L384 456 C384 472, 365 481, 352 470 L256 392 L160 470 C147 481, 128 472, 128 456 Z" fill="url(#highlightEdge)"/>\n\n    <!-- Top Shading Bar -->\n    <rect x="128" y="12" width="256" height="40" rx="4" fill="url(#topFold)"/>\n  </g>\n</svg>'
    ),
    # File New (fa-file-circle-plus)
    "file_new": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
        '<path fill="currentColor" d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM232 344V280H168c-13.3 0-24-10.7-24-24s10.7-24 24-24h64V168c0-13.3 10.7-24 24-24s24 10.7 24 24v64h64c13.3 0 24 10.7 24 24s-10.7 24-24 24H280v64c0-13.3-10.7 24-24 24s-24-10.7-24-24z"/>'
        '</svg>'
    ),
    # File Import (fa-file-import)
    "file_import": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
        '<path fill="currentColor" d="M64 464c-8.8 0-16-7.2-16-16V64c0-8.8 7.2-16 16-16H224v80c0 17.7 14.3 32 32 32h80V256h48V160c0-17-6.7-33.3-18.7-45.3L277.3 26.7C265.3 14.7 249 8 232 8H64C28.7 8 0 36.7 0 72V448c0 35.3 28.7 64 64 64H224V464H64zm359-199l-17 17c-9.4 9.4-9.4 24.6 0 33.9l47 47H256c-13.3 0-24 10.7-24 24s10.7 24 24 24h197l-47 47c-9.4 9.4-9.4 24.6 0 33.9l17 17c9.4 9.4 24.6 9.4 33.9 0l105-105c9.4-9.4 9.4-24.6 0-33.9L456.9 265c-9.4-9.4-24.6-9.4-33.9 0z"/>'
        '</svg>'
    ),
    # File Save (fa-floppy-disk)
    "file_save": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">'
        '<path fill="currentColor" d="M64 32C28.7 32 0 60.7 0 96V416c0 35.3 28.7 64 64 64H384c35.3 0 64-28.7 64-64V173.3c0-17-6.7-33.3-18.7-45.3L352 50.7C340 38.7 323.7 32 306.7 32H64zm0 64H288v96H64V96zM384 416H64V320H384v96z"/>'
        '</svg>'
    ),
    # Rename (fa-pen-to-square)
    "file_rename": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
        '<path fill="currentColor" d="M471.6 21.7c-21.9-21.9-57.3-21.9-79.2 0L362.3 51.7l97.9 97.9 30.1-30.1c21.9-21.9 21.9-57.3 0-79.2L471.6 21.7zm-299.2 220c-6.1 6.1-10.8 13.6-13.5 21.9l-29.6 88.8c-2.9 8.6-.6 18.1 5.8 24.6s15.9 8.7 24.6 5.8l88.8-29.6c8.2-2.7 15.7-7.4 21.9-13.5L437.7 172.3 339.7 74.3 172.4 241.7zM96 64C43 64 0 107 0 160V416c0 53 43 96 96 96H352c53 0 96-43 96-96V320c0-17.7-14.3-32-32-32s-32 14.3-32 32v96c0 17.7-14.3 32-32 32H96c-17.7 0-32-14.3-32-32V160c0-17.7 14.3-32 32-32h96c17.7 0 32-14.3 32-32s-14.3-32-32-32H96z"/>'
        '</svg>'
    ),
    # Delete (fa-trash-can)
    "file_delete": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">'
        '<path fill="currentColor" d="M135.2 17.7L128 32H32C14.3 32 0 46.3 0 64S14.3 96 32 96H416c17.7 0 32-14.3 32-32s-14.3-32-32-32H320l-7.2-14.3C307.4 6.8 296.3 0 284.2 0H163.8c-12.1 0-23.2 6.8-28.6 17.7zM416 128H32L53.2 467c1.6 25.3 22.6 45 47.9 45H346.9c25.3 0 46.3-19.7 47.9-45L416 128z"/>'
        '</svg>'
    ),
    # Export HTML (fa-file-code)
    "export_html": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512">'
        '<path fill="currentColor" d="M0 64C0 28.7 28.7 0 64 0H224V128c0 17.7 14.3 32 32 32H384V448c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V64zm150.6 241.4l-48 48c-6.2 6.2-6.2 16.4 0 22.6l48 48c6.2 6.2 16.4 6.2 22.6 0s6.2-16.4 0-22.6L134.6 368l38.6-38.6c6.2-6.2 6.2-16.4 0-22.6s-16.4-6.2-22.6 0zm82.8 0c-6.2-6.2-16.4-6.2-22.6 0s-6.2 16.4 0 22.6l38.6 38.6-38.6 38.6c-6.2 6.2-6.2 16.4 0 22.6s16.4 6.2 22.6 0l48-48c6.2-6.2 6.2-16.4 0-22.6l-48-48zM384 121.9V128H256V0h6.1c17 0 33.3 6.7 45.3 18.7l63.9 63.9c12 12 18.7 28.3 18.7 45.3z"/>'
        '</svg>'
    ),
    # Export PDF (fa-file-pdf)
    "export_pdf": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
        '<path fill="currentColor" d="M0 64C0 28.7 28.7 0 64 0H224V128c0 17.7 14.3 32 32 32H384V448c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V64zm384 64H256V0l128 128zM128 272c0-8.8-7.2-16-16-16s-16 7.2-16 16v96c0 8.8 7.2 16 16 16s16-7.2 16-16V352h32c26.5 0 48-21.5 48-48s-21.5-48-48-48H128v16zm32 48h-32V288h32c8.8 0 16 7.2 16 16s-7.2 16-16 16zm80-64c-8.8 0-16 7.2-16 16v96c0 8.8 7.2 16 16 16h48c26.5 0 48-21.5 48-48v-32c0-26.5-21.5-48-48-48H240zm32 96V288h16c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16h-16zm96-96c-8.8 0-16 7.2-16 16v96c0 8.8 7.2 16 16 16s16-7.2 16-16V336h32c8.8 0 16-7.2 16-16s-7.2-16-16-16h-32V288h48c8.8 0 16-7.2 16-16s-7.2-16-16-16H368z"/>'
        '</svg>'
    ),
    # Export Markdown (fa-file-lines)
    "export_md": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512">'
        '<path fill="currentColor" d="M64 0C28.7 0 0 28.7 0 64V448c0 35.3 28.7 64 64 64H320c35.3 0 64-28.7 64-64V160H256c-17.7 0-32-14.3-32-32V0H64zM256 0V128H384L256 0zM112 256H272c8.8 0 16 7.2 16 16s-7.2 16-16 16H112c-8.8 0-16-7.2-16-16s7.2-16 16-16zm0 64H272c8.8 0 16 7.2 16 16s-7.2 16-16 16H112c-8.8 0-16-7.2-16-16s7.2-16 16-16zm0 64H208c8.8 0 16 7.2 16 16s-7.2 16-16 16H112c-8.8 0-16-7.2-16-16s7.2-16 16-16z"/>'
        '</svg>'
    ),
    # Quit (fa-arrow-right-from-bracket)
    "app_quit": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
        '<path fill="currentColor" d="M377.9 105.9L500.7 228.7c15.6 15.6 15.6 40.9 0 56.6L377.9 408.1c-15.6 15.6-40.9 15.6-56.6 0s-15.6-40.9 0-56.6l53.7-53.7H160c-22.1 0-40-17.9-40-40s17.9-40 40-40h215l-53.7-53.7c-15.6-15.6-15.6-40.9 0-56.6s40.9-15.6 56.6 0zM160 96c17.7 0 32-14.3 32-32s-14.3-32-32-32H96C43 32 0 75 0 128V384c0 53 43 96 96 96h64c17.7 0 32-14.3 32-32s-14.3-32-32-32H96c-17.7 0-32-14.3-32-32V128c0-17.7 14.3-32 32-32h64z"/>'
        '</svg>'
    ),
    # Find / Search (fa-magnifying-glass)
    "search_find": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
        '<path fill="currentColor" d="M416 208c0 45.9-14.9 88.3-40 122.7L502.6 457.4c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L330.7 376c-34.4 25.2-76.8 40-122.7 40C93.1 416 0 322.9 0 208S93.1 0 208 0s208 93.1 208 208zM208 352a144 144 0 1 0 0-288 144 144 0 1 0 0 288z"/>'
        '</svg>'
    ),
    # Replace (fa-arrow-rotate-right)
    "search_replace": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
        '<path fill="currentColor" d="M142.9 96c-21.5 0-42.2 8.5-57.4 23.7L57.4 147.9c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L40.2 74.5C64.6 50.1 97.7 36.4 132.2 36.4H320c106 0 192 86 192 192s-86 192-192 192H142.9c-17.7 0-32-14.3-32-32s14.3-32 32-32H320c70.7 0 128-57.3 128-128s-57.3-128-128-128H142.9zM0 160V32c0-17.7 14.3-32 32-32s32 14.3 32 32V96H32c-17.7 0-32 14.3-32 32v32z"/>'
        '</svg>'
    ),
    # Insert Image (fa-image)
    "media_image": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
        '<path fill="currentColor" d="M448 80c8.8 0 16 7.2 16 16V416c0 8.8-7.2 16-16 16H64c-8.8 0-16-7.2-16-16V96c0-8.8 7.2-16 16-16H448zM64 32C28.7 32 0 60.7 0 96V416c0 35.3 28.7 64 64 64H448c35.3 0 64-28.7 64-64V96c0-35.3-28.7-64-64-64H64zm320 184a48 48 0 1 0 0-96 48 48 0 1 0 0 96zM152.5 192.2L64 304v80h384v-48l-107.5-120.2c-9.3-10.4-25.3-11.1-35.4-1.5L238.4 278.4l-50.5-64.7c-9.3-11.9-26.6-13.6-38-2.5z"/>'
        '</svg>'
    ),
    # Media Folder (fa-folder-open)
    "media_folder": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512">'
        '<path fill="currentColor" d="M88.7 223.8L0 375.8V96C0 60.7 28.7 32 64 32H181.5c17 0 33.3 6.7 45.3 18.7l26.5 26.5c12 12 28.3 18.7 45.3 18.7H448c35.3 0 64 28.7 64 64v32H147.2c-24.8 0-47.5 12.8-60.5 33.9zM147.2 192H528c26.5 0 48 21.5 48 48c0 5.6-1 11.2-3 16.5l-84.3 224.9c-8.9 23.7-31.5 39.4-56.8 39.4H80c-26.5 0-48-21.5-48-48c0-5.6 1-11.2 3-16.5l84.3-224.9c8.9-23.7 31.5-39.4 56.8-39.4h27.9z"/>'
        '</svg>'
    ),
    # Sync Scroll (fa-arrows-up-down)
    "view_sync": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 512">'
        '<path fill="currentColor" d="M145.1 8.5c-7.9-11.3-26.2-11.3-34.1 0l-96 137.1c-7.1 10.1-4.7 24.1 5.4 31.2s24.1 4.7 31.2-5.4L96 100.9V411.1L51.6 340.6c-7.1-10.1-21.1-12.5-31.2-5.4s-12.5 21.1-5.4 31.2l96 137.1c7.9 11.3 26.2 11.3 34.1 0l96-137.1c7.1-10.1 4.7-24.1-5.4-31.2s-24.1-4.7-31.2 5.4L160 411.1V100.9l44.4 70.5c7.1 10.1 21.1 12.5 31.2 5.4s12.5-21.1 5.4-31.2l-96-137.1z"/>'
        '</svg>'
    ),
    # Appearance / Theme (fa-palette)
    "settings_theme": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
        '<path fill="currentColor" d="M512 256c0 .9 0 1.8 0 2.7c-.4 36.5-33.6 61.3-70.1 61.3H344c-26.5 0-48 21.5-48 48v24c0 30.9-25.1 56-56 56c-2.8 0-5.7-.2-8.5-.7c-21.8-4.1-39.4-19.8-45.7-41.2C177.3 379.7 128 320 128 256C128 114.6 242.6 0 384 0c70.7 0 128 57.3 128 128v128zm-352-96a32 32 0 1 0 0-64 32 32 0 1 0 0 64zm64 64a32 32 0 1 0 -64 0 32 32 0 1 0 64 0zm96-64a32 32 0 1 0 0-64 32 32 0 1 0 0 64zm64 64a32 32 0 1 0 -64 0 32 32 0 1 0 64 0z"/>'
        '</svg>'
    ),
    # About (fa-circle-info)
    "help_about": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
        '<path fill="currentColor" d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM216 336h24V272H216c-13.3 0-24-10.7-24-24s10.7-24 24-24h48c13.3 0 24 10.7 24 24v88h8c13.3 0 24 10.7 24 24s-10.7 24-24 24H216c-13.3 0-24-10.7-24-24s10.7-24 24-24zm40-144a32 32 0 1 1 0-64 32 32 0 1 1 0 64z"/>'
        '</svg>'
    ),
    # Tag / Tags (fa-tags)
    "tag": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512">'
        '<path fill="currentColor" d="M497.9 142.1l-46.1 46.1c-3.1 3.1-8.2 3.1-11.3 0l-33.9-33.9c-3.1-3.1-3.1-8.2 0-11.3l46.1-46.1c3.1-3.1 8.2-3.1 11.3 0l33.9 33.9c3.1 3.1 3.1 8.2 0 11.3zM448 32H282.5c-17 0-33.3 6.7-45.3 18.7L26.7 261.3c-25 25-25 65.5 0 90.5l133.5 133.5c25 25 65.5 25 90.5 0L461.3 274.7c12-12 18.7-28.3 18.7-45.3V64c0-17.7-14.3-32-32-32zm-64 128a32 32 0 1 1 0-64 32 32 0 1 1 0 64z"/>'
        '</svg>'
    ),
    # Plus (fa-plus)
    "plus": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">'
        '<path fill="currentColor" d="M256 80c0-17.7-14.3-32-32-32s-32 14.3-32 32V224H48c-17.7 0-32 14.3-32 32s14.3 32 32 32H192V432c0 17.7 14.3 32 32 32s32-14.3 32-32V288H400c17.7 0 32-14.3 32-32s-14.3-32-32-32H256V80z"/>'
        '</svg>'
    ),
    # Print (fa-print)
    "print": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
        '<path fill="currentColor" d="M128 0C92.7 0 64 28.7 64 64v96h64V64H384v96h64V64c0-35.3-28.7-64-64-64H128zM384 448H128V320H384v128zm64-256H64c-35.3 0-64 28.7-64 64v144c0 26.5 21.5 48 48 48h16v-96c0-17.7 14.3-32 32-32H416c17.7 0 32 14.3 32 32v96h16c26.5 0 48-21.5 48-48V256c0-35.3-28.7-64-64-64zm-48 72a24 24 0 1 1 0-48 24 24 0 1 1 0 48z"/>'
        '</svg>'
    ),
}

ALIASES = {
    "new": "file_new",
    "import": "file_import",
    "save": "file_save",
    "rename": "file_rename",
    "delete": "file_delete",
    "remove": "file_delete",
    "html": "export_html",
    "pdf": "export_pdf",
    "md": "export_md",
    "markdown": "export_md",
    "quit": "app_quit",
    "exit": "app_quit",
    "close": "app_quit",
    "find": "search_find",
    "search": "search_find",
    "replace": "search_replace",
    "image": "media_image",
    "photo": "media_image",
    "folder": "media_folder",
    "media": "media_folder",
    "sync": "view_sync",
    "theme": "settings_theme",
    "settings": "settings_theme",
    "palette": "settings_theme",
    "about": "help_about",
    "help": "help_about",
    "info": "help_about",
    "tag": "tag",
    "tags": "tag",
    "marknote": "app",
    "logo": "app",
}
ICON_ALIASES = ALIASES

_ICON_CACHE: dict[str, QIcon] = {}


def get_icon(name: str, color: str | QColor = "#24292f") -> QIcon:
    """Tao QIcon sac net tu Font Awesome SVG voi mau tu chon."""
    _ensure_qapp()
    canonical = ALIASES.get(name, name)
    if isinstance(color, QColor):
        color = color.name()
    cache_key = f"{canonical}:{color}"
    if cache_key in _ICON_CACHE:
        return _ICON_CACHE[cache_key]

    svg_content = ICONS_SVG.get(canonical) or ICONS_SVG.get(name)
    if not svg_content:
        return QIcon()

    if canonical != "app" and color:
        # Thay the currentColor bang mau cu the
        svg_content = svg_content.replace('fill="currentColor"', f'fill="{color}"')

    renderer = QSvgRenderer(QByteArray(svg_content.encode("utf-8")))
    icon = QIcon()

    # Sinh nhieu do phan giai cho man hinh High DPI
    sizes = [16, 20, 24, 32, 48, 64] if canonical != "app" else [16, 32, 48, 64, 128, 256]
    for s in sizes:
        pix = QPixmap(s, s)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        renderer.render(painter)
        painter.end()
        icon.addPixmap(pix)

    _ICON_CACHE[cache_key] = icon
    return icon


def get_pixmap(name: str, size: int = 24, color: str | QColor = "#24292f") -> QPixmap:
    """Tao QPixmap sac net voi kich thuoc va mau tu chon."""
    _ensure_qapp()
    canonical = ICON_ALIASES.get(name, name)
    svg_content = ICONS_SVG.get(canonical)
    if not svg_content:
        return QPixmap(size, size)
    if canonical != "app" and color:
        color_hex = color.name() if isinstance(color, QColor) else str(color)
        svg_content = svg_content.replace('fill="currentColor"', f'fill="{color_hex}"')
    renderer = QSvgRenderer(QByteArray(svg_content.encode("utf-8")))
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    renderer.render(painter)
    painter.end()
    return pix


def export_app_icon_png(dest_path: Path | str, size: int = 256) -> None:
    """Luu logo app ra file PNG chat luong cao."""
    _ensure_qapp()
    svg_content = ICONS_SVG["app"]
    renderer = QSvgRenderer(QByteArray(svg_content.encode("utf-8")))
    img = QImage(size, size, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    renderer.render(painter)
    painter.end()
    dest = Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(dest))


if __name__ == "__main__":
    assets_dir = Path(__file__).resolve().parent.parent / "assets"
    export_app_icon_png(assets_dir / "marknote.png")
    print(f"Exported {assets_dir / 'marknote.png'}")
