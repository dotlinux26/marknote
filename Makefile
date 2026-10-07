PREFIX ?= /usr/local
DESTDIR ?=
APP_VERSION := 1.1
PACKAGE := marknote
PY ?= python3
APPIMAGETOOL ?= appimagetool-x86_64.AppImage
PYINSTALLER ?= .venv/bin/python -m PyInstaller

install:
	mkdir -p $(DESTDIR)$(PREFIX)/lib/$(PACKAGE) $(DESTDIR)$(PREFIX)/bin
	cp -r src assets $(DESTDIR)$(PREFIX)/lib/$(PACKAGE)/
	printf '#!/bin/sh\n# Launcher cai dat cho MarkNote\nexec /usr/bin/env python3 %s/src/main.py "$$@"\n' "$(DESTDIR)$(PREFIX)/lib/$(PACKAGE)" > $(DESTDIR)$(PREFIX)/bin/$(PACKAGE)
	chmod +x $(DESTDIR)$(PREFIX)/bin/$(PACKAGE)
	@echo "Da cai dat xong: $(PACKAGE)"
	@echo "Chay bang lenh: $(PACKAGE)"
	@echo "Du lieu ung dung nam o: ~/.marknote/"

uninstall:
	rm -rf $(DESTDIR)$(PREFIX)/lib/$(PACKAGE)
	rm -f $(DESTDIR)$(PREFIX)/bin/$(PACKAGE)
	@echo "Da go cai dat $(PACKAGE)"

run:
	@if [ -x .venv/bin/python ]; then .venv/bin/python src/main.py; else $(PY) src/main.py; fi

# Build tu dong: mot file AppImage tu choi het (PySide6 + WebEngine + Python).
# Luu y: can build trong distro co glibc cu (vi du docker ubuntu:20.04) de
# AppImage chay duoc tren distro khac — xem docs/HUONG_DAN_CAI_DAT.md.
appimage:
	@$(PY) -m pip show pyinstaller >/dev/null 2>&1 || $(PY) -m pip install pyinstaller
	$(PYINSTALLER) --noconfirm --clean --onedir --name marknote --windowed \
		--paths src --add-data "assets:assets" \
		--hidden-import markdown_it.presets.gfm_like \
		--hidden-import markdown_it.plugins.linkify \
		--hidden-import markdown_it.plugins \
		--collect-all mdit_py_plugins --collect-all pygments \
		--collect-all weasyprint --collect-all tinycss2 \
		--collect-all cssselect2 --collect-all tinyhtml5 \
		--collect-all pydyf --collect-all pyphen \
		--collect-submodules fontTools \
		--exclude-module PyQt5 --exclude-module PyQt6 \
		--exclude-module PySide2 --exclude-module tkinter \
		src/main.py
	rm -rf build/appimage dist/marknote.AppDir
	mkdir -p build/appimage/usr/bin
	cp -r dist/marknote/* build/appimage/usr/bin/
	printf '#!/bin/sh\nHERE=$$(dirname "$$(readlink -f "$${0}")")\nunset QT_PLUGIN_PATH\nexport QTWEBENGINE_DISABLE_SANDBOX=1\nexec "$$HERE/usr/bin/marknote" "$$@"\n' > build/appimage/AppRun
	chmod +x build/appimage/AppRun
	printf '[Desktop Entry]\nName=MarkNote\nComment=Offline Markdown notes with live preview\nExec=marknote\nIcon=marknote\nType=Application\nCategories=Utility;\nTerminal=false\n' > build/appimage/marknote.desktop
	ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 $(APPIMAGETOOL) --no-appstream build/appimage dist/MarkNote-$(APP_VERSION)-x86_64.AppImage
	@echo "AppImage: dist/MarkNote-$(APP_VERSION)-x86_64.AppImage"

dist:
	rm -f $(PACKAGE)-$(APP_VERSION).tar.gz
	tar -czf $(PACKAGE)-$(APP_VERSION).tar.gz \
		--transform='s,^,$(PACKAGE)-$(APP_VERSION)/,' \
		KEHOACH_MarkNote.md Makefile LICENSE README.md CHANGELOG \
		requirements.txt packaging \
		assets docs src
	@echo "Da tao goi: $(PACKAGE)-$(APP_VERSION).tar.gz"

clean:
	find src -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name '*.pyc' -delete 2>/dev/null || true
	rm -rf dist build
	rm -f $(PACKAGE)-$(APP_VERSION).tar.gz marknote.spec
	@echo "Da don dep."

.PHONY: install uninstall run appimage dist clean