; shftl.asm -- DIBANGKITKAN oleh src_c/build/asmgen.py, lalu disunting tangan.
; Sumber: disassembly langsung CONTRAP_UNPACKED.EXE (bytenya sudah pasti).
;
;   5DCEh  109 byte

        NAME    shftl

PGROUP  GROUP   PROG
DGROUP  GROUP   DATA

DATA    SEGMENT WORD PUBLIC 'DATA'
DATA    ENDS

PROG    SEGMENT BYTE PUBLIC 'PROG'
        ASSUME  CS:PGROUP, DS:DGROUP

        PUBLIC  F5DCE

F5DCE:  PUSH	BP                     ; 5DCE  55
        MOV	BP, SP                  ; 5DCF  8b ec
        PUSH	ES                     ; 5DD1  06
        PUSH	DS                     ; 5DD2  1e
        MOV	AX, WORD PTR [BP+4]     ; 5DD3  8b 46 04
        SHR	AX, 1                   ; 5DD6  d1 e8
        MUL	WORD PTR [1F60H]        ; 5DD8  f7 26 60 1f
        MOV	BX, WORD PTR [BP+6]     ; 5DDC  8b 5e 06
        ADD	BX, WORD PTR [BP+0AH]   ; 5DDF  03 5e 0a
        CMP	BX, 0                   ; 5DE2  83 fb 00
        JE	L5DE8                    ; 5DE5  74 01
        DEC	BX                      ; 5DE7  4b
L5DE8:  SHR	BX, 1                   ; 5DE8  d1 eb
        SHR	BX, 1                   ; 5DEA  d1 eb
        ADD	AX, BX                  ; 5DEC  03 c3
        TEST	WORD PTR [BP+4], 1     ; 5DEE  f7 46 04 01 00
        JE	L5DF8                    ; 5DF3  74 03
        XOR	AX, 2000H               ; 5DF5  35 00 20
L5DF8:  MOV	DI, AX                  ; 5DF8  8b f8
        MOV	SI, DI                  ; 5DFA  8b f7
        SUB	SI, WORD PTR [BP+0CH]   ; 5DFC  2b 76 0c
        MOV	CX, WORD PTR [BP+8]     ; 5DFF  8b 4e 08
        MOV	DX, WORD PTR [BP+0AH]   ; 5E02  8b 56 0a
        SHR	DX, 1                   ; 5E05  d1 ea
        SHR	DX, 1                   ; 5E07  d1 ea
        MOV	AX, 0B800H              ; 5E09  b8 00 b8
        MOV	ES, AX                  ; 5E0C  8e c0
        MOV	DS, AX                  ; 5E0E  8e d8
        JMP	L5E16                   ; 5E10  eb 04
        NOP                         ; 5E12  90
        MOV	AX, 0ABCDH              ; 5E13  b8 cd ab
L5E16:  PUSH	CX                     ; 5E16  51
        PUSH	DI                     ; 5E17  57
        PUSH	SI                     ; 5E18  56
        MOV	CX, DX                  ; 5E19  8b ca
        STD                         ; 5E1B  fd
        REP MOVSB	BYTE PTR ES:[DI], BYTE PTR [SI]; 5E1C  f3 a4
        POP	SI                      ; 5E1E  5e
        POP	DI                      ; 5E1F  5f
        CMP	SI, 2000H               ; 5E20  81 fe 00 20
        JL	L5E2C                    ; 5E24  7c 06
        ADD	SI, 50H                 ; 5E26  83 c6 50
        ADD	DI, 50H                 ; 5E29  83 c7 50
L5E2C:  XOR	DI, 2000H               ; 5E2C  81 f7 00 20
        XOR	SI, 2000H               ; 5E30  81 f6 00 20
        POP	CX                      ; 5E34  59
        LOOP	L5E16                  ; 5E35  e2 df
        POP	DS                      ; 5E37  1f
        POP	ES                      ; 5E38  07
        POP	BP                      ; 5E39  5d
        RET                         ; 5E3A  c3

PROG    ENDS
        END
