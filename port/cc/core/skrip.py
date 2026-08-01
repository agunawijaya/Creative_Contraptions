"""Skrip animasi part — menemukannya di ANIMATE, tanpa tangkapan emulator.

Sampai sekarang port membaca skrip dari `work/emu_caps/scripts_goalN.json`,
yaitu hasil MENJALANKAN game. Modul ini menggantinya: skrip diambil langsung
dari berkas aset, jadi port tidak lagi bergantung pada rekaman.

⭐ ATURAN PENCARIANNYA — dan ini yang mudah salah:

    Skrip sebuah part dicari lewat pasangan (id, row) dari record GAMBAR yang
    terpilih, BUKAN lewat indeks slot dan BUKAN lewat indeks di tabel hasil
    `loadarc()`.

Memakai indeks tabel kelihatan masuk akal (loadarc menyaring ANIMATE dengan
jenis yang sama, jadi tabelnya "sejajar") dan memberi hasil untuk slot pertama.
Ia meleset mulai slot kedua: tabel ANIMATE punya jumlah record berbeda per
jenis, jadi kesejajarannya cuma kebetulan di awal.

Diperiksa: untuk goal 1 varian 0, pencarian lewat (id, row) memberi 10 dari 10
skrip dengan panjang yang PERSIS sama dengan yang dilaporkan emulator
(zany 107, 217, 60, 51, 18, 229, 1; mech 31, 45, 19). Lewat indeks tabel, hanya
slot pertama yang benar.

⚠ Nama berkasnya menyesatkan: ANIMATE berisi SKRIP (arus opcode), bukan frame
gambar. Frame animasi ada di GRAPH/MECHS sebagai record yang berbagi (id, row)
dengan record diamnya -- lihat `Archive.kelompok()`.
"""


def cari(rec, animate):
    """Record ANIMATE untuk sebuah record gambar (GRAPH/MECHS). None kalau tak ada.

    `rec` = record gambar yang TERPILIH untuk slot itu (hasil pickpart/fillans).
    """
    for a in animate.recs:
        if a["id"] == rec["id"] and a["row"] == rec["row"]:
            return a
    return None


def byte(rec, animate):
    """Arus opcode mentah untuk sebuah record gambar. b"" kalau tak ada skrip."""
    a = cari(rec, animate)
    if a is None:
        return b""
    return animate.raw[a["off"]:a["off"] + a["ln"]]


def muat(rec, animate):
    """-> (daftar simpul opcode, panjang terbaca). Kosong kalau tak ada skrip.

    Parser opcode-nya dipakai BERSAMA dengan `cc/animvm.py` yang sudah
    tervalidasi (interpolator 2823 eksak 42/42); jangan tulis ulang di sini.
    """
    s = byte(rec, animate)
    if not s:
        return [], 0
    from .. import animvm
    return animvm.parse(s)
