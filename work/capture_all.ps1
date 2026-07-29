Add-Type -AssemblyName System.Drawing, System.Windows.Forms
$exe  = "C:\Projects\Creative_Contraptions\tools\dosbox-x\bin\x64\Release\dosbox-x.exe"
$conf = "C:\Projects\Creative_Contraptions\work\capture_all.conf"
$out  = "C:\Projects\Creative_Contraptions\work\caps_goals"
New-Item -ItemType Directory $out -Force | Out-Null

$scr = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$p = Start-Process $exe -ArgumentList "-conf `"$conf`"" -PassThru
Start-Sleep -Seconds 10

function K($k,$w=1.5){ [System.Windows.Forms.SendKeys]::SendWait($k); Start-Sleep -Seconds $w }
function Grab($name){
  $bmp = New-Object System.Drawing.Bitmap $scr.Width, $scr.Height
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($scr.X, $scr.Y, 0, 0, $bmp.Size)
  $bmp.Save("$out\$name.png"); $bmp.Dispose()
  Write-Output "  saved $name.png ($($scr.Width)x$($scr.Height))"
}

K "{ENTER}" 2                 # title -> main menu
for ($goal=1; $goal -le 6; $goal++) {
  K "{DOWN}" 1               # Fill in Mechanisms
  K "{ENTER}" 2             # WHAT IS YOUR GOAL?
  for ($d=1; $d -lt $goal; $d++){ K "{DOWN}" 0.5 }
  K "{ENTER}" 3            # contraption
  Grab ("goal{0}" -f $goal)
  K "{ESC}" 1; K "{ESC}" 1
}
Start-Sleep -Seconds 1
Get-Process dosbox-x -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Output "done"
