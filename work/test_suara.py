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
import json
import os
import re
import struct
import subprocess
import sys

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(AKAR, "port"))

from cc.core import dgtab, bunyi                               # noqa: E402

ALIRAN = 0x978              # `sndptr = 0x978; sndmode = 2;` di animvm()

# Sapuan MODE 1. `animvm()` memasangnya tepat sesudah gelung jam pasir:
#     snd[0] = 0x1f4; snd[1] = 0x5b4; snd[2] = 0x10; sndmode = 1;
# yaitu bunyi bilah bola yang meluncur.
#
# Penguraian mode 1 di `bunyi.py` selama ini bertanda "Ditafsirkan (awal,
# akhir, langkah)" -- tafsiran, bukan pengukuran. Uji ini mengukurnya.
SAPUAN = (0x1f4, 0x5b4, 0x10)
gagal = []


def deret_sapuan(freqs, langkah):
    """-> deret terpanjang di `freqs` yang naik tepat `langkah` tiap nada."""
    terbaik = []
    i = 0
    while i < len(freqs):
        j = i
        while j + 1 < len(freqs) and freqs[j + 1] - freqs[j] == langkah:
            j += 1
        if j - i + 1 > len(terbaik):
            terbaik = freqs[i:j + 1]
        i = max(j, i) + 1
    return terbaik


def cek(nama, dapat, harap):
    ok = dapat == harap
    if not ok:
        gagal.append(nama)
    print("  %-38s %s" % (nama, "OK" if ok else "GAGAL\n     dapat %s\n     harap %s"
                          % (dapat, harap)))


def dari_gim():
    """-> daftar PENUH frekuensi yang gim tulis ke PIT.

    ⚠ Dibaca dari berkas `pit_hz.json`, BUKAN dari cetakan emulator. Cetakan
    itu dipotong 16 nada supaya terbaca manusia, dan uji ini dulu mengurainya
    -- jadi ia "mengukur" 16 nada pertama saja dan sapuan mode 1, yang datang
    jauh di belakang, tak pernah terlihat sama sekali. Alat ukur yang
    membatasi temuannya sendiri.
    """
    keluaran = os.path.join(AKAR, "work", "suaraseq")
    env = dict(os.environ)
    env.update(CC_OUT=keluaran,
               CC_TRACEIO="1", CC_SNDISR="1", CC_MAXINSN="900000000")
    r = subprocess.run([sys.executable, os.path.join(AKAR, "work", "emu.py"),
                        "1", "1"], env=env, cwd=AKAR,
                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                       timeout=900)
    penuh = os.path.join(keluaran, "pit_hz.json")
    if os.path.exists(penuh):
        return json.load(open(penuh))
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

    # ── Sapuan MODE 1 ───────────────────────────────────────────────────
    sap_port = [f for f, _t in bunyi.not_dari(1, struct.pack("<HHH", *SAPUAN))[0]]
    sap_gim = deret_sapuan(gim, SAPUAN[2])
    print("  sapuan: port %d nada %s..%s | gim %d nada %s..%s"
          % (len(sap_port), sap_port[0] if sap_port else "-",
             sap_port[-1] if sap_port else "-",
             len(sap_gim), sap_gim[0] if sap_gim else "-",
             sap_gim[-1] if sap_gim else "-"))
    # ⚠ PANJANGNYA tidak dibandingkan, dan itu bukan kelonggaran: mode 1 maju
    # satu langkah per tik ISR sampai program memanggil `sndoff()`, jadi
    # jumlah nada ditentukan LAMA BUNYINYA MENYALA, bukan datanya. Yang
    # ditentukan data -- dan itulah yang diuji -- adalah nada AWAL, LANGKAH,
    # dan seluruh nilai yang benar-benar terdengar.
    cek("sapuan gim = awalan deret port (%d nada)" % len(sap_gim),
        sap_port[:len(sap_gim)], sap_gim)
    cek("sapuan mode 1 dimulai dari nilai skrip", sap_gim[:1], [SAPUAN[0]])
    cek("langkah sapuan sesuai skrip",
        sorted({b - a for a, b in zip(sap_gim, sap_gim[1:])}), [SAPUAN[2]])

    print("\n%s" % ("SUARA COCOK DENGAN GIM" if not gagal
                    else "GAGAL: %s" % ", ".join(gagal)))
    return 1 if gagal else 0


sys.exit(main())
