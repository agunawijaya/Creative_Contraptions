@echo off
REM ===================================================================
REM  Jalankan GAME ASLI Creative Contraptions (DOS 1985) di DOSBox-X.
REM  Video: scaler 5x + koreksi aspek 4:3  ->  jendela 1600x1200.
REM
REM  Keluar dari game: CTRL+F9  (atau tutup jendela).
REM  Ganti ukuran: edit baris "scaler=" di run_original.conf
REM                (normal5x / normal4x / normal3x).
REM
REM  Catatan teknis: build DOSBox-X ini MENGABAIKAN opsi -c, jadi perintah
REM  mount ditulis ke [autoexec] pada salinan conf sementara di %TEMP%.
REM  Path diambil dari %~dp0, sehingga tetap benar kalau folder proyek
REM  dipindah atau di-rename.
REM ===================================================================
setlocal
cd /d "%~dp0"

set "DOSBOX=%~dp0tools\dosbox-x\bin\x64\Release\dosbox-x.exe"
set "GAMEDIR=%~dp0Creative-Contraptions"
set "BASECONF=%~dp0run_original.conf"
set "TMPCONF=%TEMP%\cc_original_run.conf"

if not exist "%DOSBOX%" (
    echo [GAGAL] DOSBox-X tidak ditemukan di:
    echo         %DOSBOX%
    echo         Cek folder tools\dosbox-x ^(mungkin belum diekstrak dari dosbox-x.zip^).
    pause
    exit /b 1
)
if not exist "%GAMEDIR%\BANTAM.EXE" (
    echo [GAGAL] File game tidak ditemukan di:
    echo         %GAMEDIR%
    pause
    exit /b 1
)
if not exist "%BASECONF%" (
    echo [GAGAL] run_original.conf tidak ditemukan.
    pause
    exit /b 1
)

REM -- salin conf dasar, lalu tambahkan [autoexec] berisi path saat ini --
copy /y "%BASECONF%" "%TMPCONF%" >nul
>>"%TMPCONF%" echo.
>>"%TMPCONF%" echo [autoexec]
>>"%TMPCONF%" echo mount c "%GAMEDIR%"
>>"%TMPCONF%" echo c:
>>"%TMPCONF%" echo BANTAM.EXE
>>"%TMPCONF%" echo exit

echo Menjalankan game ASLI lewat DOSBox-X ^(scaler 5x, 1600x1200^)...
"%DOSBOX%" -conf "%TMPCONF%"

endlocal
