# LINK seluruh .OBJ menjadi src_c/out/CONTRAP.EXE memakai LINK.EXE 1.10 asli.
#
#   pwsh src_c/build/link.ps1
#
# Catatan penting:
#  - Baris perintah DOS dibatasi 127 karakter, sedangkan daftar objek kita
#    jauh lebih panjang. Karena itu masukan LINK diberikan lewat REDIRECT
#    dari berkas ("LINK < link.in"), format prompt: modul objek / run file /
#    map file / pustaka. Tanda "+" di ujung baris = lanjut ke baris berikutnya.
#  - C.OBJ (crt0) HARUS pertama: itu yang menentukan awal segmen kode dan
#    sudah terbukti cocok byte-per-byte dengan biner asli.
#  - gdata.OBJ diletakkan setelah kode agar DGROUP tersusun seperti aslinya.
$ErrorActionPreference = "Stop"
$root = (Resolve-Path "$PSScriptRoot\..\..").Path
$dos  = "$root\src_c\build\dos"
$bin  = "$root\tools\msc104\bin"
$out  = "$root\src_c\out"
New-Item -ItemType Directory -Force -Path $dos, $out | Out-Null

# Urutan: crt0, lalu semua modul kode, lalu data, lalu stub.
$objs = @()
$code = Get-ChildItem "$out\*.OBJ" | Where-Object {
    $n = $_.BaseName
    $n -notlike "probe*" -and $n -ne "gdata" -and $n -ne "stubs"
} | Sort-Object BaseName
foreach ($f in $code) { $objs += $f.BaseName }
$objs += "gdata"
$objs += "stubs"

foreach ($n in @($objs)) { Copy-Item "$out\$n.OBJ" "$dos\$n.OBJ" -Force }

# Susun masukan LINK: potong daftar objek jadi baris <=60 char, akhiri "+".
$lines = @()
$cur = "y:C"
foreach ($n in $objs) {
    if (($cur.Length + $n.Length + 1) -gt 60) { $lines += ($cur + "+"); $cur = $n }
    else { $cur = $cur + "+" + $n }
}
$lines += $cur
$lines += "CONTRAP"          # run file
$lines += "CONTRAP"          # map file
$lines += "y:MC"             # pustaka
Set-Content "$dos\link.in" -Value ($lines -join "`r`n") -Encoding ASCII

Get-ChildItem "$dos\CONTRAP.EXE","$dos\link.log" -ErrorAction SilentlyContinue | Remove-Item -Force
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
y:\LINK < x:\link.in > x:\link.log
exit
"@
Set-Content "$root\src_c\build\_link.conf" -Value $conf -Encoding ASCII
Start-Process "$root\tools\dosbox-x\bin\x64\Release\dosbox-x.exe" `
    -ArgumentList '-conf',"$root\src_c\build\_link.conf" -WindowStyle Minimized -Wait

if (Test-Path "$dos\link.log") { Copy-Item "$dos\link.log" "$out\link.log" -Force; Get-Content "$dos\link.log" }
if (Test-Path "$dos\CONTRAP.EXE") {
    Copy-Item "$dos\CONTRAP.EXE" "$out\CONTRAP.EXE" -Force
    if (Test-Path "$dos\CONTRAP.MAP") { Copy-Item "$dos\CONTRAP.MAP" "$out\CONTRAP.MAP" -Force }
    "EXE: src_c/out/CONTRAP.EXE  ($((Get-Item "$dos\CONTRAP.EXE").Length) byte)"
} else {
    "GAGAL: CONTRAP.EXE tidak terbentuk -- lihat link.log di atas."
    exit 1
}
