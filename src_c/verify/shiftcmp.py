# shiftcmp.py -- ukur fungsi yang masih punya SATU geseran, di KEDUA sisinya.
#
# Masalah yang dipecahkan: selama satu situs menyisakan selisih panjang, seluruh
# bagian sesudahnya salah sejajar. GLOBAL lalu MENGHUKUM perbaikan yang benar
# (pickvar: perbaikan yang betul membuat GLOBAL turun 1.662 -> 1.628 padahal
# byte cocoknya naik) -- dan lebih buruk lagi, wildcard slot relokasi memakai
# offset KITA sehingga mendarat di byte yang salah.
#
# Alat ini memotong fungsi di titik geseran: bagian SEBELUM dibandingkan apa
# adanya, bagian SESUDAH dibandingkan dengan kompensasi geseran. Dua angka yang
# dihasilkan dua-duanya bersih.
#
# Pakai:
#   python src_c/verify/shiftcmp.py <nama> <addr> <ukuran> <titik-geser> <geseran>
#
#   <titik-geser> alamat tempat `aligncmp` melaporkan geseran (mis. 4515)
#   <geseran>     panjang KITA dikurangi ASLI di titik itu (mis. +2)
#
# Contoh: python src_c/verify/shiftcmp.py pickvar 42ca 1730 4515 +2
#
# ⚠ Hanya sah kalau geserannya TUNGGAL. Kalau `aligncmp` melaporkan lebih dari
#   satu, perbaiki dulu sampai tersisa satu -- kalau tidak, sisi "ekor" pun
#   masih tercemar.
import sys
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from objcode import read_omf, pick_code_segment  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
EXE = os.path.join(ROOT, 'work', 'unpack', 'CONTRAP_UNPACKED.EXE')


def main(nama, addr, size, cut, sh):
    raw = open(EXE, 'rb').read()
    lb = struct.unpack_from('<H', raw, 8)[0] * 16
    o = raw[lb + addr: lb + addr + size]
    _, (code, slots) = pick_code_segment(
        read_omf(os.path.join(ROOT, 'src_c', 'out', nama + '.OBJ')))
    m = bytearray(code)
    S = set(slots)
    s = cut - addr

    pn = sum(1 for i in range(min(s, len(m)))
             if (o[i] if i in S else m[i]) == o[i])
    ekor = []
    for i in range(s + sh, len(m)):
        ekor.append(o[i - sh] if (i in S and 0 <= i - sh < len(o)) else m[i])
    B = o[s:]
    n = min(len(ekor), len(B))
    tn = sum(1 for i in range(n) if ekor[i] == B[i])
    beda = ['%04x: kita %02x asli %02x' % (addr + s + i, ekor[i], B[i])
            for i in range(n) if ekor[i] != B[i]]

    print('%s @0x%04x  geseran %+d di 0x%04x' % (nama, addr, sh, cut))
    print('   prefiks 0x%04x..0x%04x : %d / %d cocok' % (addr, cut, pn, s))
    print('   ekor    0x%04x..akhir  : %d / %d cocok (dikompensasi)' % (cut, tn, n))
    print('   SETARA                 : %d / %d byte  (%.1f%%)'
          % (pn + tn, s + n, 100.0 * (pn + tn) / max(1, s + n)))
    if beda:
        print('   beda di ekor (%d):' % len(beda))
        for b in beda[:20]:
            print('     ' + b)


if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], int(a[1], 16), int(a[2], 0), int(a[3], 16), int(a[4], 0))
