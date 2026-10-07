# =========================================================================
#  MarkNote - build thanh phan phoi tren Windows (PyInstaller)
#  Chay tren may Windows co Python 3.10+ (cai tu python.org).
#
#  Cach chay (PowerShell):
#    powershell -ExecutionPolicy Bypass -File packaging\build_windows.ps1
#
#  Ket qua:
#    dist\MarkNote-1.1\                   thu muc chay duoc (gan Python dem)
#    dist\MarkNote-1.1-windows-x64.zip    goi nen de chuyen di
#
#  LUU Y ve chuc nang xuat PDF (khi chay cung ung dung):
#    WeasyPrint tren Windows can thu vien Pango. Cai qua MSYS2:
#      - cai MSYS2 (https://www.msys2.org), mo "UCRT64" shell, chay:
#          pacman -S mingw-w64-ucrt-x86_64-pango
#      - truoc khi chay MarkNote dat bien moi truong:
#          set WEASYPRINT_DLL_DIRECTORIES=C:\msys64\ucrt64\bin
#    Neu khong can xuat PDF thi khong can buoc nay.
# =========================================================================
$ErrorActionPreference = "Stop"
$AppVersion = "1.1"
$Python = "python"

function Run-Checked {
    param([string]$Desc, [scriptblock]$Cmd)
    Write-Host "==> $Desc"
    & $Cmd
    if ($LASTEXITCODE -ne 0) { throw "That bai: $Desc" }
}

if (-not (Get-Command $Python -ErrorAction SilentlyContinue)) {
    Write-Host "Chua co Python trong PATH. Cai Python 3.10+ roi chay lai."
    exit 1
}

Run-Checked "Tao moi truong ao .venv" {
    & $Python -m venv .venv
    & ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
}

Run-Checked "Cai thu vien tu requirements.txt" {
    & ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
}

Run-Checked "Cai PyInstaller" {
    & ".\.venv\Scripts\python.exe" -m pip install pyinstaller
}

Run-Checked "Build ung dung (PyInstaller onedir)" {
    & ".\.venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onedir `
        --name marknote --windowed --paths src --add-data "assets;assets" `
        --hidden-import markdown_it.presets.gfm_like `
        --hidden-import markdown_it.plugins.linkify `
        --hidden-import markdown_it.plugins `
        --collect-all mdit_py_plugins --collect-all pygments `
        --collect-all weasyprint --collect-all tinycss2 `
        --collect-all cssselect2 --collect-all tinyhtml5 `
        --collect-all pydyf --collect-all pyphen `
        --collect-submodules fontTools `
        --exclude-module PyQt5 --exclude-module PySide2 `
        --exclude-module tkinter `
        src\main.py
}

Run-Checked "Tao file zip de chuyen di" {
    if (Test-Path "dist\MarkNote-$AppVersion-windows-x64.zip") {
        Remove-Item "dist\MarkNote-$AppVersion-windows-x64.zip"
    }
    Compress-Archive -Path "dist\marknote\*" `
        -DestinationPath "dist\MarkNote-$AppVersion-windows-x64.zip"
}

Write-Host ""
Write-Host "Hoan tat. Chay thu: dist\marknote\marknote.exe"
Write-Host "Goi chuyen di:   dist\MarkNote-$AppVersion-windows-x64.zip"