"""REGRESI SUARA: nada yang benar-benar dikirim gim ke PC-speaker.

Sampai sekarang `cc/core/bunyi.py` hanya diuji terhadap FORMATNYA sendiri
(`test_bunyi.py`): 3 byte per not, `u16` frekuensi + `u8` durasi, `FFFF`
sebagai penutup. Itu tidak membuktikan tafsirnya benar -- angka yang sama bisa
saja PEMBAGI PIT, bukan frekuensi, dan hasilnya akan terdengar sangat berbeda.

Uji ini mengukurnya dari sisi perangkat keras. Dua saklar emulator dibutuhkan,
dan keduanya menutup lubang di harness -- bukan di gim:

  CC_SNDISR=1  Bunyi gim TIDAK digerakkan gelung utama melainkan penangan
               INT 1Ch yang dipasang `sndsave(sndisr)`. Emulator tidak
               menjalankan interupsi timer, jadi ISR itu tak pernah jalan dan
               port speaker tetap SUNYI berapa lama pun dijalankan. Saklar ini
               memanggil `sndisr` @0x670E sendiri dari `vbwait` (sekali per
               bingkai): dorong FLAGS/CS/IP seperti interupsi asli, lompat ke
               ISR, dan `IRET` di ujungnya kembali sendiri.
  CC_TRACEIO=1 Rekam penulisan ke port 0x42/0x43/0x61.

`snd2.asm` menghitung `0x1234DE / CX` lalu menulis hasilnya ke pembagi PIT
kanal 2. Jadi frekuensi yang benar-benar terdengar = 1.193.182 / pembagi, dan
itulah yang diadu dgn hasil dekode port.

⭐ Kalau angka skrip ternyata PEMBAGI dan bukan frekuensi, uji ini gagal keras:
500 Hz akan muncul sebagai 2.386 Hz.
"""
import os
import re
import subprocess
import sys

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AKAR, "port"))

from cc.core import dgtab, bunyi                               # noqa: E402

ALIRAN = 0x978              # `sndptr = 0x978; sndmode = 2;` di animvm()
gagal = []


def cek(nama, dapat, harap):
    ok = dapat == harap
    if not ok:
        gagal.append(nama)
    print("  %-38s %s" % (nama, "OK" if ok else "GAGAL\n     dapat %s\n     harap %s"
                          % (dapat, harap)))


def dari_gim():
    env = dict(os.environ)
    env.update(CC_OUT=os.path.join(AKAR, "work", "suaraseq"),
               CC_TRACEIO="1", CC_SNDISR="1", CC_MAXINSN="400000000")
    r = subprocess.run([sys.executable, os.path.join(AKAR, "work", "emu.py"),
                        "1", "1"], env=env, cwd=AKAR,
                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                       timeout=600)
    keluar = r.stdout.decode("latin-1", "replace")
    m = re.search(r"-> frekuensi Hz: \[([^\]]*)\]", keluar)
    if not m:
        return None
    return [int(x) for x in m.group(1).split(",") if x.strip()]


def main():
    notes, ulang = bunyi.not_dari(2, bytes(dgtab.dgroup()[ALIRAN:ALIRAN + 60]))
    port = [f for f, _t in notes]
    print("  port  : %d not, %s ..." % (len(port), port[:8]))
    gim = dari_gim()
    if gim is None:
        print("  emulator tidak menghasilkan penulisan port speaker")
        return 1
    print("  gim   : %d nada terekam, %s ..." % (len(gim), gim[:8]))

    n = min(len(gim), len(port))
    cek("frekuensi cocok dgn PIT gim (%d nada)" % n, port[:n], gim[:n])
    cek("angka skrip = FREKUENSI, bukan pembagi",
        all(f == 0 or 30 < f < 5000 for f in port), True)
    cek("aliran mode 2 tidak berulang", ulang, False)

    print("\n%s" % ("SUARA COCOK DENGAN GIM" if not gagal
                    else "GAGAL: %s" % ", ".join(gagal)))
    return 1 if gagal else 0


sys.exit(main())
