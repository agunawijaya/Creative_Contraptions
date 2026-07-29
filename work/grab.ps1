Add-Type @"
using System;
using System.Runtime.InteropServices;
public class W4 {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RR r);
  [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr h, ref PP p);
  [StructLayout(LayoutKind.Sequential)] public struct RR { public int L,T,Rt,B; }
  [StructLayout(LayoutKind.Sequential)] public struct PP { public int X,Y; }
}
"@
Add-Type -AssemblyName System.Drawing, System.Windows.Forms
$OUT = "C:\Projects\Creative_Contraptions\work\shots"
function Grab($tag) {
  $p = Get-Process dosbox-x -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $p) { return }
  $h = $p.MainWindowHandle
  $r = New-Object W4+RR; [W4]::GetClientRect($h, [ref]$r) | Out-Null
  $pt = New-Object W4+PP; [W4]::ClientToScreen($h, [ref]$pt) | Out-Null
  $w = $r.Rt - $r.L; $ht = $r.B - $r.T
  $bmp = New-Object System.Drawing.Bitmap $w, $ht
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($pt.X, $pt.Y, 0, 0, $bmp.Size)
  $game = New-Object System.Drawing.Bitmap 322, 210
  $g2 = [System.Drawing.Graphics]::FromImage($game)
  $g2.DrawImage($bmp, (New-Object System.Drawing.Rectangle 0,0,322,210), (New-Object System.Drawing.Rectangle ($w-322),($ht-210),322,210), [System.Drawing.GraphicsUnit]::Pixel)
  $big = New-Object System.Drawing.Bitmap 966, 630
  $g3 = [System.Drawing.Graphics]::FromImage($big)
  $g3.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
  $g3.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
  $g3.DrawImage($game, 0, 0, 966, 630)
  $big.Save("$OUT\$tag.png")
  $bmp.Dispose(); $game.Dispose(); $big.Dispose()
  Write-Output "  -> $tag.png"
}
function Key($k, $wait=2) {
  $p = Get-Process dosbox-x | Select-Object -First 1
  [W4]::SetForegroundWindow($p.MainWindowHandle) | Out-Null
  Start-Sleep -Milliseconds 400
  [System.Windows.Forms.SendKeys]::SendWait($k)
  Start-Sleep -Seconds $wait
}
Grab "20_contraption"
Key "{RIGHT}" 2
Grab "21_review"
Key "{RIGHT}" 2
Grab "22_review"
Key " " 4
Grab "23_run"
