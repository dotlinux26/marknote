#!/usr/bin/env bash
# =========================================================================
#  MarkNote - Build all Linux distribution packages
#  Outputs:
#    - dist/MarkNote-<version>-x86_64.AppImage   (Universal AppImage)
#    - dist/marknote_<version>_amd64.deb         (Debian / Ubuntu / Mint)
#    - dist/marknote-<version>.x86_64.rpm        (Fedora / RHEL / openSUSE)
#    - dist/MarkNote-<version>-linux-x64.tar.gz  (Standalone portable folder)
#    - dist/marknote-<version>.tar.gz            (Source tarball)
# =========================================================================
set -euo pipefail

APP_VERSION="${APP_VERSION:-1.2.5}"
PYTHON="${PYTHON:-python3}"

echo "=================================================="
echo " Building MarkNote v${APP_VERSION} for Linux"
echo "=================================================="

# 1. Clean previous build dirs
mkdir -p dist build

# 2. Build PyInstaller onedir bundle
echo "==> Running PyInstaller build..."
"$PYTHON" -m PyInstaller --noconfirm --clean --onedir --name marknote --windowed \
    --paths src --add-data "assets:assets" \
    --hidden-import markdown_it.presets.gfm_like \
    --hidden-import markdown_it.plugins.linkify \
    --hidden-import markdown_it.plugins \
    --hidden-import media \
    --collect-all mdit_py_plugins --collect-all pygments \
    --collect-all weasyprint --collect-all tinycss2 \
    --collect-all cssselect2 --collect-all tinyhtml5 \
    --collect-all pydyf --collect-all pyphen \
    --collect-submodules fontTools \
    --exclude-module PyQt5 --exclude-module PyQt6 \
    --exclude-module PySide2 --exclude-module tkinter \
    src/main.py

# 3. Ensure icon exists
mkdir -p build/appimage/usr/bin
if [ -f assets/marknote.png ]; then
    cp assets/marknote.png dist/marknote.png
else
    "$PYTHON" packaging/make_icon.py dist/marknote.png
fi

# 4. Create AppDir for AppImage
echo "==> Preparing AppDir..."
rm -rf build/appimage
mkdir -p build/appimage/usr/bin
mkdir -p build/appimage/usr/share/applications
mkdir -p build/appimage/usr/share/icons/hicolor/256x256/apps

cp -r dist/marknote/* build/appimage/usr/bin/

cat > build/appimage/AppRun <<'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "${0}")")"
unset QT_PLUGIN_PATH
export QTWEBENGINE_DISABLE_SANDBOX=1
exec "$HERE/usr/bin/marknote" "$@"
EOF
chmod +x build/appimage/AppRun

cat > build/appimage/marknote.desktop <<'EOF'
[Desktop Entry]
Name=MarkNote
Comment=Offline Markdown notes with live preview and media library
Exec=marknote
Icon=marknote
Type=Application
Categories=Utility;Office;TextEditor;
Terminal=false
StartupWMClass=marknote
EOF

cp build/appimage/marknote.desktop build/appimage/usr/share/applications/marknote.desktop
cp dist/marknote.png build/appimage/marknote.png
cp dist/marknote.png build/appimage/usr/share/icons/hicolor/256x256/apps/marknote.png

# 5. Build AppImage using appimagetool
echo "==> Building AppImage..."
if [ ! -f appimagetool-x86_64.AppImage ]; then
    echo "Downloading appimagetool..."
    curl -sL -o appimagetool-x86_64.AppImage \
        https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

APPIMAGE_EXTRACT_AND_RUN=1 ./appimagetool-x86_64.AppImage --no-appstream \
    build/appimage "dist/MarkNote-${APP_VERSION}-x86_64.AppImage"
echo "Generated AppImage: dist/MarkNote-${APP_VERSION}-x86_64.AppImage"

# 6. Build Debian (.deb) package
echo "==> Building Debian (.deb) package..."
DEB_ROOT="build/deb/marknote_${APP_VERSION}_amd64"
rm -rf "$DEB_ROOT"
mkdir -p "$DEB_ROOT/usr/lib/marknote"
mkdir -p "$DEB_ROOT/usr/bin"
mkdir -p "$DEB_ROOT/usr/share/applications"
mkdir -p "$DEB_ROOT/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$DEB_ROOT/DEBIAN"

cp -r dist/marknote/* "$DEB_ROOT/usr/lib/marknote/"

cat > "$DEB_ROOT/usr/bin/marknote" <<'EOF'
#!/bin/sh
export QTWEBENGINE_DISABLE_SANDBOX=1
exec /usr/lib/marknote/marknote "$@"
EOF
chmod +x "$DEB_ROOT/usr/bin/marknote"

cp build/appimage/marknote.desktop "$DEB_ROOT/usr/share/applications/"
cp dist/marknote.png "$DEB_ROOT/usr/share/icons/hicolor/256x256/apps/marknote.png"

cat > "$DEB_ROOT/DEBIAN/control" <<EOF
Package: marknote
Version: ${APP_VERSION}
Section: utils
Priority: optional
Architecture: amd64
Maintainer: dotlinux26 <https://github.com/dotlinux26/marknote>
Description: Offline Markdown notes with live preview and media library
 MarkNote is an offline Markdown note-taking desktop application built with
 PySide6 and Qt 6. It features split-pane live preview, CSS theme support,
 FTS5 full-text search, standalone HTML/PDF export, image insertion at cursor,
 drag-and-drop, and a central media library.
EOF

dpkg-deb --build "$DEB_ROOT" "dist/marknote_${APP_VERSION}_amd64.deb"
echo "Generated DEB: dist/marknote_${APP_VERSION}_amd64.deb"

# 7. Build RPM package if alien or rpmbuild is available
if command -v alien >/dev/null 2>&1; then
    echo "==> Building RPM package via alien..."
    alien -r --scripts "dist/marknote_${APP_VERSION}_amd64.deb"
    find . -maxdepth 1 -name "marknote*.rpm" -exec mv {} "dist/marknote-${APP_VERSION}.x86_64.rpm" \;
    echo "Generated RPM: dist/marknote-${APP_VERSION}.x86_64.rpm"
fi

# 8. Build Standalone Portable Tarball
echo "==> Building Portable Standalone Tarball..."
tar -czf "dist/MarkNote-${APP_VERSION}-linux-x64.tar.gz" -C dist marknote
echo "Generated Tarball: dist/MarkNote-${APP_VERSION}-linux-x64.tar.gz"

# 9. Build Source Tarball
echo "==> Building Source Tarball..."
tar -czf "dist/marknote-${APP_VERSION}.tar.gz" \
    --transform="s,^,marknote-${APP_VERSION}/," \
    KEHOACH_MarkNote.md Makefile LICENSE README.md CHANGELOG \
    requirements.txt packaging assets docs src
echo "Generated Source Tarball: dist/marknote-${APP_VERSION}.tar.gz"

echo ""
echo "=================================================="
echo " All Linux packages built successfully in dist/:"
ls -lh dist/
echo "=================================================="
