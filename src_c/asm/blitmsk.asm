; blitmsk.asm -- DIBANGKITKAN oleh src_c/build/asmgen.py, lalu disunting tangan.
; Sumber: disassembly langsung CONTRAP_UNPACKED.EXE (bytenya sudah pasti).
;
;   6524h  326 byte

        NAME    blitmsk

PGROUP  GROUP   PROG
DGROUP  GROUP   DATA

DATA    SEGMENT WORD PUBLIC 'DATA'
DATA    ENDS

PROG    SEGMENT BYTE PUBLIC 'PROG'
        ASSUME  CS:PGROUP, DS:DGROUP

        PUBLIC  F6524

F6524:  PUSH	BP                     ; 6524  55
        PUSH	ES                     ; 6525  06
        MOV	BP, SP                  ; 6526  8b ec
        MOV	AX, 0B800H              ; 6528  b8 00 b8
        MOV	ES, AX                  ; 652B  8e c0
        MOV	DI, WORD PTR [BP+6]     ; 652D  8b 7e 06
        MOV	AX, WORD PTR [266H]     ; 6530  a1 66 02
        CMP	AX, 140H                ; 6533  3d 40 01
        JNE	L653B                   ; 6536  75 03
        JMP	L6579                   ; 6538  eb 3f
        NOP                         ; 653A  90
L653B:  SHR	AX, 1                   ; 653B  d1 e8
        MUL	WORD PTR [1FA0H]        ; 653D  f7 26 a0 1f
        ADD	AX, WORD PTR [26AH]     ; 6541  03 06 6a 02
        TEST	WORD PTR [266H], 1     ; 6545  f7 06 66 02 01 00
        JE	L6550                    ; 654B  74 03
        XOR	AX, 2000H               ; 654D  35 00 20
L6550:  MOV	BX, WORD PTR [BP+8]     ; 6550  8b 5e 08
        MOV	CX, 8                   ; 6553  b9 08 00
L6556:  MOV	SI, AX                  ; 6556  8b f0
        PUSH	CX                     ; 6558  51
        MOV	CX, 3                   ; 6559  b9 03 00
L655C:  CMP	BYTE PTR [DI], 0        ; 655C  80 3d 00
        JNE	L6566                   ; 655F  75 05
        MOV	DL, BYTE PTR [BX]       ; 6561  8a 17
        MOV	BYTE PTR ES:[SI], DL    ; 6563  26 88 14
L6566:  INC	SI                      ; 6566  46
        INC	DI                      ; 6567  47
        INC	BX                      ; 6568  43
        LOOP	L655C                  ; 6569  e2 f1
        POP	CX                      ; 656B  59
        TEST	AX, 2000H              ; 656C  a9 00 20
        JE	L6574                    ; 656F  74 03
        ADD	AX, 50H                 ; 6571  05 50 00
L6574:  XOR	AX, 2000H               ; 6574  35 00 20
        LOOP	L6556                  ; 6577  e2 dd
L6579:  POP	ES                      ; 6579  07
        POP	BP                      ; 657A  5d
        RET                         ; 657B  c3
        PUSH	BP                     ; 657C  55
        PUSH	ES                     ; 657D  06
        MOV	BP, SP                  ; 657E  8b ec
        MOV	AX, 0B800H              ; 6580  b8 00 b8
        MOV	ES, AX                  ; 6583  8e c0
        MOV	DI, WORD PTR [BP+6]     ; 6585  8b 7e 06
        MOV	AX, WORD PTR [260H]     ; 6588  a1 60 02
        CMP	AX, 140H                ; 658B  3d 40 01
        JNE	L6593                   ; 658E  75 03
        JMP	L65DD                   ; 6590  eb 4b
        NOP                         ; 6592  90
L6593:  SHR	AX, 1                   ; 6593  d1 e8
        MUL	WORD PTR [1FA0H]        ; 6595  f7 26 a0 1f
        ADD	AX, WORD PTR [268H]     ; 6599  03 06 68 02
        TEST	WORD PTR [260H], 1     ; 659D  f7 06 60 02 01 00
        JE	L65A8                    ; 65A3  74 03
        XOR	AX, 2000H               ; 65A5  35 00 20
L65A8:  MOV	CX, 8                   ; 65A8  b9 08 00
L65AB:  MOV	SI, AX                  ; 65AB  8b f0
        PUSH	CX                     ; 65AD  51
        PUSH	AX                     ; 65AE  50
        MOV	AX, WORD PTR [BP+8]     ; 65AF  8b 46 08
        MOV	CX, 3                   ; 65B2  b9 03 00
