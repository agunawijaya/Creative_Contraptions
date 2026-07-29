@echo off
REM ===================================================================
REM  Jalankan HASIL PORT (Python/pygame) Creative Contraptions.
REM
REM  Kontrol: panah = navigasi menu / pilih part, ENTER = pilih/tempatkan,
REM           SPACE = jalankan contraption, ESC = mundur, Q = keluar.
REM  Butuh: Python 3 + pygame  (pasang: pip install pygame)
REM ===================================================================
setlocal
cd /d "%~dp0"

set "PY="
where python >nul 2>&1 && set "PY=python"
if not defined PY ( where py >nul 2>&1 && set "PY=py" )

if not defined PY (
    echo [GAGAL] Python tidak ditemukan di PATH.
    echo         Pasang Python 3 dari https://www.python.org/downloads/
    pause
    exit /b 1
)

%PY% -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo [GAGAL] Modul pygame belum terpasang.
    echo         Jalankan:  %PY% -m pip install pygame
    pause
    exit /b 1
)

REM -- bundel aset: dibuat sekali, sesudah itu port tidak butuh folder game asli --
if not exist "%~dp0port\cc\data\GRAPH" (
    echo Bundel aset belum ada, membuat sekali jalan...
    %PY% "%~dp0port\import_assets.py"
    if errorlevel 1 (
        echo.
        echo [GAGAL] Bundel aset tidak bisa dibuat.
        echo         Tunjuk folder game asli secara manual:
        echo             %PY% port\import_assets.py ^<folder_game^>
        pause
        exit /b 1
    )
    echo.
)

echo Menjalankan PORT Python...
%PY% "%~dp0port\main.py" %*
if errorlevel 1 pause

endlocal
