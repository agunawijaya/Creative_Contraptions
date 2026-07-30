; fillrec.asm -- DIBANGKITKAN oleh src_c/build/asmgen.py, lalu disunting tangan.
; Sumber: disassembly langsung CONTRAP_UNPACKED.EXE (bytenya sudah pasti).
;
;   6869h  208 byte

        NAME    fillrec

PGROUP  GROUP   PROG
DGROUP  GROUP   DATA

DATA    SEGMENT WORD PUBLIC 'DATA'
DATA    ENDS

PROG    SEGMENT BYTE PUBLIC 'PROG'
        ASSUME  CS:PGROUP, DS:DGROUP

        PUBLIC  F6869

F6869:  PUSH	BP                     ; 6869  55
        PUSH	ES                     ; 686A  06
        MOV	BP, SP                  ; 686B  8b ec
        MOV	AX, 0B800H              ; 686D  b8 00 b8
        MOV	ES, AX                  ; 6870  8e c0
        MOV	AX, WORD PTR [BP+8]     ; 6872  8b 46 08
        MOV	AH, AL                  ; 6875  8a e0
        AND	AX, 1FEH                ; 6877  25 fe 01
        SHL	AX, 1                   ; 687A  d1 e0
        SHL	AX, 1                   ; 687C  d1 e0
        SHL	AX, 1                   ; 687E  d1 e0
        MOV	DI, AX                  ; 6880  8b f8
        AND	DI, 7FFH                ; 6882  81 e7 ff 07
        SHL	AX, 1                   ; 6886  d1 e0
        SHL	AX, 1                   ; 6888  d1 e0
        ADD	DI, AX                  ; 688A  03 f8
        MOV	AX, WORD PTR [BP+6]     ; 688C  8b 46 06
        SAR	AX, 1                   ; 688F  d1 f8
        SAR	AX, 1                   ; 6891  d1 f8
        ADD	DI, AX                  ; 6893  03 f8
        MOV	CX, WORD PTR [BP+0CH]   ; 6895  8b 4e 0c
        SUB	CX, WORD PTR [BP+8]     ; 6898  2b 4e 08
        INC	CX                      ; 689B  41
        MOV	SI, WORD PTR [BP+0AH]   ; 689C  8b 76 0a
        SAR	SI, 1                   ; 689F  d1 fe
        SAR	SI, 1                   ; 68A1  d1 fe
        MOV	AX, WORD PTR [BP+6]     ; 68A3  8b 46 06
        SAR	AX, 1                   ; 68A6  d1 f8
        SAR	AX, 1                   ; 68A8  d1 f8
        SUB	SI, AX                  ; 68AA  2b f0
        MOV	BX, WORD PTR [BP+0EH]   ; 68AC  8b 5e 0e
        AND	BX, 3                   ; 68AF  81 e3 03 00
        MOV	DL, BYTE PTR [BX+2160H] ; 68B3  8a 97 60 21
        MOV	BX, WORD PTR [BP+6]     ; 68B7  8b 5e 06
        AND	BX, 3                   ; 68BA  81 e3 03 00
        SHL	BX, 1                   ; 68BE  d1 e3
        SHL	BX, 1                   ; 68C0  d1 e3
        MOV	AX, WORD PTR [BP+0AH]   ; 68C2  8b 46 0a
        AND	AX, 3                   ; 68C5  25 03 00
        ADD	BX, AX                  ; 68C8  03 d8
        SHL	BX, 1                   ; 68CA  d1 e3
        MOV	BX, WORD PTR [BX+2140H] ; 68CC  8b 9f 40 21
        MOV	DH, DL                  ; 68D0  8a f2
        MOV	AH, DL                  ; 68D2  8a e2
        AND	DX, BX                  ; 68D4  23 d3
        CLD                         ; 68D6  fc
L68D7:  PUSH	CX                     ; 68D7  51
        PUSH	DI                     ; 68D8  57
        MOV	CX, SI                  ; 68D9  8b ce
        MOV	AL, BH                  ; 68DB  8a c7
        JCXZ	L68F0                  ; 68DD  e3 11
        NOT	AL                      ; 68DF  f6 d0
        AND	AL, BYTE PTR ES:[DI]    ; 68E1  26 22 05
        OR	AL, DH                   ; 68E4  0a c6
        STOSB	BYTE PTR ES:[DI], AL  ; 68E6  aa
        DEC	CX                      ; 68E7  49
        JCXZ	L68EE                  ; 68E8  e3 04
        MOV	AL, AH                  ; 68EA  8a c4
        REP STOSB	BYTE PTR ES:[DI], AL; 68EC  f3 aa
L68EE:  MOV	AL, 0FFH                ; 68EE  b0 ff
L68F0:  AND	AL, BL                  ; 68F0  22 c3
        AND	DL, AL                  ; 68F2  22 d0
        NOT	AL                      ; 68F4  f6 d0
        AND	AL, BYTE PTR ES:[DI]    ; 68F6  26 22 05
        OR	AL, DL                   ; 68F9  0a c2
        STOSB	BYTE PTR ES:[DI], AL  ; 68FB  aa
        POP	DI                      ; 68FC  5f
        TEST	DI, 2000H              ; 68FD  f7 c7 00 20
        JE	L6906                    ; 6901  74 03
        ADD	DI, 50H                 ; 6903  83 c7 50
L6906:  XOR	DI, 2000H               ; 6906  81 f7 00 20
        POP	CX                      ; 690A  59
        LOOP	L68D7                  ; 690B  e2 ca
        POP	ES                      ; 690D  07
        POP	BP                      ; 690E  5d
        RET                         ; 690F  c3
        PUSH	BP                     ; 6910  55
        PUSH	ES                     ; 6911  06
        MOV	BP, SP                  ; 6912  8b ec
        MOV	AX, 0B800H              ; 6914  b8 00 b8
        MOV	ES, AX                  ; 6917  8e c0
        MOV	AH, 0                   ; 6919  b4 00
        MOV	BX, WORD PTR [BP+6]     ; 691B  8b 5e 06
        MOV	AL, BYTE PTR ES:[BX]    ; 691E  26 8a 07
        POP	ES                      ; 6921  07
        POP	BP                      ; 6922  5d
        RET                         ; 6923  c3
        PUSH	BP                     ; 6924  55
        PUSH	ES                     ; 6925  06
        MOV	BP, SP                  ; 6926  8b ec
        MOV	AX, 0B800H              ; 6928  b8 00 b8
        MOV	ES, AX                  ; 692B  8e c0
        MOV	AX, WORD PTR [BP+8]     ; 692D  8b 46 08
        MOV	BX, WORD PTR [BP+6]     ; 6930  8b 5e 06
        MOV	BYTE PTR ES:[BX], AL    ; 6933  26 88 07
        POP	ES                      ; 6936  07
        POP	BP                      ; 6937  5d
        RET                         ; 6938  c3

PROG    ENDS
        END