L65B5:  MOV	DL, BYTE PTR [DI]       ; 65B5  8a 15
        INC	DI                      ; 65B7  47
        MOV	BX, AX                  ; 65B8  8b d8
        INC	AX                      ; 65BA  40
        AND	DL, BYTE PTR [BX]       ; 65BB  22 17
        MOV	BX, WORD PTR [BP+0AH]   ; 65BD  8b 5e 0a
        INC	WORD PTR [BP+0AH]       ; 65C0  ff 46 0a
        OR	DL, BYTE PTR [BX]        ; 65C3  0a 17
        MOV	BYTE PTR ES:[SI], DL    ; 65C5  26 88 14
        INC	SI                      ; 65C8  46
        LOOP	L65B5                  ; 65C9  e2 ea
        MOV	WORD PTR [BP+8], AX     ; 65CB  89 46 08
        POP	AX                      ; 65CE  58
        POP	CX                      ; 65CF  59
        TEST	AX, 2000H              ; 65D0  a9 00 20
        JE	L65D8                    ; 65D3  74 03
        ADD	AX, 50H                 ; 65D5  05 50 00
L65D8:  XOR	AX, 2000H               ; 65D8  35 00 20
        LOOP	L65AB                  ; 65DB  e2 ce
L65DD:  POP	ES                      ; 65DD  07
        POP	BP                      ; 65DE  5d
        RET                         ; 65DF  c3
        PUSH	BP                     ; 65E0  55
        PUSH	ES                     ; 65E1  06
        MOV	BP, SP                  ; 65E2  8b ec
        MOV	AX, 0B800H              ; 65E4  b8 00 b8
        MOV	ES, AX                  ; 65E7  8e c0
        MOV	AX, 0B00H               ; 65E9  b8 00 0b
        SUB	BH, BH                  ; 65EC  2a ff
        MOV	BL, BYTE PTR [BP+6]     ; 65EE  8a 5e 06
        INT	10H                     ; 65F1  cd 10
        MOV	AX, 0B00H               ; 65F3  b8 00 0b
        MOV	BH, 1                   ; 65F6  b7 01
        MOV	BL, BYTE PTR [BP+8]     ; 65F8  8a 5e 08
        INT	10H                     ; 65FB  cd 10
        POP	ES                      ; 65FD  07
        POP	BP                      ; 65FE  5d
        RET                         ; 65FF  c3
        PUSH	BP                     ; 6600  55
        MOV	BP, SP                  ; 6601  8b ec
        PUSH	ES                     ; 6603  06
        PUSH	DS                     ; 6604  1e
        MOV	AX, WORD PTR [BP+4]     ; 6605  8b 46 04
        SHR	AX, 1                   ; 6608  d1 e8
        MUL	WORD PTR [1FB0H]        ; 660A  f7 26 b0 1f
        MOV	BX, WORD PTR [BP+6]     ; 660E  8b 5e 06
        CMP	BX, 0                   ; 6611  83 fb 00
        JE	L6617                    ; 6614  74 01
        DEC	BX                      ; 6616  4b
L6617:  SHR	BX, 1                   ; 6617  d1 eb
        SHR	BX, 1                   ; 6619  d1 eb
        ADD	AX, BX                  ; 661B  03 c3
        TEST	WORD PTR [BP+4], 1     ; 661D  f7 46 04 01 00
        JE	L6627                    ; 6622  74 03
        XOR	AX, 2000H               ; 6624  35 00 20
L6627:  MOV	DI, AX                  ; 6627  8b f8
        MOV	SI, DI                  ; 6629  8b f7
        SUB	SI, WORD PTR [BP+0CH]   ; 662B  2b 76 0c
        MOV	CX, WORD PTR [BP+8]     ; 662E  8b 4e 08
        MOV	DX, WORD PTR [BP+0AH]   ; 6631  8b 56 0a
        SHR	DX, 1                   ; 6634  d1 ea
        SHR	DX, 1                   ; 6636  d1 ea
        MOV	AX, 0B800H              ; 6638  b8 00 b8
        MOV	ES, AX                  ; 663B  8e c0
        MOV	DS, AX                  ; 663D  8e d8
        JMP	L6645                   ; 663F  eb 04
        NOP                         ; 6641  90
        MOV	AX, 0ABCDH              ; 6642  b8 cd ab
L6645:  PUSH	CX                     ; 6645  51
        PUSH	DI                     ; 6646  57
        PUSH	SI                     ; 6647  56
        MOV	CX, DX                  ; 6648  8b ca
        CLD                         ; 664A  fc
        REP MOVSB	BYTE PTR ES:[DI], BYTE PTR [SI]; 664B  f3 a4
        POP	SI                      ; 664D  5e
        POP	DI                      ; 664E  5f
        CMP	SI, 2000H               ; 664F  81 fe 00 20
        JL	L665B                    ; 6653  7c 06
        ADD	SI, 50H                 ; 6655  83 c6 50
        ADD	DI, 50H                 ; 6658  83 c7 50
L665B:  XOR	DI, 2000H               ; 665B  81 f7 00 20
        XOR	SI, 2000H               ; 665F  81 f6 00 20
        POP	CX                      ; 6663  59
        LOOP	L6645                  ; 6664  e2 df
        POP	DS                      ; 6666  1f
        POP	ES                      ; 6667  07
        POP	BP                      ; 6668  5d
        RET                         ; 6669  c3

PROG    ENDS
        END
