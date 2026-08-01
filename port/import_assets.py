"""Impor aset game asli SEKALI ke bundel milik port sendiri (port/cc/data/).

Kenapa ada skrip ini
--------------------
Port HARUS mandiri: setelah bundel terbentuk, `port/main.py` tidak lagi membaca folder
game asli. Jadi folder game boleh dipindah, di-rename, atau tidak ada sama sekali —
port tetap jalan. Bundel juga TIDAK ikut ke git (lihat .gitignore): repo berisi kode,
bukan berkas game.

Aset disalin APA ADANYA (tanpa re-encode). Ini disengaja: prinsip proyek adalah
"baca aset asli", sehingga grafis setia by construction. Mengubah format akan
menambah titik gagal baru tanpa manfaat.

Pakai
-----
    python port/import_assets.py                 # cari folder game otomatis
    python port/import_assets.py <folder_game>   # tunjuk manual
    python port/import_assets.py --check         # periksa bundel, jangan salin
"""
import os
import sys
import json
import shutil
import hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLE = os.path.join(HERE, "cc", "data")

# Berkas yang BENAR-BENAR dipakai port saat runtime, beserta ukuran yang diharapkan.
# Ukuran dipakai sebagai pemeriksaan kewarasan: salinan yang salah/terpotong ketahuan
# di sini, bukan nanti sebagai sprite berantakan di layar.
NEEDED = {
    "GRAPH":   155286,   # arsip sprite objek zany
    "MECHS":     5111,   # arsip sprite mekanisme
    "ANIMATE":  14799,   # skrip VM animasi
    "CONTRAP":   2376,   # tata letak contraption per goal
    "MISC":       3398,   # potongan antarmuka tetap (corong bola, dsb.)
}

# Tempat yang ditengok kalau folder game tidak ditunjuk manual.
SEARCH = ("_ORIGINAL_READONLY", "Creative-Contraptions", "work")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(65536), b""):
            h.update(blk)
    return h.hexdigest()


def find_game_dir():
    root = os.path.abspath(os.path.join(HERE, ".."))
    for cand in SEARCH:
        d = os.path.join(root, cand)
        if all(os.path.exists(os.path.join(d, n)) for n in NEEDED):
            return d
    return None


def check_bundle(verbose=True):
    """True kalau bundel lengkap dan ukurannya benar."""
    if not os.path.isdir(BUNDLE):
        if verbose:
            print("Bundel belum ada: %s" % BUNDLE)
        return False
    ok = True
    for name, size in NEEDED.items():
        p = os.path.join(BUNDLE, name)
        if not os.path.exists(p):
            ok = False
            if verbose:
                print("  HILANG  %s" % name)
        elif os.path.getsize(p) != size:
            ok = False
            if verbose:
                print("  UKURAN SALAH  %s: %d byte (harusnya %d)"
                      % (name, os.path.getsize(p), size))
        elif verbose:
            print("  ok      %-8s %7d byte" % (name, size))
    return ok


def main(argv):
    if "--check" in argv:
        print("Memeriksa bundel aset port")
        return 0 if check_bundle() else 1

    src = None
    args = [a for a in argv if not a.startswith("--")]
    if args:
        src = os.path.abspath(args[0])
        if not all(os.path.exists(os.path.join(src, n)) for n in NEEDED):
            print("GAGAL: folder tidak memuat berkas game lengkap: %s" % src)
            print("       dibutuhkan: %s" % ", ".join(NEEDED))
            return 1
    else:
        src = find_game_dir()
        if not src:
            print("GAGAL: folder game asli tidak ditemukan otomatis.")
            print("       Tunjuk manual:  python port/import_assets.py <folder_game>")
            print("       Folder itu harus berisi: %s" % ", ".join(NEEDED))
            return 1

    print("Sumber : %s" % src)
    print("Tujuan : %s" % BUNDLE)
    os.makedirs(BUNDLE, exist_ok=True)

    manifest = {}
    for name, size in NEEDED.items():
        s = os.path.join(src, name)
        actual = os.path.getsize(s)
        if actual != size:
            print("  PERINGATAN %s: %d byte, diharapkan %d — tetap disalin, "
                  "tapi versi game mungkin berbeda." % (name, actual, size))
        d = os.path.join(BUNDLE, name)
        shutil.copyfile(s, d)
        os.chmod(d, 0o644)
        manifest[name] = dict(size=actual, sha256=sha256(d))
        print("  salin   %-8s %7d byte" % (name, actual))

    with open(os.path.join(BUNDLE, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(dict(source=src, files=manifest), f, indent=2)

    print()
    print("Bundel siap. Port sekarang MANDIRI — folder game asli boleh dipindah/dihapus.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
