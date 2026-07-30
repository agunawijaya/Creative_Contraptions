; text.asm -- DIBANGKITKAN oleh src_c/build/asmgen.py, lalu disunting tangan.
; Sumber: disassembly langsung CONTRAP_UNPACKED.EXE (bytenya sudah pasti).
;
;   644Ah  218 byte

        NAME    text

PGROUP  GROUP   PROG
DGROUP  GROUP   DATA

DATA    SEGMENT WORD PUBLIC 'DATA'
DATA    ENDS

PROG    SEGMENT BYTE PUBLIC 'PROG'
        ASSUME  CS:PGROUP, DS:DGROUP

        PUBLIC  F644A
        EXTRN   X6869:NEAR      ;; ??? target di luar modul

F644A:  MOV	BX, SP                  ; 644A  8b dc
        MOV	AX, WORD PTR SS:[BX+2]  ; 644C  36 8b 47 02
        INT	10H                     ; 6450  cd 10
        RET                         ; 6452  c3
        PUSH	BP                     ; 6453  55
        PUSH	ES                     ; 6454  06
        MOV	BP, SP                  ; 6455  8b ec
        PUSH	SI                     ; 6457  56
        MOV	AX, 0B800H              ; 6458  b8 00 b8
        MOV	ES, AX                  ; 645B  8e c0
L645D:  MOV	BX, WORD PTR [BP+6]     ; 645D  8b 5e 06
        MOV	AL, BYTE PTR [BX]       ; 6460  8a 07
        INC	WORD PTR [BP+6]         ; 6462  ff 46 06
        CMP	AL, 0                   ; 6465  3c 00
        JNE	L646C                   ; 6467  75 03
        JMP	L6520                   ; 6469  e9 b4 00
L646C:  MOV	AH, 0                   ; 646C  b4 00
        SHL	AX, 1                   ; 646E  d1 e0
        SHL	AX, 1                   ; 6470  d1 e0
        SHL	AX, 1                   ; 6472  d1 e0
        CMP	AX, 400H                ; 6474  3d 00 04
        JGE	L647F                   ; 6477  7d 06
        ADD	AX, 0FA75H              ; 6479  05 75 fa
        JMP	L6491                   ; 647C  eb 13
        NOP                         ; 647E  90
L647F:  SUB	AX, 400H                ; 647F  2d 00 04
        ADD	AX, 1F70H               ; 6482  05 70 1f
        ADD	AX, 7                   ; 6485  05 07 00
        MOV	SI, AX                  ; 6488  8b f0
        MOV	DX, DS                  ; 648A  8c da
        MOV	AX, DS                  ; 648C  8c d8
        JMP	L649A                   ; 648E  eb 0a
        NOP                         ; 6490  90
L6491:  MOV	SI, AX                  ; 6491  8b f0
        MOV	DX, DS                  ; 6493  8c da
        MOV	AX, 0F000H              ; 6495  b8 00 f0
        MOV	DS, AX                  ; 6498  8e d8
L649A:  MOV	CX, 8                   ; 649A  b9 08 00
        STD                         ; 649D  fd
L649E:  LODSB	AL, BYTE PTR [SI]     ; 649E  ac
        PUSH	AX                     ; 649F  50
        LOOP	L649E                  ; 64A0  e2 fc
        MOV	DS, DX                  ; 64A2  8e da
        MOV	AX, WORD PTR [BP+8]     ; 64A4  8b 46 08
        MOV	WORD PTR [1F90H], AX    ; 64A7  a3 90 1f
        MOV	AX, WORD PTR [BP+0AH]   ; 64AA  8b 46 0a
        MOV	WORD PTR [1F94H], AX    ; 64AD  a3 94 1f
        MOV	CX, 8                   ; 64B0  b9 08 00
L64B3:  POP	DX                      ; 64B3  5a
        PUSH	CX                     ; 64B4  51
        MOV	AX, WORD PTR [BP+0EH]   ; 64B5  8b 46 0e
        DEC	AX                      ; 64B8  48
        ADD	AX, WORD PTR [1F94H]    ; 64B9  03 06 94 1f
        MOV	WORD PTR [1F96H], AX    ; 64BD  a3 96 1f
        MOV	CX, 8                   ; 64C0  b9 08 00
L64C3:  PUSH	CX                     ; 64C3  51
        MOV	AX, WORD PTR [BP+0CH]   ; 64C4  8b 46 0c
        DEC	AX                      ; 64C7  48
        ADD	AX, WORD PTR [1F90H]    ; 64C8  03 06 90 1f
        MOV	WORD PTR [1F92H], AX    ; 64CC  a3 92 1f
        TEST	DL, 80H                ; 64CF  f6 c2 80
        JE	L64F7                    ; 64D2  74 23
        PUSH	AX                     ; 64D4  50
        PUSH	BX                     ; 64D5  53
        PUSH	CX                     ; 64D6  51
        PUSH	DX                     ; 64D7  52
        PUSH	SI                     ; 64D8  56
        PUSH	WORD PTR [BP+10H]      ; 64D9  ff 76 10
        PUSH	WORD PTR [1F96H]       ; 64DC  ff 36 96 1f
        PUSH	WORD PTR [1F92H]       ; 64E0  ff 36 92 1f
        PUSH	WORD PTR [1F94H]       ; 64E4  ff 36 94 1f
        PUSH	WORD PTR [1F90H]       ; 64E8  ff 36 90 1f
        CALL	X6869                  ; 64EC  e8 7a 03
        ADD	SP, 0AH                 ; 64EF  83 c4 0a
        POP	SI                      ; 64F2  5e
        POP	DX                      ; 64F3  5a
        POP	CX                      ; 64F4  59
        POP	BX                      ; 64F5  5b
        POP	AX                      ; 64F6  58
L64F7:  MOV	AX, WORD PTR [1F92H]    ; 64F7  a1 92 1f
        INC	AX                      ; 64FA  40
        MOV	WORD PTR [1F90H], AX    ; 64FB  a3 90 1f
        ROL	DL, 1                   ; 64FE  d0 c2
        POP	CX                      ; 6500  59
        LOOP	L64C3                  ; 6501  e2 c0
        MOV	AX, WORD PTR [BP+8]     ; 6503  8b 46 08
        MOV	WORD PTR [1F90H], AX    ; 6506  a3 90 1f
        MOV	AX, WORD PTR [1F96H]    ; 6509  a1 96 1f
        INC	AX                      ; 650C  40
        MOV	WORD PTR [1F94H], AX    ; 650D  a3 94 1f
        POP	CX                      ; 6510  59
        LOOP	L64B3                  ; 6511  e2 a0
        MOV	AL, 8                   ; 6513  b0 08
        MOV	CX, WORD PTR [BP+0CH]   ; 6515  8b 4e 0c
        MUL	CL                      ; 6518  f6 e1
        ADD	WORD PTR [BP+8], AX     ; 651A  01 46 08
        JMP	L645D                   ; 651D  e9 3d ff
L6520:  POP	SI                      ; 6520  5e
        POP	ES                      ; 6521  07
        POP	BP                      ; 6522  5d
        RET                         ; 6523  c3

PROG    ENDS
        END
