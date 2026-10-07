#!/usr/bin/env bash
# =========================================================================
#  MarkNote - build AppImage trong container Ubuntu 20.04 (glibc 2.31)
#  de file chay duoc tren NHIEU distro hon (Ubuntu 20.04+, Debian 11+...).
#
#  Vi sao? AppImage lay glibc cua may build. May moi (glibc 2.42) se tao
#  AppImage chi chay tren distro moi. Build trong distro cu => tuong thich rong.
#
#  Yeu cau: Docker (hoac Podman bat =1).
#
#  Cach chay:
#    bash packaging/build_appimage_docker.sh
#
#  Ket qua: dist/MarkNote-1.1-x86_64.AppImage
# =========================================================================
set -euo pipefail

APP_VERSION="${APP_VERSION:-1.1}"
IMAGE="${IMAGE:-ubuntu:20.04}"

docker run --rm -v "$PWD:/src" -w /src "$IMAGE" bash -c "
set -eux
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq python3.10 python3.10-venv python3-pip \
    libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 \
    libjpeg-dev libopenjp2-7-dev libffi-dev libcairo2 \
    curl file wget ca-certificates
# Python 3.10 venv (Ubuntu 20.04 mac dinh python3 la 3.8)
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
python3 -m venv /opt/build --system-site-packages
/opt/build/bin/pip install --upgrade pip
/opt/build/bin/pip install pyinstaller
# chạy đúng lệnh build giống make appimage
/opt/build/bin/pyinstaller --noconfirm --clean --onedir --name marknote --windowed \
    --paths src --add-data 'assets:assets' \
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
"

# Dong goi AppImage o may chu (docker co the khong co GUI/fuse)
mkdir -p build/appimage/usr/bin
cp -r dist/marknote/* build/appimage/usr/bin/
cat > build/appimage/AppRun <<'SH'
#!/bin/sh
HERE="$(dirname "$(readlink -f "${0}")")"
unset QT_PLUGIN_PATH
export QTWEBENGINE_DISABLE_SANDBOX=1
exec "$HERE/usr/bin/marknote" "$@"
SH
chmod +x build/appimage/AppRun
cat > build/appimage/marknote.desktop <<'SH'
[Desktop Entry]
Name=MarkNote
Comment=Offline Markdown notes with live preview
Exec=marknote
Icon=marknote
Type=Application
Categories=Utility;
Terminal=false
SH
# icon: tao lai tu venv may hien tai (neu co) hoac bo qua
if [ -x .venv/bin/python ]; then .venv/bin/python packaging/make_icon.py dist/marknote.png; fi

if [ ! -f appimagetool-x86_64.AppImage ]; then
    curl -sL -o appimagetool-x86_64.AppImage \
        https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

cp dist/marknote.png build/appimage/marknote.png
APPIMAGE_EXTRACT_AND_RUN=1 ./appimagetool-x86_64.AppImage --no-appstream \
    build/appimage "dist/MarkNote-${APP_VERSION}-x86_64.AppImage"
echo "XONG: dist/MarkNote-${APP_VERSION}-x86_64.AppImage"