; setup.asm -- FUN_1000_5f90 @ 1000:5f90, TIGA byte.
;
; ⚠ BUKAN dari C. MS C 1.04 SELALU memancarkan prolog `push bp; mov bp,sp`
; dan epilog `pop bp` untuk fungsi apa pun -- `setup() { return 0; }` memberi
; 7 byte (55 8b ec 33 c0 5d c3), sedangkan aslinya hanya 3 byte tanpa prolog
; sama sekali. Jadi ini assembly tulisan tangan.
;
; Dipanggil `main` sekali di awal:
;     if (setup() != 0) { printf(0x930); return; }
; Di biner rilis pemeriksaannya SELALU lulus -- isinya sudah dicabut dan
; tinggal mengembalikan 0. Kemungkinan sisa pemeriksaan perangkat keras.
;
; ⚠ Sesudahnya ada 1.200 byte NOL (0x5F93..0x6442) yang BUKAN kode. Itu
; penting untuk akuntansi target rekonstruksi -- lihat catatan di README.

        NAME    setup

PGROUP  GROUP   PROG
DGROUP  GROUP   DATA

DATA    SEGMENT WORD PUBLIC 'DATA'
DATA    ENDS

PROG    SEGMENT BYTE PUBLIC 'PROG'
        ASSUME  CS:PGROUP, DS:DGROUP

        PUBLIC  setup

setup   PROC    NEAR
        SUB     AX,AX                   ; 5f90  2b c0
        RET                             ; 5f92  c3
setup   ENDP

PROG    ENDS
        END
