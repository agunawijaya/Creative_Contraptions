; blit.asm -- DIBANGKITKAN oleh src_c/build/asmgen.py, lalu disunting tangan.
; Sumber: disassembly langsung CONTRAP_UNPACKED.EXE (bytenya sudah pasti).
;
;   672Fh  314 byte

        NAME    blit

PGROUP  GROUP   PROG
DGROUP  GROUP   DATA

DATA    SEGMENT WORD PUBLIC 'DATA'
DATA    ENDS

PROG    SEGMENT BYTE PUBLIC 'PROG'
        ASSUME  CS:PGROUP, DS:DGROUP

        PUBLIC  F672F

F672F:  PUSH	BP                     ; 672F  55
        PUSH	ES                     ; 6730  06
        MOV	BP, SP                  ; 6731  8b ec
        MOV	AX, 0B800H              ; 6733  b8 00 b8
        MOV	ES, AX                  ; 6736  8e c0
        MOV	AX, WORD PTR [BP+8]     ; 6738  8b 46 08
        ADD	AX, WORD PTR [BP+0CH]   ; 673B  03 46 0c
        MOV	WORD PTR DS:[2128H], AX ; 673E  a3 28 21
        MOV	AX, WORD PTR [BP+0AH]   ; 6741  8b 46 0a
        CDQ                         ; 6744  99
        DIV	WORD PTR DS:[2120H]     ; 6745  f7 36 20 21
        MOV	BX, DX                  ; 6749  8b da
        MOV	AX, WORD PTR [BP+0EH]   ; 674B  8b 46 0e
        CDQ                         ; 674E  99
        DIV	WORD PTR DS:[2120H]     ; 674F  f7 36 20 21
        ADD	BX, DX                  ; 6753  03 da
        SHL	BX, 1                   ; 6755  d1 e3
        MOV	WORD PTR DS:[2130H], BX ; 6757  89 1e 30 21
        MOV	BX, WORD PTR [BP+0AH]   ; 675B  8b 5e 0a
        SHR	BX, 1                   ; 675E  d1 eb
        SHR	BX, 1                   ; 6760  d1 eb
        MOV	WORD PTR DS:[2124H], BX ; 6762  89 1e 24 21
        MOV	AX, WORD PTR [BP+0AH]   ; 6766  8b 46 0a
        CDQ                         ; 6769  99
        DIV	WORD PTR DS:[2120H]     ; 676A  f7 36 20 21
        SHL	DX, 1                   ; 676E  d1 e2
        MOV	WORD PTR [212CH], DX    ; 6770  89 16 2c 21
        NEG	DX                      ; 6774  f7 da
        ADD	DX, 8                   ; 6776  83 c2 08
        MOV	WORD PTR [212EH], DX    ; 6779  89 16 2e 21
        MOV	AX, WORD PTR [BP+0EH]   ; 677D  8b 46 0e
        DEC	AX                      ; 6780  48
        SHR	AX, 1                   ; 6781  d1 e8
        SHR	AX, 1                   ; 6783  d1 e8
        ADD	AX, BX                  ; 6785  03 c3
        MOV	DX, AX                  ; 6787  8b d0
        CMP	WORD PTR [212CH], 0     ; 6789  83 3e 2c 21 00
        JE	L6791                    ; 678E  74 01
        INC	DX                      ; 6790  42
L6791:  MOV	SI, WORD PTR [BP+6]     ; 6791  8b 76 06
        MOV	BX, WORD PTR [BP+8]     ; 6794  8b 5e 08
L6797:  CMP	BX, WORD PTR DS:[2128H] ; 6797  3b 1e 28 21
        JL	L67A0                    ; 679B  7c 03
        JMP	L6850                   ; 679D  e9 b0 00
L67A0:  MOV	AX, BX                  ; 67A0  8b c3
        SHR	AX, 1                   ; 67A2  d1 e8
        PUSH	DX                     ; 67A4  52
        MUL	WORD PTR DS:[2122H]     ; 67A5  f7 26 22 21
        POP	DX                      ; 67A9  5a
        ADD	AX, WORD PTR DS:[2124H] ; 67AA  03 06 24 21
        MOV	DI, AX                  ; 67AE  8b f8
        TEST	BX, 1                  ; 67B0  f7 c3 01 00
        JE	L67BA                    ; 67B4  74 04
        ADD	DI, 2000H               ; 67B6  81 c7 00 20
L67BA:  PUSH	BX                     ; 67BA  53
        MOV	BX, WORD PTR DS:[2124H] ; 67BB  8b 1e 24 21
L67BF:  CMP	BX, DX                  ; 67BF  3b da
        JLE	L67C6                   ; 67C1  7e 03
        JMP	L684B                   ; 67C3  e9 85 00
