; dgalign.asm -- modul KOSONG. Tugasnya cuma satu: memberi atribut PARA pada
; segmen DATA supaya LINK memadatkan PROG sampai batas paragraf, sehingga DGROUP
; mulai di batas PARAGRAF.
;
; KENAPA PERLU. DGROUP mulai tepat sesudah PROG. Kalau panjang PROG bukan
; kelipatan 16, LINK menaruh DATA di alamat yang tidak selaras paragraf, dan
; register DS menunjuk ke paragraf DI BAWAHNYA -- sehingga SETIAP offset DGROUP
; meleset sebesar sisa pembagiannya.
;
; Gejalanya di biner kita (2026-08-01, sebelum modul ini ada):
;   PROG berakhir 0x9064 (bukan 0x9070)  ->  DATA mulai 0x9064
;   DS = 0x0A16 (asli 0x0A17), tiap offset DGROUP MELESET +4
;   akibatnya `open("misc")` membaca string yang salah, XCFINT mengambil cabang
;   berbeda, dan program keluar tanpa menggambar apa pun.
; Biner ASLI memang punya 14 byte NOL di 0x9062..0x9070 -- itu padding yang sama.
;
; ⚠ TIGA CARA LAIN SUDAH DICOBA & GAGAL:
;   1. `PROG SEGMENT PARA` -- menyelaraskan AWAL segmen PROG (jadi 0x10, bukan
;      0x0E) dan menggeser SELURUH kode 2 byte. Bukan padding di ujung.
;   2. `DATA SEGMENT PARA` di SEMUA modul .asm -- DATA memang jadi 0x9070, TAPI
;      kontribusi DATA tiap modul ikut diselaraskan, sehingga 12 byte pengisi
;      disisipkan SEBELUM gdata dan seluruh DGROUP bergeser +12.
;   3. `DB 12 DUP(0)` di segmen PROG modul ini -- modul PUSTAKA di-link SESUDAH
;      semua objek kita, jadi 12 byte itu mendorong seluruh kode MC.LIB +12
;      (_main pindah 0x70e8 -> 0x70f4). Padding harus datang dari LINK, bukan
;      dari modul.
;
; ⚠ Modul ini WAJIB di-link PALING AWAL (sebelum C.OBJ). Lihat link.ps1.

        NAME    dgalign

PGROUP  GROUP   PROG
DGROUP  GROUP   DATA

; ⚠ Yang dideklarasikan DULU harus BASE, bukan PROG. Urutan kemunculan segmen
;   di modul PERTAMA menentukan urutan segmen di .EXE, dan C.OBJ menaruh BASE
;   (14 byte, kelas PROG) paling depan. Sudah dicoba dan GAGAL:
;     - DATA lebih dulu  -> seluruh DGROUP pindah ke depan kode (DATA 0x0000)
;     - PROG lebih dulu  -> BASE terdorong ke UJUNG (0x9060), kode geser -14
BASE    SEGMENT BYTE PUBLIC 'PROG'
BASE    ENDS

; PARA di sini yang bekerja: ia memberi atribut PARA pada SEGMEN DATA gabungan,
; sehingga LINK memberi padding di UJUNG PROG sampai batas paragraf. Karena
; modul ini di-link PALING AWAL (sebelum C.OBJ), kontribusi DATA-nya yang
; KOSONG jatuh di offset 0 -- sudah selaras, jadi TIDAK ada byte tersisip.
DATA    SEGMENT PARA PUBLIC 'DATA'
DATA    ENDS


        END
