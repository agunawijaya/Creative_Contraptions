; vbio.asm -- lima primitif CGA kecil di 0x5d98..0x5dcd (54 byte).
;
; Ini fungsi ASSEMBLY TULISAN TANGAN di biner asli, bukan hasil kompilasi C:
; tidak ada prolog "push bp; sub sp,N; mov bp,sp" sama sekali, dan semuanya
; menyentuh port I/O langsung. Lihat src_c/README.md Sec.Fungsi assembly.
;
;   5d98 vbwait   tunggu sampai bit vblank MENYALA  (9 byte)
;   5da1 vbend    tunggu sampai bit vblank PADAM    (9 byte)
;   5daa scroff   CGA mode 0x3d8 <- 02  (video mati) (7 byte)
;   5db1 scron    CGA mode 0x3d8 <- 0A  (video hidup)(7 byte)
;   5db8 setfont  pasang vektor INT 1Fh -> 907h:1F40h (font 8x8 separuh atas)
;
; Segmen & grup HARUS sama dengan keluaran MS C 1.04 supaya bisa di-link
; bersama: PROG SEGMENT BYTE PUBLIC 'PROG', grup PGROUP.
; (dibaca dari LNAMES/SEGDEF .OBJ hasil MC2: '', PROG, DATA, PGROUP, DGROUP)

        NAME    vbio

PGROUP  GROUP   PROG
DGROUP  GROUP   DATA

DATA    SEGMENT WORD PUBLIC 'DATA'
DATA    ENDS

PROG    SEGMENT BYTE PUBLIC 'PROG'
        ASSUME  CS:PGROUP, DS:DGROUP

        PUBLIC  vbwait, vbend, scroff, scron, setfont

; tunggu sampai bit 3 port 3DAh MENYALA (retrace mulai)
vbwait  PROC    NEAR
        MOV     DX,3DAH
VBW1:   IN      AL,DX
        TEST    AL,8
        JZ      VBW1
        RET
vbwait  ENDP

; tunggu sampai bit 3 port 3DAh PADAM (retrace selesai)
vbend   PROC    NEAR
        MOV     DX,3DAH
VBE1:   IN      AL,DX
        TEST    AL,8
        JNZ     VBE1
        RET
vbend   ENDP

; matikan video CGA
scroff  PROC    NEAR
        MOV     AL,2
        MOV     DX,3D8H
        OUT     DX,AL
        RET
scroff  ENDP

; hidupkan video CGA (320x200 grafis)
scron   PROC    NEAR
        MOV     AL,0AH
        MOV     DX,3D8H
        OUT     DX,AL
        RET
scron   ENDP

; arahkan INT 1Fh (font 8x8 karakter 128..255) ke tabel di DGROUP:1F40h
setfont PROC    NEAR
        PUSH    ES
        MOV     AX,0
        MOV     ES,AX
        CLI
        MOV     DI,7CH
        MOV     AX,1F40H
        CLD
        STOSW
        MOV     AX,DGROUP
        STOSW
        STI
        POP     ES
        RET
setfont ENDP

PROG    ENDS
        END
