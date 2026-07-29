# Kompilasi satu berkas .c dengan Microsoft C 1.04 di dalam DOSBox-X.
#
#   pwsh src_c/build/compile.ps1 rnd
#
# Menghasilkan src_c/out/<nama>.OBJ + <nama>.log
# Catatan: build DOSBox-X di tools/ MENGABAIKAN opsi -c, jadi perintah ditulis
# ke [autoexec]. Nama berkas WAJIB 8.3 — DOS tidak mengenal nama panjang.
param([Parameter(Mandatory=$true)][string]$Name)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path "$PSScriptRoot\..\..").Path
$dos  = "$root\src_c\build\dos"
$bin  = "$root\tools\msc104\bin"
$out  = "$root\src_c\out"

if ($Name.Length -gt 8) { throw "Nama '$Name' lebih dari 8 karakter — DOS tidak akan mengenalinya." }
$src = "$root\src_c\src\$Name.c"
if (-not (Test-Path $src)) { throw "Tidak ada: $src" }
if (-not (Test-Path $bin\MC1.EXE)) { throw "Kompiler tidak ada di $bin (unduh MS C 1.04 dulu)" }

New-Item -ItemType Directory -Force -Path $dos, $out | Out-Null
Copy-Item $src "$dos\$Name.C" -Force
Remove-Item "$dos\$Name.OBJ","$dos\build.log" -ErrorAction SilentlyContinue

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
y:\MC1 $Name > x:\build.log
y:\MC2 $Name >> x:\build.log
exit
"@
Set-Content "$root\src_c\build\_gen.conf" -Value $conf -Encoding ASCII
Start-Process "$root\tools\dosbox-x\bin\x64\Release\dosbox-x.exe" `
    -ArgumentList '-conf',"$root\src_c\build\_gen.conf" -WindowStyle Minimized -Wait

if (Test-Path "$dos\build.log") {
    Copy-Item "$dos\build.log" "$out\$Name.log" -Force
    Get-Content "$dos\build.log"
}
if (Test-Path "$dos\$Name.OBJ") {
    Copy-Item "$dos\$Name.OBJ" "$out\$Name.OBJ" -Force
    "OBJ: src_c/out/$Name.OBJ  ($((Get-Item "$dos\$Name.OBJ").Length) byte)"
} else {
    "GAGAL: .OBJ tidak terbentuk — lihat log di atas."
    exit 1
}
