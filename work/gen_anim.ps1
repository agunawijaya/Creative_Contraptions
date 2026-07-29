$counts = @{ 1 = 2; 2 = 1; 3 = 2; 4 = 2; 5 = 1; 6 = 2 }
$env:VCAP = "1"
foreach ($g in 1..6) {
    for ($v = 0; $v -lt $counts[$g]; $v++) {
        $env:VARIANT = "$v"
        $out = python work/emu.py $g 2 2>&1 | Select-String -Pattern "BALL SCREEN"
        Write-Host "goal $g var $v : $out"
    }
}
$env:VCAP = $null
$env:VARIANT = $null
