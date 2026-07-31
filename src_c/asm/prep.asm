; prep.asm -- DIBANGKITKAN oleh src_c/build/asmgen.py, lalu disunting tangan.
; Sumber: disassembly langsung CONTRAP_UNPACKED.EXE (bytenya sudah pasti).
;
;   6939h  271 byte

        NAME    prep

PGROUP  GROUP   PROG
DGROUP  GROUP   DATA

DATA    SEGMENT WORD PUBLIC 'DATA'
DATA    ENDS

PROG    SEGMENT BYTE PUBLIC 'PROG'
        ASSUME  CS:PGROUP, DS:DGROUP

        PUBLIC  prep

prep:   PUSH	ES                     ; 6939  06
        PUSH	BP                     ; 693A  55
        MOV	BP, SP                  ; 693B  8b ec
        MOV	AX, 0B800H              ; 693D  b8 00 b8
        MOV	ES, AX                  ; 6940  8e c0
        SHR	WORD PTR [BP+8], 1      ; 6942  d1 6e 08
        SHR	WORD PTR [BP+8], 1      ; 6945  d1 6e 08
        MOV	DI, WORD PTR [BP+0AH]   ; 6948  8b 7e 0a
        MOV	DX, WORD PTR [BP+6]     ; 694B  8b 56 06
        MOV	AX, DX                  ; 694E  8b c2
        SHR	AX, 1                   ; 6950  d1 e8
        MUL	BYTE PTR DS:[2170H]     ; 6952  f6 26 70 21
        ADD	AX, WORD PTR [BP+8]     ; 6956  03 46 08
        MOV	WORD PTR DS:[2176H], AX ; 6959  a3 76 21
        ADD	AX, 2000H               ; 695C  05 00 20
        MOV	WORD PTR DS:[2174H], AX ; 695F  a3 74 21
        TEST	DX, 1                  ; 6962  f7 c2 01 00
        JE	L696F                    ; 6966  74 07
        MOV	AX, 50H                 ; 6968  b8 50 00
        ADD	WORD PTR DS:[2176H], AX ; 696B  01 06 76 21
L696F:  MOV	CX, 8                   ; 696F  b9 08 00
L6972:  MOV	BX, WORD PTR DS:[2171H] ; 6972  8b 1e 71 21
        TEST	DX, 1                  ; 6976  f7 c2 01 00
        JE	L6986                    ; 697A  74 0a
        MOV	SI, WORD PTR DS:[2174H] ; 697C  8b 36 74 21
        ADD	WORD PTR DS:[2174H], BX ; 6980  01 1e 74 21
        JMP	SHORT L698E             ; 6984  eb 08
L6986:  MOV	SI, WORD PTR DS:[2176H] ; 6986  8b 36 76 21
        ADD	WORD PTR DS:[2176H], BX ; 698A  01 1e 76 21
L698E:  XOR	BX, BX                  ; 698E  33 db
        PUSH	CX                     ; 6990  51
        MOV	CX, 3                   ; 6991  b9 03 00
L6994:  MOV	AL, BYTE PTR ES:[BX+SI] ; 6994  26 8a 00
        MOV	BYTE PTR [BX+DI], AL    ; 6997  88 01
        INC	BX                      ; 6999  43
        LOOP	L6994                  ; 699A  e2 f8
        POP	CX                      ; 699C  59
        ADD	DI, 3                   ; 699D  83 c7 03
        INC	DX                      ; 69A0  42
        LOOP	L6972                  ; 69A1  e2 cf
        POP	BP                      ; 69A3  5d
        POP	ES                      ; 69A4  07
        RET                         ; 69A5  c3
        PUSH	ES                     ; 69A6  06
        PUSH	BP                     ; 69A7  55
        MOV	BP, SP                  ; 69A8  8b ec
        MOV	AX, 0B800H              ; 69AA  b8 00 b8
        MOV	ES, AX                  ; 69AD  8e c0
        MOV	AX, WORD PTR [BP+6]     ; 69AF  8b 46 06
        TEST	AX, 1                  ; 69B2  a9 01 00
        JNE	L69C0                   ; 69B5  75 09
        SHR	AX, 1                   ; 69B7  d1 e8
        MUL	WORD PTR DS:[2171H]     ; 69B9  f7 26 71 21
        JMP	SHORT L69C9             ; 69BD  eb 0a
        NOP                         ; 69BF  90
L69C0:  SHR	AX, 1                   ; 69C0  d1 e8
        MUL	WORD PTR DS:[2171H]     ; 69C2  f7 26 71 21
        ADD	AX, 2000H               ; 69C6  05 00 20
L69C9:  ADD	AX, WORD PTR [BP+8]     ; 69C9  03 46 08
        MOV	BX, AX                  ; 69CC  8b d8
        MOV	CX, WORD PTR [BP+0AH]   ; 69CE  8b 4e 0a
        MOV	BYTE PTR ES:[BX], CL    ; 69D1  26 88 0f
        POP	BP                      ; 69D4  5d
        POP	ES                      ; 69D5  07
        RET                         ; 69D6  c3

; ⚠ DIPOTONG 2026-07-31. Baris di bawah ini dulu memuat 113 byte lagi
; (0x69D7..0x6A47) yang TERNYATA BUKAN milik `prep` melainkan modul MC.LIB
; `CXM33` (pembantu perkalian long) -- dibuktikan `src_c/verify/libmatch.py`:
;     0x69d7  113 byte  CXM33   CXM33@0x69d7
; Kode itu tidak pernah di-PUBLIC di sini, jadi ia beban mati: LINK tetap
; menarik CXM33 dari pustaka untuk memenuhi rujukan, dan salinan di sini
; cuma menggeser SELURUH wilayah pustaka +113 byte.
; `prep` yang benar = 0x6939..0x69D6 = 158 byte.

PROG    ENDS
        END
