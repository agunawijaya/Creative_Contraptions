; snd1.asm -- DIBANGKITKAN oleh src_c/build/asmgen.py, lalu disunting tangan.
; Sumber: disassembly langsung CONTRAP_UNPACKED.EXE (bytenya sudah pasti).
;
;   5A5Bh  252 byte

        NAME    snd1

PGROUP  GROUP   PROG
DGROUP  GROUP   DATA

DATA    SEGMENT WORD PUBLIC 'DATA'
DATA    ENDS

PROG    SEGMENT BYTE PUBLIC 'PROG'
        ASSUME  CS:PGROUP, DS:DGROUP

        PUBLIC  rnd, sndrest, sndsave

rnd:    MOV	BX, SP                  ; 5A5B  8b dc
        MOV	AX, 3E85H               ; 5A5D  b8 85 3e
        MUL	WORD PTR DS:[71AH]      ; 5A60  f7 26 1a 07
        ADD	AX, 3619H               ; 5A64  05 19 36
        MOV	WORD PTR DS:[71AH], AX  ; 5A67  a3 1a 07
        MOV	AX, WORD PTR [BX+2]     ; 5A6A  8b 47 02
        MUL	WORD PTR DS:[71AH]      ; 5A6D  f7 26 1a 07
        MOV	AX, DX                  ; 5A71  8b c2
        RET                         ; 5A73  c3
        CLI                         ; 5A74  fa
        RET                         ; 5A75  c3
        STI                         ; 5A76  fb
        RET                         ; 5A77  c3
        SUB	AH, AH                  ; 5A78  2a e4
        INT	1AH                     ; 5A7A  cd 1a
        MOV	AX, DX                  ; 5A7C  8b c2
        RET                         ; 5A7E  c3
sndsave:PUSH	ES                     ; 5A7F  06
        CLI                         ; 5A80  fa
        MOV	AX, 0                   ; 5A81  b8 00 00
        MOV	ES, AX                  ; 5A84  8e c0
        MOV	DI, 70H                 ; 5A86  bf 70 00
        MOV	BX, SP                  ; 5A89  8b dc
        MOV	AX, WORD PTR SS:[BX+4]  ; 5A8B  36 8b 47 04
        MOV	CX, WORD PTR ES:[DI]    ; 5A8F  26 8b 0d
        MOV	WORD PTR DS:[1F00H], CX ; 5A92  89 0e 00 1f
        MOV	CX, WORD PTR ES:[DI+2]  ; 5A96  26 8b 4d 02
        MOV	WORD PTR DS:[1F02H], CX ; 5A9A  89 0e 02 1f
        MOV	WORD PTR ES:[DI], AX    ; 5A9E  26 89 05
        MOV	AX, CS                  ; 5AA1  8c c8
        MOV	WORD PTR ES:[DI+2], AX  ; 5AA3  26 89 45 02
        MOV	BX, WORD PTR DS:[71EH]  ; 5AA7  8b 1e 1e 07
        MOV	AX, 36H                 ; 5AAB  b8 36 00
        CALL	L5B23                  ; 5AAE  e8 72 00
        MOV	WORD PTR DS:[1F06H], 0FFFFH; 5AB1  c7 06 06 1f ff ff
        PUSH	DS                     ; 5AB7  1e
        MOV	AX, CS                  ; 5AB8  8c c8
        MOV	DS, AX                  ; 5ABA  8e d8
        MOV	DX, 5AF4H               ; 5ABC  ba f4 5a
        MOV	AL, 23H                 ; 5ABF  b0 23
        MOV	AH, 25H                 ; 5AC1  b4 25
        INT	21H                     ; 5AC3  cd 21
        POP	DS                      ; 5AC5  1f
        POP	ES                      ; 5AC6  07
        STI                         ; 5AC7  fb
        RET                         ; 5AC8  c3
