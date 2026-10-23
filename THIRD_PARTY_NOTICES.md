# Third-Party Notices & Licenses

MarkNote is licensed under the [MIT License](LICENSE). 

This project incorporates, links to, and utilizes several open-source software (OSS) libraries, runtimes, and components. This document provides copyright notices, licensing terms, and obligations for all third-party software utilized in MarkNote.

---

## 1. Summary of Dependencies & Licenses

| Component / Library | Minimum Version | License Type | Upstream Project | Role in MarkNote |
|:--------------------|:---------------:|:------------:|:-----------------|:-----------------|
| **Python** | 3.10+ | PSF License | [python.org](https://www.python.org/) | Runtime & core application logic execution |
| **PySide6 / Qt 6** | 6.5+ | LGPLv3 / GPLv3 | [qt.io](https://www.qt.io/) | GUI framework, widgets, styling, and QtWebEngine |
| **SQLite (FTS5)** | 3.35+ | Public Domain / Blessing | [sqlite.org](https://www.sqlite.org/) | Local note database, tagging, and FTS5 full-text indexing |
| **markdown-it-py** | 3.0+ | MIT | [markdown-it-py](https://github.com/executablebooks/markdown-it-py) | CommonMark & GFM Markdown parser |
| **linkify-it-py** | 2.0+ | MIT | [linkify-it-py](https://github.com/tsutsu3/linkify-it-py) | Automatic link recognition in Markdown text |
| **mdit-py-plugins** | 0.4+ | MIT | [mdit-py-plugins](https://github.com/executablebooks/mdit-py-plugins) | Extended syntax plugins (task lists, footnotes) |
| **Pygments** | 2.15+ | BSD-2-Clause | [pygments.org](https://pygments.org/) | Syntax highlighting engine for code blocks |
| **WeasyPrint** | 60.0+ | BSD-3-Clause | [weasyprint.org](https://weasyprint.org/) | Visual HTML/CSS to PDF rendering engine |
| **Pango / HarfBuzz / GObject** | 1.44+ | LGPL-2.1+ / MIT | [pango.gnome.org](https://pango.gnome.org/) | Font layout, glyph shaping, text rendering (PDF export) |
| **tinycss2** | 1.2+ | BSD-3-Clause | [tinycss2](https://github.com/Kozea/tinycss2) | Low-level CSS parser used by WeasyPrint |
| **cssselect2** | 0.7+ | BSD-3-Clause | [cssselect2](https://github.com/Kozea/cssselect2) | CSS3 selectors implementation for WeasyPrint |
| **tinyhtml5** | 2.0+ | MIT | [tinyhtml5](https://github.com/CourtBouillon/tinyhtml5) | HTML parser used by WeasyPrint |
| **pydyf** | 0.8+ | BSD-3-Clause | [pydyf](https://github.com/CourtBouillon/pydyf) | Low-level PDF generator |
| **Pyphen** | 0.14+ | GPL-2.0+ / LGPL-2.1+ / MPL-1.1 | [pyphen](https://github.com/Kozea/Pyphen) | Hyphenation library for formatted PDF export |
| **fonttools** | 4.40+ | MIT / Apache-2.0 | [fonttools](https://github.com/fonttools/fonttools) | Font file parsing and manipulation for PDF rendering |
| **Pillow (PIL)** | 9.5+ | HPND (MIT-like) | [python-pillow.org](https://python-pillow.org/) | Image format decoding and raster processing |

---

## 2. LGPLv3 Compliance Notice (PySide6 / Qt 6)

MarkNote uses **PySide6 (Qt for Python)**, which is licensed under the **GNU Lesser General Public License version 3 (LGPLv3)**.

### Dynamic Linking & User Replacement
In accordance with LGPLv3 Section 4:
1. MarkNote does **not** modify the source code of Qt or PySide6.
2. MarkNote utilizes Qt via **dynamic linking** (`.dll` files on Windows, `.so` files on Linux).
3. In binary distributions (such as PyInstaller `onedir` or AppImage), the Qt shared libraries (e.g., `Qt6Core`, `Qt6Widgets`, `Qt6Gui`, `Qt6WebEngineCore`) remain dynamically linked and modular in the distribution folder (`_internal/`).
4. Users have the legal right and technical ability to replace the included Qt/PySide6 dynamic shared libraries with their own custom or updated versions without violating MarkNote's application license.

Source code for PySide6 and Qt is available from:
- Qt Project: <https://code.qt.io/>
- PySide6: <https://code.qt.io/cgit/pyside/pyside-setup.git>

---

## 3. License Texts & Copyright Notices

### MIT License
Used by: **MarkNote**, **markdown-it-py**, **linkify-it-py**, **mdit-py-plugins**, **tinyhtml5**

```text
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

### BSD 2-Clause License
Used by: **Pygments**
Copyright (c) 2006-2026 by the Pygments team.

```text
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

---

### BSD 3-Clause License
Used by: **WeasyPrint**, **tinycss2**, **cssselect2**, **pydyf**
Copyright (c) CourtBouillon and WeasyPrint contributors.

```text
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software without
   specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

---

### Python Software Foundation (PSF) License
Used by: **Python Runtime**
Copyright (c) 2001-2026 Python Software Foundation. All rights reserved.

Licensed under the Python Software Foundation License Agreement:
<https://docs.python.org/3/license.html>

---

### SQLite Dedication & Blessing
Used by: **SQLite & FTS5**

```text
The author disclaims copyright to this source code. In place of
a legal notice, here is a blessing:

   May you do good and not evil.
   May you find forgiveness for yourself and forgive others.
   May you share freely, never taking more than you give.
```
All code in SQLite is in the public domain: <https://www.sqlite.org/copyright.html>
