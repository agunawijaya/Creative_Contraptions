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
# ⚠⚠ URUTAN MODUL = URUTAN ALAMAT, BUKAN ABJAD.
# LINK menempatkan modul sesuai urutan pemberiannya, jadi urutan abjad
# menghasilkan .EXE yang isinya benar tapi TATA LETAKNYA acak -- cuma 6,7%
# byte cocok per posisi, dan emulator langsung keluar. Urutan yang benar
# dibaca dari manifest.txt (nama + alamat asli).
$order = @{}
Get-Content "$root\src_c\src\manifest.txt" | ForEach-Object {
    if ($_ -match '^\s*(\S+)\s+([0-9a-fA-F]+)\s+(\d+)') {
        $order[$Matches[1]] = [Convert]::ToInt32($Matches[2], 16)
    }
}
$objs = @()
$code = Get-ChildItem "$out\*.OBJ" | Where-Object {
    $n = $_.BaseName
    $n -notlike "probe*" -and $n -ne "gdata" -and $n -ne "stubs" -and $n -ne "dgalign"
} | Sort-Object @{Expression={ if ($order.ContainsKey($_.BaseName)) { $order[$_.BaseName] } else { 0x7FFF } }}, BaseName
foreach ($f in $code) { $objs += $f.BaseName }
$objs += "gdata"
# `stubs` sudah TIDAK ADA lagi (penghuni terakhirnya, `sndbuf`, ternyata ISR
# `sndisr` di keyio.asm). Tetap didukung kalau suatu saat dibutuhkan lagi.
if (Test-Path "$out\stubs.OBJ") { $objs += "stubs" }

foreach ($n in @($objs) + @("dgalign")) { Copy-Item "$out\$n.OBJ" "$dos\$n.OBJ" -Force }

# Susun masukan LINK: potong daftar objek jadi baris <=60 char, akhiri "+".
$lines = @()
# dgalign HARUS pertama: atribut PARA-nya menyelaraskan segmen DATA, dan
# kontribusi DATA-nya yang kosong di offset 0 tidak menyisipkan byte apa pun.
$cur = "dgalign+y:C"
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
    # PENJAGA: DGROUP HARUS mulai di batas paragraf. Kalau tidak, DS menunjuk ke
# paragraf di bawahnya dan SETIAP offset DGROUP meleset -- gejalanya bukan crash
# melainkan program yang "jalan lalu keluar", sangat mahal untuk didiagnosa.
# Perbaikannya: sesuaikan jumlah DB di src_c/asm/dgalign.asm.
$mapTxt = Get-Content "$out\CONTRAP.MAP"
$dataRow = $mapTxt | Where-Object { $_ -match "^\s*([0-9A-F]+)H\s+([0-9A-F]+)H\s+([0-9A-F]+)H\s+DATA\s" }
if ($dataRow -match "^\s*([0-9A-F]+)H") {
    $dataStart = [Convert]::ToInt32($Matches[1], 16)
    if ($dataStart % 16 -ne 0) {
        throw ("DGROUP mulai di 0x{0:X} -- BUKAN batas paragraf. Tambah/kurangi DB di src_c/asm/dgalign.asm sebanyak {1} byte." -f $dataStart, (16 - $dataStart % 16))
    }
    "DGROUP mulai 0x{0:X} (selaras paragraf, DS akan benar)" -f $dataStart
}

"EXE: src_c/out/CONTRAP.EXE  ($((Get-Item "$dos\CONTRAP.EXE").Length) byte)"
} else {
    "GAGAL: CONTRAP.EXE tidak terbentuk -- lihat link.log di atas."
    exit 1
}
