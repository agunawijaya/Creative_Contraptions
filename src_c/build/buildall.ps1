# Kompilasi SEMUA src_c/src/*.c dalam SATU sesi DOSBox.
#
# Kenapa: tiap peluncuran DOSBox makan beberapa detik. Untuk 60 fungsi, satu
# peluncuran per berkas jadi hambatan utama. Di sini seluruh berkas dikompilasi
# dalam satu [autoexec].
#
#   pwsh src_c/build/buildall.ps1
#   pwsh src_c/build/buildall.ps1 -Only goalmenu,delay
param([string[]]$Only)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path "$PSScriptRoot\..\..").Path
$dos  = "$root\src_c\build\dos"
$bin  = "$root\tools\msc104\bin"
$out  = "$root\src_c\out"
New-Item -ItemType Directory -Force -Path $dos, $out | Out-Null

$files = Get-ChildItem "$root\src_c\src\*.c" | Where-Object {
    $n = $_.BaseName
    (-not $Only -or $Only -contains $n) -and $n.Length -le 8
}
if (-not $files) { throw "Tidak ada berkas .c yang cocok." }

foreach ($f in $files) { Copy-Item $f.FullName "$dos\$($f.BaseName).C" -Force }
Get-ChildItem "$dos\*.OBJ","$dos\build.log" -ErrorAction SilentlyContinue | Remove-Item -Force

$lines = @("mount x ""$dos""", "mount y ""$bin""", "x:")
foreach ($f in $files) {
    $n = $f.BaseName
    $lines += "echo === $n === >> x:\build.log"
    $lines += "y:\MC1 $n >> x:\build.log"
    $lines += "y:\MC2 $n >> x:\build.log"
}
$lines += "exit"

$conf = "[dosbox]`nmachine=cga`n[cpu]`ncputype=386`ncycles=fixed 30000`n[autoexec]`n" + ($lines -join "`n")
Set-Content "$root\src_c\build\_all.conf" -Value $conf -Encoding ASCII
Start-Process "$root\tools\dosbox-x\bin\x64\Release\dosbox-x.exe" `
    -ArgumentList '-conf',"$root\src_c\build\_all.conf" -WindowStyle Minimized -Wait

if (Test-Path "$dos\build.log") { Copy-Item "$dos\build.log" "$out\build.log" -Force }
$ok = 0
foreach ($f in $files) {
    $n = $f.BaseName
    if (Test-Path "$dos\$n.OBJ") { Copy-Item "$dos\$n.OBJ" "$out\$n.OBJ" -Force; $ok++ }
    else { Write-Host "GAGAL kompilasi: $n" }
}
"terkompilasi $ok/$($files.Count)"
$errs = Select-String -Path "$out\build.log" -Pattern "Error|Warning" -ErrorAction SilentlyContinue
if ($errs) { "--- pesan kompiler ---"; $errs | ForEach-Object { "  " + $_.Line } }
