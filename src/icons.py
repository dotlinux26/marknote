"""Bo icon Font Awesome 6 Free chuan vector SVG cho MarkNote."""

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


# Font Awesome 6 Free Official SVG Icons (Vector standard)
ICONS_SVG = {
    # App Logo (Bookmark Ribbon Cyan-Blue Gradient)
    "app": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">\n  <defs>\n    <!-- Vibrant Cyan-Blue-Indigo Gradient identical to user sample -->\n    <linearGradient id="bookmarkGrad" x1="0%" y1="0%" x2="0%" y2="100%">\n      <stop offset="0%" stop-color="#00d2ff"/>\n      <stop offset="35%" stop-color="#0ea5e9"/>\n      <stop offset="70%" stop-color="#3b82f6"/>\n      <stop offset="100%" stop-color="#6366f1"/>\n    </linearGradient>\n\n    <!-- Subtle Top Fold / Shading for Depth -->\n    <linearGradient id="topFold" x1="0%" y1="0%" x2="0%" y2="100%">\n      <stop offset="0%" stop-color="#0284c7" stop-opacity="0.3"/>\n      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>\n    </linearGradient>\n\n    <!-- Ambient Glow / Drop Shadow -->\n    <filter id="ribbonShadow" x="-20%" y="-10%" width="140%" height="130%">\n      <feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#0284c7" flood-opacity="0.4"/>\n      <feDropShadow dx="0" dy="24" stdDeviation="28" flood-color="#000000" flood-opacity="0.35"/>\n    </filter>\n\n    <!-- Inner Highlight -->\n    <linearGradient id="highlightEdge" x1="0%" y1="0%" x2="100%" y2="0%">\n      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.4"/>\n      <stop offset="8%" stop-color="#ffffff" stop-opacity="0.1"/>\n      <stop offset="92%" stop-color="#000000" stop-opacity="0"/>\n      <stop offset="100%" stop-color="#000000" stop-opacity="0.25"/>\n    </linearGradient>\n  </defs>\n\n  <!-- Bookmark Ribbon Body with V-Tail Notch -->\n  <g filter="url(#ribbonShadow)">\n    <!-- Main Ribbon Path -->\n    <path d="M128 32 C128 20, 138 12, 150 12 L362 12 C374 12, 384 20, 384 32 L384 456 C384 472, 365 481, 352 470 L256 392 L160 470 C147 481, 128 472, 128 456 Z" fill="url(#bookmarkGrad)"/>\n\n    <!-- Subtle Edge Bevel Highlight -->\n    <path d="M128 32 C128 20, 138 12, 150 12 L362 12 C374 12, 384 20, 384 32 L384 456 C384 472, 365 481, 352 470 L256 392 L160 470 C147 481, 128 472, 128 456 Z" fill="url(#highlightEdge)"/>\n\n    <!-- Top Shading Bar -->\n    <rect x="128" y="12" width="256" height="40" rx="4" fill="url(#topFold)"/>\n  </g>\n</svg>'
    ),
    # File New (fa-file-circle-plus - Font Awesome 6 Free Solid)
    "file_new": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><path fill="currentColor" d="M0 64C0 28.7 28.7 0 64 0L224 0l0 128c0 17.7 14.3 32 32 32l128 0 0 38.6C310.1 219.5 256 287.4 256 368c0 59.1 29.1 111.3 73.7 143.3c-3.2 .5-6.4 .7-9.7 .7L64 512c-35.3 0-64-28.7-64-64L0 64zm384 64l-128 0L256 0 384 128zm48 96a144 144 0 1 1 0 288 144 144 0 1 1 0-288zm16 80c0-8.8-7.2-16-16-16s-16 7.2-16 16l0 48-48 0c-8.8 0-16 7.2-16 16s7.2 16 16 16l48 0 0 48c0 8.8 7.2 16 16 16s16-7.2 16-16l0-48 48 0c8.8 0 16-7.2 16-16s-7.2-16-16-16l-48 0 0-48z"/></svg>'
    ),
    # File Import (fa-file-import - Font Awesome 6 Free Solid)
    "file_import": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="currentColor" d="M128 64c0-35.3 28.7-64 64-64L352 0l0 128c0 17.7 14.3 32 32 32l128 0 0 288c0 35.3-28.7 64-64 64l-256 0c-35.3 0-64-28.7-64-64l0-112 174.1 0-39 39c-9.4 9.4-9.4 24.6 0 33.9s24.6 9.4 33.9 0l80-80c9.4-9.4 9.4-24.6 0-33.9l-80-80c-9.4-9.4-24.6-9.4-33.9 0s-9.4 24.6 0 33.9l39 39L128 288l0-224zm0 224l0 48L24 336c-13.3 0-24-10.7-24-24s10.7-24 24-24l104 0zM512 128l-128 0L384 0 512 128z"/></svg>'
    ),
    # File Save (fa-floppy-disk - Font Awesome 6 Free Solid)
    "file_save": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path fill="currentColor" d="M64 32C28.7 32 0 60.7 0 96L0 416c0 35.3 28.7 64 64 64l320 0c35.3 0 64-28.7 64-64l0-242.7c0-17-6.7-33.3-18.7-45.3L352 50.7C340 38.7 323.7 32 306.7 32L64 32zm0 96c0-17.7 14.3-32 32-32l192 0c17.7 0 32 14.3 32 32l0 64c0 17.7-14.3 32-32 32L96 224c-17.7 0-32-14.3-32-32l0-64zM224 288a64 64 0 1 1 0 128 64 64 0 1 1 0-128z"/></svg>'
    ),
    # Rename (fa-pen-to-square - Font Awesome 6 Free Solid)
    "file_rename": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="currentColor" d="M471.6 21.7c-21.9-21.9-57.3-21.9-79.2 0L362.3 51.7l97.9 97.9 30.1-30.1c21.9-21.9 21.9-57.3 0-79.2L471.6 21.7zm-299.2 220c-6.1 6.1-10.8 13.6-13.5 21.9l-29.6 88.8c-2.9 8.6-.6 18.1 5.8 24.6s15.9 8.7 24.6 5.8l88.8-29.6c8.2-2.7 15.7-7.4 21.9-13.5L437.7 172.3 339.7 74.3 172.4 241.7zM96 64C43 64 0 107 0 160L0 416c0 53 43 96 96 96l256 0c53 0 96-43 96-96l0-96c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 96c0 17.7-14.3 32-32 32L96 448c-17.7 0-32-14.3-32-32l0-256c0-17.7 14.3-32 32-32l96 0c17.7 0 32-14.3 32-32s-14.3-32-32-32L96 64z"/></svg>'
    ),
    # Delete (fa-trash-can - Font Awesome 6 Free Solid)
    "file_delete": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path fill="currentColor" d="M135.2 17.7C140.6 6.8 151.7 0 163.8 0L284.2 0c12.1 0 23.2 6.8 28.6 17.7L320 32l96 0c17.7 0 32 14.3 32 32s-14.3 32-32 32L32 96C14.3 96 0 81.7 0 64S14.3 32 32 32l96 0 7.2-14.3zM32 128l384 0 0 320c0 35.3-28.7 64-64 64L96 512c-35.3 0-64-28.7-64-64l0-320zm96 64c-8.8 0-16 7.2-16 16l0 224c0 8.8 7.2 16 16 16s16-7.2 16-16l0-224c0-8.8-7.2-16-16-16zm96 0c-8.8 0-16 7.2-16 16l0 224c0 8.8 7.2 16 16 16s16-7.2 16-16l0-224c0-8.8-7.2-16-16-16zm96 0c-8.8 0-16 7.2-16 16l0 224c0 8.8 7.2 16 16 16s16-7.2 16-16l0-224c0-8.8-7.2-16-16-16z"/></svg>'
    ),
    # Export HTML (fa-file-code - Font Awesome 6 Free Solid)
    "export_html": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><path fill="currentColor" d="M64 0C28.7 0 0 28.7 0 64L0 448c0 35.3 28.7 64 64 64l256 0c35.3 0 64-28.7 64-64l0-288-128 0c-17.7 0-32-14.3-32-32L224 0 64 0zM256 0l0 128 128 0L256 0zM153 289l-31 31 31 31c9.4 9.4 9.4 24.6 0 33.9s-24.6 9.4-33.9 0L71 337c-9.4-9.4-9.4-24.6 0-33.9l48-48c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9zM265 255l48 48c9.4 9.4 9.4 24.6 0 33.9l-48 48c-9.4 9.4-24.6 9.4-33.9 0s-9.4-24.6 0-33.9l31-31-31-31c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0z"/></svg>'
    ),
    # Export PDF (fa-file-pdf - Font Awesome 6 Free Solid)
    "export_pdf": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="currentColor" d="M0 64C0 28.7 28.7 0 64 0L224 0l0 128c0 17.7 14.3 32 32 32l128 0 0 144-208 0c-35.3 0-64 28.7-64 64l0 144-48 0c-35.3 0-64-28.7-64-64L0 64zm384 64l-128 0L256 0 384 128zM176 352l32 0c30.9 0 56 25.1 56 56s-25.1 56-56 56l-16 0 0 32c0 8.8-7.2 16-16 16s-16-7.2-16-16l0-48 0-80c0-8.8 7.2-16 16-16zm32 80c13.3 0 24-10.7 24-24s-10.7-24-24-24l-16 0 0 48 16 0zm96-80l32 0c26.5 0 48 21.5 48 48l0 64c0 26.5-21.5 48-48 48l-32 0c-8.8 0-16-7.2-16-16l0-128c0-8.8 7.2-16 16-16zm32 128c8.8 0 16-7.2 16-16l0-64c0-8.8-7.2-16-16-16l-16 0 0 96 16 0zm80-112c0-8.8 7.2-16 16-16l48 0c8.8 0 16 7.2 16 16s-7.2 16-16 16l-32 0 0 32 32 0c8.8 0 16 7.2 16 16s-7.2 16-16 16l-32 0 0 48c0 8.8-7.2 16-16 16s-16-7.2-16-16l0-64 0-64z"/></svg>'
    ),
    # Export Markdown (fa-file-lines - Font Awesome 6 Free Solid)
    "export_md": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"><path fill="currentColor" d="M64 0C28.7 0 0 28.7 0 64L0 448c0 35.3 28.7 64 64 64l256 0c35.3 0 64-28.7 64-64l0-288-128 0c-17.7 0-32-14.3-32-32L224 0 64 0zM256 0l0 128 128 0L256 0zM112 256l160 0c8.8 0 16 7.2 16 16s-7.2 16-16 16l-160 0c-8.8 0-16-7.2-16-16s7.2-16 16-16zm0 64l160 0c8.8 0 16 7.2 16 16s-7.2 16-16 16l-160 0c-8.8 0-16-7.2-16-16s7.2-16 16-16zm0 64l160 0c8.8 0 16 7.2 16 16s-7.2 16-16 16l-160 0c-8.8 0-16-7.2-16-16s7.2-16 16-16z"/></svg>'
    ),
    # Quit (fa-arrow-right-from-bracket - Font Awesome 6 Free Solid)
    "app_quit": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="currentColor" d="M502.6 278.6c12.5-12.5 12.5-32.8 0-45.3l-128-128c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L402.7 224 192 224c-17.7 0-32 14.3-32 32s14.3 32 32 32l210.7 0-73.4 73.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0l128-128zM160 96c17.7 0 32-14.3 32-32s-14.3-32-32-32L96 32C43 32 0 75 0 128L0 384c0 53 43 96 96 96l64 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-64 0c-17.7 0-32-14.3-32-32l0-256c0-17.7 14.3-32 32-32l64 0z"/></svg>'
    ),
    # Find / Search (fa-magnifying-glass - Font Awesome 6 Free Solid)
    "search_find": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="currentColor" d="M416 208c0 45.9-14.9 88.3-40 122.7L502.6 457.4c12.5 12.5 12.5 32.8 0 45.3s-32.8 12.5-45.3 0L330.7 376c-34.4 25.2-76.8 40-122.7 40C93.1 416 0 322.9 0 208S93.1 0 208 0S416 93.1 416 208zM208 352a144 144 0 1 0 0-288 144 144 0 1 0 0 288z"/></svg>'
    ),
    # Replace (fa-arrows-rotate - Font Awesome 6 Free Solid)
    "search_replace": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="currentColor" d="M105.1 202.6c7.7-21.8 20.2-42.3 37.8-59.8c62.5-62.5 163.8-62.5 226.3 0L386.3 160 352 160c-17.7 0-32 14.3-32 32s14.3 32 32 32l111.5 0c0 0 0 0 0 0l.4 0c17.7 0 32-14.3 32-32l0-112c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 35.2L414.4 97.6c-87.5-87.5-229.3-87.5-316.8 0C73.2 122 55.6 150.7 44.8 181.4c-5.9 16.7 2.9 34.9 19.5 40.8s34.9-2.9 40.8-19.5zM39 289.3c-5 1.5-9.8 4.2-13.7 8.2c-4 4-6.7 8.8-8.1 14c-.3 1.2-.6 2.5-.8 3.8c-.3 1.7-.4 3.4-.4 5.1L16 432c0 17.7 14.3 32 32 32s32-14.3 32-32l0-35.1 17.6 17.5c0 0 0 0 0 0c87.5 87.4 229.3 87.4 316.7 0c24.4-24.4 42.1-53.1 52.9-83.8c5.9-16.7-2.9-34.9-19.5-40.8s-34.9 2.9-40.8 19.5c-7.7 21.8-20.2 42.3-37.8 59.8c-62.5 62.5-163.8 62.5-226.3 0l-.1-.1L125.6 352l34.4 0c17.7 0 32-14.3 32-32s-14.3-32-32-32L48.4 288c-1.6 0-3.2 .1-4.8 .3s-3.1 .5-4.6 1z"/></svg>'
    ),
    # Insert Image (fa-image - Font Awesome 6 Free Solid)
    "media_image": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="currentColor" d="M0 96C0 60.7 28.7 32 64 32l384 0c35.3 0 64 28.7 64 64l0 320c0 35.3-28.7 64-64 64L64 480c-35.3 0-64-28.7-64-64L0 96zM323.8 202.5c-4.5-6.6-11.9-10.5-19.8-10.5s-15.4 3.9-19.8 10.5l-87 127.6L170.7 297c-4.6-5.7-11.5-9-18.7-9s-14.2 3.3-18.7 9l-64 80c-5.8 7.2-6.9 17.1-2.9 25.4s12.4 13.6 21.6 13.6l96 0 32 0 208 0c8.9 0 17.1-4.9 21.2-12.8s3.6-17.4-1.4-24.7l-120-176zM112 192a48 48 0 1 0 0-96 48 48 0 1 0 0 96z"/></svg>'
    ),
    # Media Folder (fa-folder-open - Font Awesome 6 Free Solid)
    "media_folder": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><path fill="currentColor" d="M88.7 223.8L0 375.8 0 96C0 60.7 28.7 32 64 32l117.5 0c17 0 33.3 6.7 45.3 18.7l26.5 26.5c12 12 28.3 18.7 45.3 18.7L416 96c35.3 0 64 28.7 64 64l0 32-336 0c-22.8 0-43.8 12.1-55.3 31.8zm27.6 16.1C122.1 230 132.6 224 144 224l400 0c11.5 0 22 6.1 27.7 16.1s5.7 22.2-.1 32.1l-112 192C453.9 474 443.4 480 432 480L32 480c-11.5 0-22-6.1-27.7-16.1s-5.7-22.2 .1-32.1l112-192z"/></svg>'
    ),
    # Sync Scroll (fa-arrows-up-down - Font Awesome 6 Free Solid)
    "view_sync": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path fill="currentColor" d="M182.6 9.4c-12.5-12.5-32.8-12.5-45.3 0l-96 96c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L128 109.3l0 293.5L86.6 361.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l96 96c12.5 12.5 32.8 12.5 45.3 0l96-96c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 402.7l0-293.5 41.4 41.4c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3l-96-96z"/></svg>'
    ),
    # Appearance / Theme (fa-palette - Font Awesome 6 Free Solid)
    "settings_theme": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="currentColor" d="M512 256c0 .9 0 1.8 0 2.7c-.4 36.5-33.6 61.3-70.1 61.3L344 320c-26.5 0-48 21.5-48 48c0 3.4 .4 6.7 1 9.9c2.1 10.2 6.5 20 10.8 29.9c6.1 13.8 12.1 27.5 12.1 42c0 31.8-21.6 60.7-53.4 62c-3.5 .1-7 .2-10.6 .2C114.6 512 0 397.4 0 256S114.6 0 256 0S512 114.6 512 256zM128 288a32 32 0 1 0 -64 0 32 32 0 1 0 64 0zm0-96a32 32 0 1 0 0-64 32 32 0 1 0 0 64zM288 96a32 32 0 1 0 -64 0 32 32 0 1 0 64 0zm96 96a32 32 0 1 0 0-64 32 32 0 1 0 0 64z"/></svg>'
    ),
    # About (fa-circle-info - Font Awesome 6 Free Solid)
    "help_about": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="currentColor" d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM216 336l24 0 0-64-24 0c-13.3 0-24-10.7-24-24s10.7-24 24-24l48 0c13.3 0 24 10.7 24 24l0 88 8 0c13.3 0 24 10.7 24 24s-10.7 24-24 24l-80 0c-13.3 0-24-10.7-24-24s10.7-24 24-24zm40-208a32 32 0 1 1 0 64 32 32 0 1 1 0-64z"/></svg>'
    ),
    # Tag / Tags (fa-tags - Font Awesome 6 Free Solid)
    "tag": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="currentColor" d="M345 39.1L472.8 168.4c52.4 53 52.4 138.2 0 191.2L360.8 472.9c-9.3 9.4-24.5 9.5-33.9 .2s-9.5-24.5-.2-33.9L438.6 325.9c33.9-34.3 33.9-89.4 0-123.7L310.9 72.9c-9.3-9.4-9.2-24.6 .2-33.9s24.6-9.2 33.9 .2zM0 229.5L0 80C0 53.5 21.5 32 48 32l149.5 0c17 0 33.3 6.7 45.3 18.7l168 168c25 25 25 65.5 0 90.5L277.3 442.7c-25 25-65.5 25-90.5 0l-168-168C6.7 262.7 0 246.5 0 229.5zM144 144a32 32 0 1 0 -64 0 32 32 0 1 0 64 0z"/></svg>'
    ),
    # Plus (fa-plus - Font Awesome 6 Free Solid)
    "plus": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path fill="currentColor" d="M256 80c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 144L48 224c-17.7 0-32 14.3-32 32s14.3 32 32 32l144 0 0 144c0 17.7 14.3 32 32 32s32-14.3 32-32l0-144 144 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-144 0 0-144z"/></svg>'
    ),
    # Print (fa-print - Font Awesome 6 Free Solid)
    "print": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="currentColor" d="M128 0C92.7 0 64 28.7 64 64l0 96 64 0 0-96 226.7 0L384 93.3l0 66.7 64 0 0-66.7c0-17-6.7-33.3-18.7-45.3L400 18.7C388 6.7 371.7 0 354.7 0L128 0zM384 352l0 32 0 64-256 0 0-64 0-16 0-16 256 0zm64 32l32 0c17.7 0 32-14.3 32-32l0-96c0-35.3-28.7-64-64-64L64 192c-35.3 0-64 28.7-64 64l0 96c0 17.7 14.3 32 32 32l32 0 0 64c0 35.3 28.7 64 64 64l256 0c35.3 0 64-28.7 64-64l0-64zM432 248a24 24 0 1 1 0 48 24 24 0 1 1 0-48z"/></svg>'
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
    img.save(str(dest_path))
