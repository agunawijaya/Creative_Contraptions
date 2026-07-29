$counts = @{ 1 = 2; 2 = 1; 3 = 2; 4 = 2; 5 = 1; 6 = 2; 7 = 9 }
$dst = "port/cc/draws"
$cap = "work/emu_caps"
foreach ($g in 1..7) {
    for ($v = 0; $v -lt $counts[$g]; $v++) {
        $target = "$dst/draws_goal${g}_v${v}.json"
        if ($v -eq 0 -and (Test-Path "$dst/draws_goal${g}.json")) {
            Copy-Item "$dst/draws_goal${g}.json" $target -Force   # v0 = referensi terverifikasi
        } else {
            Copy-Item "$cap/draws_goal${g}_v${v}.json" $target -Force  # v1+ = tangkapan emulator
        }
    }
}
Write-Host "installed:" (Get-ChildItem "$dst/draws_goal*_v*.json").Count "variant files"
