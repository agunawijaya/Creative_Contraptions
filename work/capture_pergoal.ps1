Add-Type -AssemblyName System.Drawing, System.Windows.Forms
$exe  = "C:\Projects\Creative_Contraptions\tools\dosbox-x\bin\x64\Release\dosbox-x.exe"
$conf = "C:\Projects\Creative_Contraptions\work\capture_all.conf"
$out  = "C:\Projects\Creative_Contraptions\work\caps_goals"
New-Item -ItemType Directory $out -Force | Out-Null
$scr = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds

function K($k,$w=1.3){ [System.Windows.Forms.SendKeys]::SendWait($k); Start-Sleep -Seconds $w }

for ($goal=1; $goal -le 6; $goal++) {
  $p = Start-Process $exe -ArgumentList "-conf `"$conf`"" -PassThru
  Start-Sleep -Seconds 10
  K "{ENTER}" 2                 # title -> main menu
  K "{DOWN}" 1                  # Fill in Mechanisms
  K "{ENTER}" 2                # WHAT IS YOUR GOAL?
  for ($d=1; $d -lt $goal; $d++){ K "{DOWN}" 0.5 }
  K "{ENTER}" 3.5             # contraption menggambar
  $bmp = New-Object System.Drawing.Bitmap $scr.Width, $scr.Height
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($scr.X, $scr.Y, 0, 0, $bmp.Size)
  $bmp.Save("$out\goal$goal.png"); $bmp.Dispose()
  Write-Output "  goal$goal captured"
  Get-Process dosbox-x -ErrorAction SilentlyContinue | Stop-Process -Force
  Start-Sleep -Seconds 2
}
Write-Output "done"
