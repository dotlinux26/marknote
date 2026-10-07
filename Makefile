PREFIX ?= /usr/local
DESTDIR ?=
APP_VERSION := 1.0
PACKAGE := marknote

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
	python3 src/main.py

dist:
	rm -f $(PACKAGE)-$(APP_VERSION).tar.gz
	tar -czf $(PACKAGE)-$(APP_VERSION).tar.gz \
		--transform='s,^,$(PACKAGE)-$(APP_VERSION)/,' \
		KEHOACH_MarkNote.md Makefile LICENSE README.md CHANGELOG \
		requirements.txt \
		assets docs src
	@echo "Da tao goi: $(PACKAGE)-$(APP_VERSION).tar.gz"

clean:
	find src -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name '*.pyc' -delete 2>/dev/null || true
	rm -f $(PACKAGE)-$(APP_VERSION).tar.gz
	@echo "Da don dep."

.PHONY: install uninstall run dist clean