L67C6:  JNE	L67CF                   ; 67C6  75 07
        CMP	WORD PTR DS:[2130H], 0  ; 67C8  83 3e 30 21 00
        JNE	L680C                   ; 67CD  75 3d
L67CF:  CMP	WORD PTR [212CH], 0     ; 67CF  83 3e 2c 21 00
        JE	L6834                    ; 67D4  74 5e
        CMP	BX, WORD PTR DS:[2124H] ; 67D6  3b 1e 24 21
        JE	L67F5                    ; 67DA  74 19
        CMP	BX, DX                  ; 67DC  3b da
        JE	L680C                    ; 67DE  74 2c
        MOV	AL, BYTE PTR [SI]       ; 67E0  8a 04
        INC	SI                      ; 67E2  46
        MOV	CX, WORD PTR [212EH]    ; 67E3  8b 0e 2e 21
        SHL	AL, CL                  ; 67E7  d2 e0
        MOV	AH, BYTE PTR [SI]       ; 67E9  8a 24
        MOV	CX, WORD PTR [212CH]    ; 67EB  8b 0e 2c 21
        SHR	AH, CL                  ; 67EF  d2 ec
        OR	AL, AH                   ; 67F1  0a c4
        JMP	L6843                   ; 67F3  eb 4e
L67F5:  MOV	AL, BYTE PTR [SI]       ; 67F5  8a 04
        MOV	CX, WORD PTR [212CH]    ; 67F7  8b 0e 2c 21
        SHR	AL, CL                  ; 67FB  d2 e8
        MOV	AH, BYTE PTR ES:[DI]    ; 67FD  26 8a 25
        MOV	CX, WORD PTR [212EH]    ; 6800  8b 0e 2e 21
        SHR	AH, CL                  ; 6804  d2 ec
        SHL	AH, CL                  ; 6806  d2 e4
        OR	AL, AH                   ; 6808  0a c4
        JMP	L6843                   ; 680A  eb 37
L680C:  MOV	AL, BYTE PTR [SI]       ; 680C  8a 04
        INC	SI                      ; 680E  46
        MOV	CX, WORD PTR [212EH]    ; 680F  8b 0e 2e 21
        CMP	WORD PTR [212EH], 8     ; 6813  83 3e 2e 21 08
        JGE	L681C                   ; 6818  7d 02
        SHL	AL, CL                  ; 681A  d2 e0
L681C:  JMP	L6825                   ; 681C  eb 07
        NOP                         ; 681E  90
        CMP	AL, 0                   ; 681F  3c 00
        JNE	L6825                   ; 6821  75 02
        JMP	L6846                   ; 6823  eb 21
L6825:  MOV	AH, BYTE PTR ES:[DI]    ; 6825  26 8a 25
        MOV	CX, WORD PTR DS:[2130H] ; 6828  8b 0e 30 21
        SHL	AH, CL                  ; 682C  d2 e4
        SHR	AH, CL                  ; 682E  d2 ec
        OR	AL, AH                   ; 6830  0a c4
        JMP	L6843                   ; 6832  eb 0f
L6834:  MOV	AL, BYTE PTR [SI]       ; 6834  8a 04
        INC	SI                      ; 6836  46
        MOV	BYTE PTR ES:[DI], AL    ; 6837  26 88 05
        INC	DI                      ; 683A  47
        INC	BX                      ; 683B  43
        CMP	BX, DX                  ; 683C  3b da
        JLE	L6834                   ; 683E  7e f4
        JMP	L684B                   ; 6840  eb 09
        NOP                         ; 6842  90
L6843:  MOV	BYTE PTR ES:[DI], AL    ; 6843  26 88 05
L6846:  INC	DI                      ; 6846  47
        INC	BX                      ; 6847  43
        JMP	L67BF                   ; 6848  e9 74 ff
L684B:  POP	BX                      ; 684B  5b
        INC	BX                      ; 684C  43
        JMP	L6797                   ; 684D  e9 47 ff
L6850:  POP	ES                      ; 6850  07
        POP	BP                      ; 6851  5d
        RET                         ; 6852  c3
        PUSH	BP                     ; 6853  55
        MOV	BP, SP                  ; 6854  8b ec
        MOV	AX, WORD PTR [BP+4]     ; 6856  8b 46 04
        INT	16H                     ; 6859  cd 16
        JNE	L6867                   ; 685B  75 0a
        CMP	WORD PTR [BP+4], 100H   ; 685D  81 7e 04 00 01
        JNE	L6867                   ; 6862  75 03
        MOV	AX, 0                   ; 6864  b8 00 00
L6867:  POP	BP                      ; 6867  5d
        RET                         ; 6868  c3

PROG    ENDS
        END
