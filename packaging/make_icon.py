"""Tao icon PNG cho MarkNote dung trong AppImage / desktop (khong thuoc app)."""
import argparse
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter
from PySide6.QtWidgets import QApplication


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("out", nargs="?", default="dist/marknote.png")
    parser.add_argument("--size", type=int, default=256)
    args = parser.parse_args()

    app = QApplication.instance() or QApplication([])
    img = QImage(args.size, args.size, QImage.Format.Format_ARGB32)
    img.fill(QColor("#2563eb"))
    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    font = QFont("Sans Serif", int(args.size * 0.6), QFont.Weight.Bold)
    painter.setFont(font)
    painter.setPen(QColor("white"))
    painter.drawText(img.rect(), Qt.AlignmentFlag.AlignCenter, "M")
    painter.end()
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(path))
    print(f"icon ok: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())