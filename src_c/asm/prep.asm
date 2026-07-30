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
        PUSH	BP                     ; 69D7  55
        SUB	SP, 4                   ; 69D8  83 ec 04
        MOV	BP, SP                  ; 69DB  8b ec
        MOV	WORD PTR [BP], AX       ; 69DD  89 46 00
        OR	AX, BX                   ; 69E0  0b c3
        JE	L6A43                    ; 69E2  74 5f
        MOV	WORD PTR [BP+2], CX     ; 69E4  89 4e 02
        OR	CX, DX                   ; 69E7  0b ca
        JE	L6A3F                    ; 69E9  74 54
        MOV	AX, WORD PTR [BP]       ; 69EB  8b 46 00
        MOV	CX, WORD PTR [BP+2]     ; 69EE  8b 4e 02
        MOV	SI, AX                  ; 69F1  8b f0
        TEST	SI, SI                 ; 69F3  85 f6
        JNS	L69FE                   ; 69F5  79 07
        NOT	AX                      ; 69F7  f7 d0
        NEG	BX                      ; 69F9  f7 db
        SBB	AX, 0FFFFH              ; 69FB  1d ff ff
L69FE:  XOR	SI, CX                  ; 69FE  33 f1
        MOV	WORD PTR [BP], SI       ; 6A00  89 76 00
        TEST	CX, CX                 ; 6A03  85 c9
        JNS	L6A0E                   ; 6A05  79 07
        NOT	CX                      ; 6A07  f7 d1
        NEG	DX                      ; 6A09  f7 da
        SBB	CX,-1                   ; 6A0B  83 d9 ff
L6A0E:  MOV	SI, 20H                 ; 6A0E  be 20 00
        MOV	WORD PTR [BP+2], SI     ; 6A11  89 76 02
        XOR	SI, SI                  ; 6A14  33 f6
        XOR	DI, DI                  ; 6A16  33 ff
L6A18:  SHR	SI, 1                   ; 6A18  d1 ee
        RCR	DI, 1                   ; 6A1A  d1 df
        RCR	AX, 1                   ; 6A1C  d1 d8
        RCR	BX, 1                   ; 6A1E  d1 db
        JAE	L6A26                   ; 6A20  73 04
        ADD	DI, DX                  ; 6A22  03 fa
        ADC	SI, CX                  ; 6A24  13 f1
L6A26:  DEC	WORD PTR [BP+2]         ; 6A26  ff 4e 02
        JNE	L6A18                   ; 6A29  75 ed
        SHR	AX, 1                   ; 6A2B  d1 e8
        RCR	BX, 1                   ; 6A2D  d1 db
        MOV	SI, WORD PTR [BP]       ; 6A2F  8b 76 00
        TEST	SI, SI                 ; 6A32  85 f6
        JNS	L6A43                   ; 6A34  79 0d
        NOT	AX                      ; 6A36  f7 d0
        NEG	BX                      ; 6A38  f7 db
        SBB	AX, 0FFFFH              ; 6A3A  1d ff ff
        JMP	SHORT L6A43             ; 6A3D  eb 04
L6A3F:  XOR	AX, AX                  ; 6A3F  33 c0
        XOR	BX, BX                  ; 6A41  33 db
L6A43:  ADD	SP, 4                   ; 6A43  83 c4 04
        POP	BP                      ; 6A46  5d
        RET                         ; 6A47  c3

PROG    ENDS
        END
