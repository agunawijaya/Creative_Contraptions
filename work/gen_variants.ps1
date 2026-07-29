$counts = @{ 1 = 2; 2 = 1; 3 = 2; 4 = 2; 5 = 1; 6 = 2; 7 = 9 }
foreach ($g in 1..7) {
    for ($v = 0; $v -lt $counts[$g]; $v++) {
        $env:VARIANT = "$v"
        $out = python work/emu.py $g 2 2>&1 | Select-String -Pattern "SCENE static"
        Write-Host "goal $g var $v : $out"
    }
}
$env:VARIANT = $null
