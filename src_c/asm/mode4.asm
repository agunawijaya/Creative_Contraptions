; mode4.asm -- 0x5F93..0x6449, 1.207 byte.
;
; Menutup satu-satunya LUBANG yang tersisa di wilayah kode (<0x69d7). Sebelum
; modul ini ada, manifest melompat dari `setup` (0x5F90, 3 byte) langsung ke
; `text` (0x644A) -- dan .EXE hasil link kita KEHILANGAN 1.207 byte di situ,
; sehingga seluruh isi sesudahnya bergeser.
;
; Isinya dua bagian:
;
; 1. 0x5F93..0x6442 = 1.200 byte NOL.
;    TIDAK ADA satu pun `call` di seluruh biner yang menunjuk ke dalam rentang
;    ini (dipindai byte-per-byte atas E8 di 0x0082..0x9062). Jadi ini bukan
;    kode: kemungkinan penyangga tak terinisialisasi milik rutin setup yang
;    isinya sudah dicabut (lihat setup.asm -- fungsinya tinggal `SUB AX,AX/RET`).
;    Apa pun asal-usulnya, byte-nya ADA di biner asli dan harus dipancarkan
;    supaya tata letaknya cocok.
;
; 2. 0x6443..0x6449 = 7 byte: set mode video CGA 4 (320x200, 4 warna).
;    Juga tidak dipanggil `call` mana pun -- kemungkinan sisa dari jalur
;    inisialisasi yang sama. Diberi nama `mode4` dan di-PUBLIC supaya
;    symcheck bisa memeriksanya; tidak ada yang memanggilnya dari C.
;
; ⚠ Modul ini HARUS berada di antara `setup` dan `text` saat link. Urutan link
;   sekarang dibaca dari manifest.txt (urut ALAMAT), jadi cukup daftarkan
;   `mode4 5f93 1207` di sana.

        NAME    mode4

PGROUP  GROUP   PROG
DGROUP  GROUP   DATA

DATA    SEGMENT WORD PUBLIC 'DATA'
DATA    ENDS

PROG    SEGMENT BYTE PUBLIC 'PROG'
        ASSUME  CS:PGROUP, DS:DGROUP

        PUBLIC  mode4

        DB      1200 DUP(0)             ; 5f93..6442  penyangga/sisa, semuanya nol

mode4   PROC    NEAR
        MOV     AL,4                    ; 6443  b0 04
        MOV     AH,0                    ; 6445  b4 00
        INT     10H                     ; 6447  cd 10
        RET                             ; 6449  c3
mode4   ENDP

PROG    ENDS
        END
