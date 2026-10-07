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
#  Xuat PDF KHONG can pacman/MSYS2: script tu tai "weasyprint-windows.zip"
#  (ban chinh thuc cua WeasyPrint, da dong goi san Pango) va dat
#  weasyprint.exe vao ben trong goi cai. Ung dung tu dong dung no khi
#  Python weasyprint khong tim thay Pango.
# =========================================================================
$ErrorActionPreference = "Stop"
$AppVersion = "1.1"
$Python = "python"
# Nie nhat dinh ban weasyprint-windows.zip (co san Pango, file chinh thuc)
$WeasyVersion = "v68.1"
$WeasyUrl = "https://github.com/Kozea/WeasyPrint/releases/download/$WeasyVersion/weasyprint-windows.zip"

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

Run-Checked "Dong goi san weasyprint.exe (kem Pango) cho xuat PDF" {
    $weasyZip = "build\weasyprint-windows.zip"
    if (Test-Path "dist\marknote\bin\weasyprint\weasyprint.exe") {
        Write-Host "Da co san, bo qua."
    }
    else {
        if (-not (Test-Path $weasyZip)) {
            Write-Host "Tai $WeasyUrl ..."
            Invoke-WebRequest -Uri $WeasyUrl -OutFile $weasyZip
        }
        $extractDir = "build\weasyprint-windows"
        if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force }
        Expand-Archive -Path $weasyZip -DestinationPath $extractDir -Force
        $exe = Get-ChildItem -Path $extractDir -Recurse -Filter "*.exe" |
            Select-Object -First 1
        if (-not $exe) { throw "Khong tim thay .exe trong goi weasyprint chinh thuc." }
        New-Item -ItemType Directory -Force -Path "dist\marknote\bin\weasyprint" | Out-Null
        Copy-Item $exe.FullName "dist\marknote\bin\weasyprint\weasyprint.exe" -Force
        Write-Host "Dong goi xong: dist\marknote\bin\weasyprint\weasyprint.exe"
    }
}

Write-Host ""
Write-Host "Hoan tat. Chay thu: dist\marknote\marknote.exe"
Write-Host "Goi chuyen di:   dist\MarkNote-$AppVersion-windows-x64.zip"