sndrest:PUSH	ES                     ; 5AC9  06
        CLI                         ; 5ACA  fa
        MOV	AX, 0                   ; 5ACB  b8 00 00
        MOV	ES, AX                  ; 5ACE  8e c0
        MOV	DI, 70H                 ; 5AD0  bf 70 00
        MOV	BX, SP                  ; 5AD3  8b dc
        MOV	AX, WORD PTR DS:[1F00H] ; 5AD5  a1 00 1f
        MOV	WORD PTR ES:[DI], AX    ; 5AD8  26 89 05
        MOV	AX, WORD PTR DS:[1F02H] ; 5ADB  a1 02 1f
        MOV	WORD PTR ES:[DI+2], AX  ; 5ADE  26 89 45 02
        MOV	BX, 0FFFFH              ; 5AE2  bb ff ff
        MOV	AX, 36H                 ; 5AE5  b8 36 00
        CALL	L5B23                  ; 5AE8  e8 38 00
        MOV	WORD PTR DS:[1F06H], 0  ; 5AEB  c7 06 06 1f 00 00
        STI                         ; 5AF1  fb
        POP	ES                      ; 5AF2  07
        RET                         ; 5AF3  c3
        PUSH	AX                     ; 5AF4  50
        PUSH	DX                     ; 5AF5  52
        PUSH	DS                     ; 5AF6  1e
        CLI                         ; 5AF7  fa
        CMP	WORD PTR DS:[1F06H], 0  ; 5AF8  83 3e 06 1f 00
        JE	L5B0D                    ; 5AFD  74 0e
        MOV	DX, WORD PTR DS:[1F00H] ; 5AFF  8b 16 00 1f
        MOV	DS, WORD PTR DS:[1F02H] ; 5B03  8e 1e 02 1f
        MOV	AL, 1CH                 ; 5B07  b0 1c
        MOV	AH, 25H                 ; 5B09  b4 25
        INT	21H                     ; 5B0B  cd 21
L5B0D:  MOV	AX, 5                   ; 5B0D  b8 05 00
        INT	10H                     ; 5B10  cd 10
        IN	AL, 61H                  ; 5B12  e4 61
        AND	AL, 0FCH                ; 5B14  24 fc
        OUT	61H, AL                 ; 5B16  e6 61
        SUB	AL, AL                  ; 5B18  2a c0
        MOV	AH, 4CH                 ; 5B1A  b4 4c
        INT	21H                     ; 5B1C  cd 21
        POP	DS                      ; 5B1E  1f
        POP	DX                      ; 5B1F  5a
        POP	AX                      ; 5B20  58
        STI                         ; 5B21  fb
        IRET                        ; 5B22  cf
L5B23:  OUT	43H, AL                 ; 5B23  e6 43
        MOV	DX, 40H                 ; 5B25  ba 40 00
        ADD	DL, AH                  ; 5B28  02 d4
        MOV	AL, BL                  ; 5B2A  8a c3
        OUT	DX, AL                  ; 5B2C  ee
        PUSH	DX                     ; 5B2D  52
        POP	DX                      ; 5B2E  5a
        MOV	AL, BH                  ; 5B2F  8a c7
        OUT	DX, AL                  ; 5B31  ee
        RET                         ; 5B32  c3
        PUSH	AX                     ; 5B33  50
        MOV	AL, CL                  ; 5B34  8a c1
        OUT	42H, AL                 ; 5B36  e6 42
        MOV	AL, CH                  ; 5B38  8a c5
        OUT	42H, AL                 ; 5B3A  e6 42
        POP	AX                      ; 5B3C  58
        RET                         ; 5B3D  c3
        PUSH	AX                     ; 5B3E  50
        CMP	WORD PTR DS:[83CH], 0   ; 5B3F  83 3e 3c 08 00
        JE	L5B4C                    ; 5B44  74 06
        IN	AL, 61H                  ; 5B46  e4 61
        OR	AL, 3                    ; 5B48  0c 03
        OUT	61H, AL                 ; 5B4A  e6 61
L5B4C:  POP	AX                      ; 5B4C  58
        RET                         ; 5B4D  c3
        PUSH	AX                     ; 5B4E  50
        IN	AL, 61H                  ; 5B4F  e4 61
        AND	AL, 0FCH                ; 5B51  24 fc
        OUT	61H, AL                 ; 5B53  e6 61
        POP	AX                      ; 5B55  58
        RET                         ; 5B56  c3

PROG    ENDS
        END
