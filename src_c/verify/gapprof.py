# gapprof.py -- PROFIL CELAH: "kurang DITULIS" atau "murni REGISTER"?
#
# Memakai difflib yang SAMA dengan metrik GLOBAL di aligncmp.py, supaya hasilnya
# dijamin konsisten. JANGAN menulis model "geseran kumulatif" sendiri -- sudah
# TIGA alat ad-hoc yang salah (metrik serakah, fixorder, peta kepadatan/128B).
#
# Cara baca:
#   celah TERBESAR >= 20 B   -> masih ada STRUKTUR yang belum ditulis; garap volumenya
#   rata-rata celah 1-2 B    -> kelas ALOKASI REGISTER; jangan diperlakukan sbg volume
#
# Pakai:  python src_c/verify/gapprof.py <nama> <addr> <ukuran>
#         python src_c/verify/gapprof.py --semua
import sys, os, struct, difflib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from objcode import read_omf, pick_code_segment  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
EXE = os.path.join(ROOT, 'work', 'unpack', 'CONTRAP_UNPACKED.EXE')
OUT = os.path.join(ROOT, 'src_c', 'out')


def profil(nama, addr, size, top=10):
    obj = os.path.join(OUT, nama + '.OBJ')
    if not os.path.exists(obj):
        print('%-9s  (tidak ada %s.OBJ)' % (nama, nama))
        return
    _, (code, slots) = pick_code_segment(read_omf(obj))
    m = bytearray(code)
    raw = open(EXE, 'rb').read()
    lb = struct.unpack_from('<H', raw, 8)[0] * 16
    o = raw[lb + addr: lb + addr + size]
    # slot relokasi = wildcard
    for k in slots:
        if k < len(m) and k < len(o):
            m[k] = o[k]

    sm = difflib.SequenceMatcher(None, bytes(m), bytes(o), autojunk=False)
    cocok = sum(n for _, _, n in sm.get_matching_blocks())
    gaps, pb = [], 0
    for _i, j, n in sm.get_matching_blocks():
        if j > pb:
            gaps.append((pb, j - pb))
        pb = j + n

    tot = sum(g[1] for g in gaps)
    rata = (tot / len(gaps)) if gaps else 0.0
    besar = max((g[1] for g in gaps), default=0)
    kelas = 'VOLUME (struktur belum ditulis)' if besar >= 20 else 'REGISTER (struktur lengkap)'
    print('%-9s @0x%04x  GLOBAL %d/%d (%.1f%%)' % (nama, addr, cocok, size, 100.0 * cocok / size))
    print('   celah: %d byte dalam %d celah | terbesar %d B | rata-rata %.1f B  -> %s'
          % (tot, len(gaps), besar, rata, kelas))
    if gaps:
        urut = sorted(gaps, key=lambda g: -g[1])[:top]
        print('   TERBESAR: ' + ', '.join('0x%04x=%dB' % (addr + a, n) for a, n in urut))


SEMUA = [
    ('nvar', 0x4094, 566), ('animvm', 0x18db, 3040), ('pickvar', 0x42ca, 1730),
    ('loadcon', 0x5035, 739), ('place', 0x4e3e, 503), ('f498c', 0x498c, 165),
    ('main_', 0x0082, 4219),
]

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == '--semua':
        for n, ad, sz in SEMUA:
            profil(n, ad, sz)
    else:
        profil(a[0], int(a[1], 16), int(a[2], 0))
