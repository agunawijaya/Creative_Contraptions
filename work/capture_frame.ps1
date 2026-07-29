Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WC {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
}
"@
Add-Type -AssemblyName System.Windows.Forms

$caps = "C:\Projects\Creative_Contraptions\work\caps"
if (Test-Path $caps) { Remove-Item "$caps\*" -Force -ErrorAction SilentlyContinue }
else { New-Item -ItemType Directory $caps | Out-Null }

$exe = "C:\Projects\Creative_Contraptions\tools\dosbox-x\bin\x64\Release\dosbox-x.exe"
$conf = "C:\Projects\Creative_Contraptions\work\dosbox_cap.conf"
$p = Start-Process $exe -ArgumentList "-conf `"$conf`"" -PassThru
Start-Sleep -Seconds 7

function Foc { [WC]::SetForegroundWindow((Get-Process dosbox-x | Select-Object -First 1).MainWindowHandle) | Out-Null; Start-Sleep -Milliseconds 300 }
function K($k,$w=2){ Foc; [System.Windows.Forms.SendKeys]::SendWait($k); Start-Sleep -Seconds $w }

# Navigasi: title -> main menu -> Contraption Mix Up -> Apprentice -> instruksi -> contraption
K "{ENTER}" 2       # title -> main menu
K "{DOWN}" 1
K "{DOWN}" 1
K "{DOWN}" 1        # sorot "Play Contraption Mix Up"
K "{ENTER}" 2       # -> WHAT LEVEL
K "{ENTER}" 2       # pilih Apprentice -> layar instruksi
K "{ENTER}" 5       # -> contraption menggambar, tunggu penuh

# Screenshot mentah DOSBox-X (native 320x200). Coba beberapa shortcut umum.
Foc; [System.Windows.Forms.SendKeys]::SendWait("^{F5}"); Start-Sleep -Seconds 1
Foc; [System.Windows.Forms.SendKeys]::SendWait("{F5}"); Start-Sleep -Seconds 1

Start-Sleep -Seconds 1
Write-Output "File di caps:"
Get-ChildItem $caps -File -ErrorAction SilentlyContinue | Select-Object Name, Length | Format-Table -AutoSize
