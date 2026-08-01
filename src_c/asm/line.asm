; line.asm -- DIBANGKITKAN oleh src_c/build/asmgen.py, lalu disunting tangan.
; Sumber: disassembly langsung CONTRAP_UNPACKED.EXE (bytenya sudah pasti).
;
;   5CBBh  221 byte

        NAME    line

PGROUP  GROUP   PROG
DGROUP  GROUP   DATA

DATA    SEGMENT WORD PUBLIC 'DATA'
DATA    ENDS

PROG    SEGMENT BYTE PUBLIC 'PROG'
        ASSUME  CS:PGROUP, DS:DGROUP

        PUBLIC  line

line:   PUSH	BP                     ; 5CBB  55
        PUSH	ES                     ; 5CBC  06
        MOV	BP, SP                  ; 5CBD  8b ec
        MOV	AX, 0B800H              ; 5CBF  b8 00 b8
        MOV	ES, AX                  ; 5CC2  8e c0
        MOV	AX, WORD PTR [BP+8]     ; 5CC4  8b 46 08
        MOV	AH, AL                  ; 5CC7  8a e0
        AND	AX, 1FEH                ; 5CC9  25 fe 01
        SHL	AX, 1                   ; 5CCC  d1 e0
        SHL	AX, 1                   ; 5CCE  d1 e0
        SHL	AX, 1                   ; 5CD0  d1 e0
        MOV	DI, AX                  ; 5CD2  8b f8
        AND	DI, 7FFH                ; 5CD4  81 e7 ff 07
        SHL	AX, 1                   ; 5CD8  d1 e0
        SHL	AX, 1                   ; 5CDA  d1 e0
        ADD	DI, AX                  ; 5CDC  03 f8
        MOV	AX, WORD PTR [BP+6]     ; 5CDE  8b 46 06
        SAR	AX, 1                   ; 5CE1  d1 f8
        SAR	AX, 1                   ; 5CE3  d1 f8
        ADD	DI, AX                  ; 5CE5  03 f8
        MOV	CX, WORD PTR [BP+0CH]   ; 5CE7  8b 4e 0c
        SUB	CX, WORD PTR [BP+8]     ; 5CEA  2b 4e 08
        INC	CX                      ; 5CED  41
        MOV	SI, WORD PTR [BP+0AH]   ; 5CEE  8b 76 0a
        SAR	SI, 1                   ; 5CF1  d1 fe
        SAR	SI, 1                   ; 5CF3  d1 fe
        MOV	AX, WORD PTR [BP+6]     ; 5CF5  8b 46 06
        SAR	AX, 1                   ; 5CF8  d1 f8
        SAR	AX, 1                   ; 5CFA  d1 f8
        SUB	SI, AX                  ; 5CFC  2b f0
        MOV	BX, WORD PTR [BP+0EH]   ; 5CFE  8b 5e 0e
        AND	BX, 3                   ; 5D01  81 e3 03 00
        MOV	DL, BYTE PTR [BX+1F30H] ; 5D05  8a 97 30 1f
        MOV	BX, WORD PTR [BP+6]     ; 5D09  8b 5e 06
        AND	BX, 3                   ; 5D0C  81 e3 03 00
        SHL	BX, 1                   ; 5D10  d1 e3
        SHL	BX, 1                   ; 5D12  d1 e3
        MOV	AX, WORD PTR [BP+0AH]   ; 5D14  8b 46 0a
        AND	AX, 3                   ; 5D17  25 03 00
        ADD	BX, AX                  ; 5D1A  03 d8
        SHL	BX, 1                   ; 5D1C  d1 e3
        MOV	BX, WORD PTR [BX+1F10H] ; 5D1E  8b 9f 10 1f
        MOV	DH, DL                  ; 5D22  8a f2
        MOV	AH, DL                  ; 5D24  8a e2
        AND	DX, BX                  ; 5D26  23 d3
        CLD                         ; 5D28  fc
        MOV	BP, CX                  ; 5D29  8b e9
L5D2B:  PUSH	CX                     ; 5D2B  51
        PUSH	DI                     ; 5D2C  57
        MOV	CX, SI                  ; 5D2D  8b ce
        MOV	AL, BH                  ; 5D2F  8a c7
        JCXZ	L5D42                  ; 5D31  e3 0f
        XOR	BYTE PTR ES:[DI], DH    ; 5D33  26 30 35
        INC	DI                      ; 5D36  47
        DEC	CX                      ; 5D37  49
        JCXZ	L5D40                  ; 5D38  e3 06
L5D3A:  XOR	BYTE PTR ES:[DI], AH    ; 5D3A  26 30 25
        INC	DI                      ; 5D3D  47
        LOOP	L5D3A                  ; 5D3E  e2 fa
L5D40:  MOV	AL, 0FFH                ; 5D40  b0 ff
L5D42:  AND	AL, BL                  ; 5D42  22 c3
        AND	DL, AL                  ; 5D44  22 d0
        XOR	BYTE PTR ES:[DI], DL    ; 5D46  26 30 15
        INC	DI                      ; 5D49  47
        POP	DI                      ; 5D4A  5f
        TEST	DI, 2000H              ; 5D4B  f7 c7 00 20
        JE	L5D54                    ; 5D4F  74 03
        ADD	DI, 50H                 ; 5D51  83 c7 50
L5D54:  XOR	DI, 2000H               ; 5D54  81 f7 00 20
        POP	CX                      ; 5D58  59
        LOOP	L5D2B                  ; 5D59  e2 d0
        POP	ES                      ; 5D5B  07
        POP	BP                      ; 5D5C  5d
        RET                         ; 5D5D  c3
        PUSH	BP                     ; 5D5E  55
        PUSH	ES                     ; 5D5F  06
        MOV	BP, SP                  ; 5D60  8b ec
        MOV	BX, 0B800H              ; 5D62  bb 00 b8
        MOV	ES, BX                  ; 5D65  8e c3
        MOV	BX, WORD PTR [BP+6]     ; 5D67  8b 5e 06
        MOV	BYTE PTR ES:[BX], 0     ; 5D6A  26 c6 07 00
        POP	ES                      ; 5D6E  07
        POP	BP                      ; 5D6F  5d
        RET                         ; 5D70  c3
        MOV	AX, BP                  ; 5D71  8b c5
        SUB	AX, SP                  ; 5D73  2b c4
        PUSH	BP                     ; 5D75  55
        PUSH	ES                     ; 5D76  06
        MOV	BP, SP                  ; 5D77  8b ec
        MOV	BX, 0B800H              ; 5D79  bb 00 b8
        MOV	ES, BX                  ; 5D7C  8e c3
        MOV	BX, WORD PTR [BP+6]     ; 5D7E  8b 5e 06
        MOV	AL, BYTE PTR [BP+8]     ; 5D81  8a 46 08
        CMP	WORD PTR [BP+0AH], 0    ; 5D84  83 7e 0a 00
        JNE	L5D92                   ; 5D88  75 08
        NOT	AL                      ; 5D8A  f6 d0
        AND	BYTE PTR ES:[BX], AL    ; 5D8C  26 20 07
        JMP	SHORT L5D95             ; 5D8F  eb 04
        NOP                         ; 5D91  90
L5D92:  OR	BYTE PTR ES:[BX], AL     ; 5D92  26 08 07
L5D95:  POP	ES                      ; 5D95  07
        POP	BP                      ; 5D96  5d
        RET                         ; 5D97  c3

PROG    ENDS
        END
