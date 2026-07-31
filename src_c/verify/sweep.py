# sweep.py -- ORACLE BATCH: banyak varian C -> SATU peluncuran DOSBox -> laporan.
#
# Sebelum ini tiap varian butuh peluncuran DOSBox sendiri (~8 detik), jadi probe
# 5 varian = satu iterasi penuh. DOSBox bisa menjalankan puluhan perintah dalam
# satu [autoexec]; harness ini memakai itu. 24 varian sekali jalan.
#
# Pakai:
#   python src_c/verify/sweep.py <dir-varian> [--pola REGEX]
#
# <dir-varian> berisi V01.C, V02.C, ... (nama WAJIB 8.3, DOS tidak kenal nama
# panjang). Tiap berkas dikompilasi MC1+MC2 lalu dibongkar; keluarannya tabel
# "varian -> panjang kode + baris yang cocok --pola".
#
# ⚠ MC1 juga meninggalkan <nama>.Q -- berkas QUAD, satu-satunya masukan MC2.
#   Dua varian dengan Q identik TIDAK MUNGKIN menghasilkan kode berbeda; itu
#   bukti langsung bahwa pertanyaannya salah tingkat (aturan (t)). Kolom `qhash`
#   melaporkannya.
# ⚠ HAPUS .OBJ dulu; varian yang gagal kompilasi dilaporkan GAGAL, bukan diam.
import sys
import os
import re
import glob
import hashlib
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
DOS = os.path.join(ROOT, 'src_c', 'build', 'dos')
BIN = os.path.join(ROOT, 'tools', 'msc104', 'bin')
DBX = os.path.join(ROOT, 'tools', 'dosbox-x', 'bin', 'x64', 'Release', 'dosbox-x.exe')


def run(names):
    lines = ['[dosbox]', 'machine=cga', '[cpu]', 'cputype=386',
             'cycles=fixed 30000', '[autoexec]',
             'mount x "%s"' % DOS, 'mount y "%s"' % BIN, 'x:']
    lines.append('y:\\MC1 %s > x:\\sweep.log' % names[0])
    lines.append('y:\\MC2 %s >> x:\\sweep.log' % names[0])
    for n in names[1:]:
        lines.append('y:\\MC1 %s >> x:\\sweep.log' % n)
        lines.append('y:\\MC2 %s >> x:\\sweep.log' % n)
    lines.append('exit')
    conf = os.path.join(DOS, '_sweep.conf')
    open(conf, 'w').write('\n'.join(lines) + '\n')
    subprocess.run([DBX, '-conf', conf, '-fastlaunch', '-exit'],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def globalmatch(code, slots, addr, size):
    """Metrik GLOBAL yang sama dengan aligncmp: difflib atas byte, slot
    relokasi di-wildcard. Dipakai supaya varian berkas SUNGGUHAN bisa diukur
    langsung -- reproduksi mini sering tidak setia karena tekanan register
    di fungsi aslinya tidak ikut tereproduksi."""
    import difflib
    import struct
    raw = open(os.path.join(ROOT, 'work', 'unpack', 'CONTRAP_UNPACKED.EXE'), 'rb').read()
    lb = struct.unpack_from('<H', raw, 8)[0] * 16
    o = raw[lb + addr: lb + addr + size]
    m = bytearray(code)
    for k in slots:
        if k < len(m) and k < len(o):
            m[k] = o[k]
    sm = difflib.SequenceMatcher(None, bytes(m), o, autojunk=False)
    return sum(k for _, _, k in sm.get_matching_blocks()), len(m)


def main(d, pola, cmp_at=None):
    from objcode import read_omf, pick_code_segment
    from capstone import Cs, CS_ARCH_X86, CS_MODE_16

    srcs = sorted(glob.glob(os.path.join(d, '*.[cC]')))
    if not srcs:
        sys.exit('tidak ada *.c di %s' % d)
    names = []
    for s in srcs:
        n = os.path.splitext(os.path.basename(s))[0].upper()
        if len(n) > 8:
            sys.exit('nama %s > 8 karakter -- DOS tidak akan mengenalinya' % n)
        open(os.path.join(DOS, n + '.C'), 'wb').write(open(s, 'rb').read())
        for e in ('.OBJ', '.Q'):
            try:
                os.remove(os.path.join(DOS, n + e))
            except OSError:
                pass
        names.append(n)

    run(names)

    rx = re.compile(pola) if pola else None
    md = Cs(CS_ARCH_X86, CS_MODE_16)
    qh = {}
    for n in names:
        o = os.path.join(DOS, n + '.OBJ')
        q = os.path.join(DOS, n + '.Q')
        if not os.path.exists(o):
            print('%-8s GAGAL KOMPILASI' % n)
            continue
        # ⚠ MC2 MENGHAPUS .Q setelah membacanya, jadi kolom ini hanya terisi
        #   kalau sweep dijalankan tanpa MC2. Tanpa penjaga ini semua varian
        #   dilaporkan "quad SAMA" (hash kosong) -- bukti palsu yang meyakinkan.
        h = hashlib.sha1(open(q, 'rb').read()).hexdigest()[:8] if os.path.exists(q) else None
        sama = qh.setdefault(h, n) if h else n
        _, (code, slots) = pick_code_segment(read_omf(o))
        tag = '' if sama == n else '  quad SAMA dgn %s' % sama
        h = h or '(dihapus MC2)'
        if cmp_at:
            addr, size = cmp_at
            g, ln = globalmatch(code, slots, addr, size)
            print('%-8s %4d byte (%+d)  GLOBAL %d/%d (%.1f%%)%s'
                  % (n, ln, ln - size, g, size, 100.0 * g / size, tag))
        else:
            print('%-8s %4d byte  quad=%s%s' % (n, len(code), h, tag))
        if rx:
            for i in md.disasm(bytes(code), 0):
                t = '%s %s' % (i.mnemonic, i.op_str)
                if rx.search(t):
                    print('           %04x  %s' % (i.address, t))


if __name__ == '__main__':
    a = sys.argv[1:]
    p = None
    c = None
    if '--pola' in a:
        i = a.index('--pola')
        p = a[i + 1]
        a = a[:i] + a[i + 2:]
    if '--cmp' in a:
        i = a.index('--cmp')
        c = (int(a[i + 1], 16), int(a[i + 2], 0))
        a = a[:i] + a[i + 3:]
    main(a[0], p, c)
