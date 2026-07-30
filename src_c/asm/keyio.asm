; keyio.asm -- DIBANGKITKAN oleh src_c/build/asmgen.py, lalu disunting tangan.
; Sumber: disassembly langsung CONTRAP_UNPACKED.EXE (bytenya sudah pasti).
;
;   66FDh  50 byte

        NAME    keyio

PGROUP  GROUP   PROG
DGROUP  GROUP   DATA

DATA    SEGMENT WORD PUBLIC 'DATA'
DATA    ENDS

PROG    SEGMENT BYTE PUBLIC 'PROG'
        ASSUME  CS:PGROUP, DS:DGROUP

        PUBLIC  F66FD
        EXTRN   tone3:NEAR

F66FD:  PUSH	BP                     ; 66FD  55
        MOV	BP, SP                  ; 66FE  8b ec
        MOV	AH, 2                   ; 6700  b4 02
        MOV	BH, 0                   ; 6702  b7 00
        MOV	DH, BYTE PTR [BP+4]     ; 6704  8a 76 04
        MOV	DL, BYTE PTR [BP+6]     ; 6707  8a 56 06
        INT	10H                     ; 670A  cd 10
        POP	BP                      ; 670C  5d
        RET                         ; 670D  c3
        PUSH	AX                     ; 670E  50
        PUSH	DS                     ; 670F  1e
        MOV	AX, 907H                ; 6710  b8 07 09
        MOV	DS, AX                  ; 6713  8e d8
        DEC	WORD PTR DS:[2E4H]      ; 6715  ff 0e e4 02
        DEC	WORD PTR DS:[7EAH]      ; 6719  ff 0e ea 07
        DEC	WORD PTR DS:[7F2H]      ; 671D  ff 0e f2 07
        DEC	WORD PTR DS:[7F4H]      ; 6721  ff 0e f4 07
        CALL	tone3                  ; 6725  e8 4b f4
        MOV	AL, 20H                 ; 6728  b0 20
        OUT	20H, AL                 ; 672A  e6 20
        POP	DS                      ; 672C  1f
        POP	AX                      ; 672D  58
        IRET                        ; 672E  cf

PROG    ENDS
        END
