Add-Type @"
using System;
using System.Runtime.InteropServices;
public class W2 {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RR r);
  [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr h, ref PP p);
  [StructLayout(LayoutKind.Sequential)] public struct RR { public int L,T,Rt,B; }
  [StructLayout(LayoutKind.Sequential)] public struct PP { public int X,Y; }
}
"@
Add-Type -AssemblyName System.Drawing, System.Windows.Forms

$OUT = "C:\Projects\Creative_Contraptions\work\shots"
if (-not (Test-Path $OUT)) { New-Item -ItemType Directory $OUT | Out-Null }

function Grab($tag) {
  $p = Get-Process dosbox-x -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $p) { Write-Output "no dosbox"; return }
  $h = $p.MainWindowHandle
  $r = New-Object W2+RR; [W2]::GetClientRect($h, [ref]$r) | Out-Null
  $pt = New-Object W2+PP; [W2]::ClientToScreen($h, [ref]$pt) | Out-Null
  $w = $r.Rt - $r.L; $ht = $r.B - $r.T
  $bmp = New-Object System.Drawing.Bitmap $w, $ht
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($pt.X, $pt.Y, 0, 0, $bmp.Size)
  $bmp.Save("$OUT\$tag.png")
  $bmp.Dispose()
  Write-Output "  -> $tag.png (${w}x${ht})"
}

function Key($k) {
  $p = Get-Process dosbox-x | Select-Object -First 1
  [W2]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
  Start-Sleep -Milliseconds 400
  [System.Windows.Forms.SendKeys]::SendWait($k)
  Start-Sleep -Seconds 2
}

Grab "00_title"
foreach ($i in 1..6) {
  Key "{ENTER}"
  Grab ("{0:d2}_enter" -f $i)
}
