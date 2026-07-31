# shapediff.py -- DIFF INSTRUKSI KASAR: beda BENTUK, bukan beda ALAMAT.
#
# Pasangan dari gapprof.py: gapprof menutup PANJANG, shapediff menutup BENTUK.
# Di `animvm` gapprof melaporkan 114 celah byte sementara shapediff cuma 7 situs
# bentuk -- dan salah satunya langsung menunjuk bug `je`/`jne`.
#
# Cara kerjanya: disassemble kedua sisi, buang SEMUA literal heksa (alamat,
# immediate, displacement) dengan satu penanda, lalu difflib atas daftar
# "mnemonic + operan-register". Yang tersisa hanya perbedaan BENTUK.
#
# ⚠ Normalisasi HARUS simetris di kedua sisi; yang asimetris melaporkan puluhan
#   beda palsu pada `call`.
# ⚠ Tabel data tertanam menggeser capstone. Pakai --stop untuk berhenti sebelum
#   tabel (animvm 0x23d4; main 0x0488/0x0511/0x10ca).
# ⚠ JANGAN membaca ISI tabel switch dari keluaran ini: wildcard slot relokasi
#   memakai offset KITA, jadi kalau tabel bergeser byte-nya mendarat salah.
#
# Membaca laporannya:
#   `insert @asli` satu `jmp` TEPAT SEBELUM tabel switch -> `default:` hilang
#   `delete`  = KITA punya `jmp` ekstra -> `break` yang seharusnya jatuh-tembus
#   beda di SEKITAR tabel -> ARTEFAK kalau tabel bergeser; perbaiki penyebab
#      geserannya dulu, baru nilai ulang
#
# Pakai: python src_c/verify/shapediff.py <nama> <addr> <ukuran> [--stop 0x23d4]
import sys, os, struct, difflib, re

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from objcode import read_omf, pick_code_segment  # noqa: E402
from capstone import Cs, CS_ARCH_X86, CS_MODE_16  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
EXE = os.path.join(ROOT, 'work', 'unpack', 'CONTRAP_UNPACKED.EXE')


def shapediff(nama, addr, size, stop=None):
    _, (code, slots) = pick_code_segment(read_omf(os.path.join(ROOT, 'src_c', 'out', nama + '.OBJ')))
    m = bytearray(code)
    raw = open(EXE, 'rb').read()
    lb = struct.unpack_from('<H', raw, 8)[0] * 16
    o = raw[lb + addr: lb + addr + size]
    for k in slots:
        if k < len(m) and k < len(o):
            m[k] = o[k]

    n = (stop - addr) if stop else min(len(m), len(o))
    md = Cs(CS_ARCH_X86, CS_MODE_16)

    def norm(buf):
        return [(i.address, i.mnemonic + ' ' + re.sub(r'0x[0-9a-f]+', 'K', i.op_str))
                for i in md.disasm(bytes(buf[:n]), addr)]

    A, B = norm(m), norm(o)
    sa, sb = [t for _, t in A], [t for _, t in B]
    sm = difflib.SequenceMatcher(None, sa, sb, autojunk=False)
    cocok = sum(k for _, _, k in sm.get_matching_blocks())
    print('%s @0x%04x%s  instruksi KITA=%d ASLI=%d  BENTUK COCOK=%d (%.1f%%)'
          % (nama, addr, ('  [berhenti di 0x%04x]' % stop) if stop else '',
             len(A), len(B), cocok, 100.0 * cocok / max(1, len(B))))
    print('   panjang byte KITA=%d ASLI=%d (%+d)' % (len(m), len(o), len(m) - len(o)))
    situs = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        situs += 1
        print('--- %s @asli 0x%04x' % (tag, B[j1][0] if j1 < len(B) else B[-1][0]))
        for k in range(i1, min(i2, i1 + 4)):
            print('   KITA 0x%04x %s' % A[k])
        for k in range(j1, min(j2, j1 + 4)):
            print('   ASLI 0x%04x %s' % B[k])
    print('   -> %d situs BENTUK' % situs)


if __name__ == '__main__':
    a = sys.argv[1:]
    stop = None
    if '--stop' in a:
        i = a.index('--stop')
        stop = int(a[i + 1], 0)
        a = a[:i] + a[i + 2:]
    shapediff(a[0], int(a[1], 16), int(a[2], 0), stop)
