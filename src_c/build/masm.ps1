# Rakit satu berkas .asm dengan Microsoft MACRO Assembler 1.27 (1984) di DOSBox-X.
#
#   pwsh src_c/build/masm.ps1 -Name vbio
#
# Menghasilkan src_c/out/<nama>.OBJ + <nama>.lst + <nama>.log
#
# MASM 1.27 diekstrak dari image floppy arsip (ms-masm-v127-840529) ke
# tools/masm/bin. Dipilih yang SEZAMAN (1984) supaya pilihan encoding-nya
# sedekat mungkin dengan yang dipakai penulis aslinya tahun 1985.
#
# Baris perintah MASM 1.x: MASM sumber,objek,listing,crossref;
# Titik koma di ujung menekan semua prompt.
# Nama berkas WAJIB 8.3 — DOS tidak mengenal nama panjang.
param([Parameter(Mandatory=$true)][string]$Name)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path "$PSScriptRoot\..\..").Path
$dos  = "$root\src_c\build\dos"
$bin  = "$root\tools\masm\bin"
$out  = "$root\src_c\out"

if ($Name.Length -gt 8) { throw "Nama '$Name' lebih dari 8 karakter." }
$src = "$root\src_c\asm\$Name.asm"
if (-not (Test-Path $src)) { throw "Tidak ada: $src" }
if (-not (Test-Path $bin\MASM.EXE)) { throw "MASM tidak ada di $bin" }

New-Item -ItemType Directory -Force -Path $dos, $out | Out-Null
# MASM 1.27 butuh akhir baris CRLF. Berkas ber-LF dibaca sebagai SATU baris
# dan gagal dengan "End of file, no END directive" -- gejalanya menyesatkan.
$text = (Get-Content $src -Raw) -replace "`r`n", "`n" -replace "`n", "`r`n"
[IO.File]::WriteAllText("$dos\$Name.ASM", $text, [Text.Encoding]::ASCII)
Remove-Item "$dos\$Name.OBJ","$dos\masm.log" -ErrorAction SilentlyContinue

$conf = @"
[dosbox]
machine=cga
[cpu]
cputype=386
cycles=fixed 30000
[autoexec]
mount x "$dos"
mount y "$bin"
x:
y:\MASM $Name,$Name,$Name,NUL; > x:\masm.log
exit
"@
Set-Content "$root\src_c\build\_masm.conf" -Value $conf -Encoding ASCII
Start-Process "$root\tools\dosbox-x\bin\x64\Release\dosbox-x.exe" `
    -ArgumentList '-conf',"$root\src_c\build\_masm.conf" -WindowStyle Minimized -Wait

if (Test-Path "$dos\masm.log") {
    Copy-Item "$dos\masm.log" "$out\$Name.log" -Force
    Get-Content "$dos\masm.log"
}
if (Test-Path "$dos\$Name.OBJ") {
    Copy-Item "$dos\$Name.OBJ" "$out\$Name.OBJ" -Force
    if (Test-Path "$dos\$Name.LST") { Copy-Item "$dos\$Name.LST" "$out\$Name.lst" -Force }
    "OBJ: src_c/out/$Name.OBJ  ($((Get-Item "$dos\$Name.OBJ").Length) byte)"
} else {
    "GAGAL: .OBJ tidak terbentuk - lihat log di atas."
    exit 1
}
