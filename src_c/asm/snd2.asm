; snd2.asm -- DIBANGKITKAN oleh src_c/build/asmgen.py, lalu disunting tangan.
; Sumber: disassembly langsung CONTRAP_UNPACKED.EXE (bytenya sudah pasti).
;
;   5B57h  356 byte

        NAME    snd2

PGROUP  GROUP   PROG
DGROUP  GROUP   DATA

DATA    SEGMENT WORD PUBLIC 'DATA'
DATA    ENDS

PROG    SEGMENT BYTE PUBLIC 'PROG'
        ASSUME  CS:PGROUP, DS:DGROUP

        PUBLIC  L5B57, refresh, tone3
        EXTRN   sndb:NEAR
        EXTRN   sndc:NEAR
        EXTRN   sndd:NEAR
        EXTRN   vbwait:NEAR
        EXTRN   vbend:NEAR

L5B57:  PUSH	DX                     ; 5B57  52
        PUSH	AX                     ; 5B58  50
        CMP	CX, 0                   ; 5B59  83 f9 00
        JE	L5B6D                    ; 5B5C  74 0f
        CALL	sndc                   ; 5B5E  e8 dd ff
        MOV	DX, 12H                 ; 5B61  ba 12 00
        MOV	AX, 34DEH               ; 5B64  b8 de 34
        DIV	CX                      ; 5B67  f7 f1
        MOV	CX, AX                  ; 5B69  8b c8
        JMP	SHORT L5B70             ; 5B6B  eb 03
L5B6D:  CALL	sndd                   ; 5B6D  e8 de ff
L5B70:  POP	AX                      ; 5B70  58
        POP	DX                      ; 5B71  5a
        RET                         ; 5B72  c3
tone3:  PUSH	AX                     ; 5B73  50
        PUSH	BX                     ; 5B74  53
        PUSH	CX                     ; 5B75  51
        PUSH	DX                     ; 5B76  52
        MOV	AX, DS                  ; 5B77  8c d8
        PUSH	AX                     ; 5B79  50
        MOV	AX, DGROUP                ; 5B7A  b8 07 09   <- SEG, bukan literal
        MOV	DS, AX                  ; 5B7D  8e d8
        MOV	DX, 0                   ; 5B7F  ba 00 00
        CMP	WORD PTR DS:[83CH], DX  ; 5B82  39 16 3c 08
        JNE	L5B8B                   ; 5B86  75 03
        CALL	sndd                   ; 5B88  e8 c3 ff
L5B8B:  CMP	WORD PTR DS:[720H], DX  ; 5B8B  39 16 20 07
        JE	L5BBE                    ; 5B8F  74 2d
        MOV	AX, WORD PTR DS:[720H]  ; 5B91  a1 20 07
        MOV	WORD PTR DS:[1EF6H], AX ; 5B94  a3 f6 1e
        MOV	WORD PTR DS:[1EF8H], AX ; 5B97  a3 f8 1e
        MOV	WORD PTR DS:[720H], DX  ; 5B9A  89 16 20 07
        MOV	AX, WORD PTR DS:[722H]  ; 5B9E  a1 22 07
        MOV	WORD PTR DS:[1EFAH], AX ; 5BA1  a3 fa 1e
        MOV	WORD PTR DS:[722H], DX  ; 5BA4  89 16 22 07
        CMP	AX, DX                  ; 5BA8  3b c2
        JNE	L5BBB                   ; 5BAA  75 0f
        CALL	sndd                   ; 5BAC  e8 9f ff
        MOV	WORD PTR DS:[1EFEH], 0  ; 5BAF  c7 06 fe 1e 00 00
        MOV	WORD PTR DS:[1EF6H], DX ; 5BB5  89 16 f6 1e
        JMP	SHORT L5BBE             ; 5BB9  eb 03
L5BBB:  CALL	sndc                   ; 5BBB  e8 80 ff
L5BBE:  MOV	AX, WORD PTR DS:[1EFAH] ; 5BBE  a1 fa 1e
        CMP	AX, 1                   ; 5BC1  3d 01 00
        JNE	L5BC9                   ; 5BC4  75 03
        JMP	L5C50                   ; 5BC6  e9 87 00
L5BC9:  CMP	AX, 2                   ; 5BC9  3d 02 00
        JE	L5BE7                    ; 5BCC  74 19
        CMP	AX, 3                   ; 5BCE  3d 03 00
        JE	L5BDF                    ; 5BD1  74 0c
        CALL	sndd                   ; 5BD3  e8 78 ff
        MOV	WORD PTR DS:[1EFEH], 0  ; 5BD6  c7 06 fe 1e 00 00
        JMP	L5C7C                   ; 5BDC  e9 9d 00
L5BDF:  MOV	WORD PTR DS:[1EFCH], 1  ; 5BDF  c7 06 fc 1e 01 00
        JMP	SHORT L5BEB             ; 5BE5  eb 04
L5BE7:  MOV	WORD PTR DS:[1EFCH], DX ; 5BE7  89 16 fc 1e
L5BEB:  CMP	WORD PTR DS:[1EFEH], DX ; 5BEB  39 16 fe 1e
        JNE	L5C3C                   ; 5BEF  75 4b
        MOV	BX, WORD PTR DS:[1EF6H] ; 5BF1  8b 1e f6 1e
        MOV	CX, WORD PTR [BX]       ; 5BF5  8b 0f
        MOV	AL, BYTE PTR [BX+2]     ; 5BF7  8a 47 02
        ADD	WORD PTR DS:[1EF6H], 3  ; 5BFA  83 06 f6 1e 03
        DB      81H,0F9H,0FFH,0FFH  ; 5BFF  81 f9 ff ff  ;; DB: MASM akan memendekkannya
        JNE	L5C1A                   ; 5C03  75 15
        CMP	WORD PTR DS:[1EFCH], 1  ; 5C05  83 3e fc 1e 01
        JNE	L5C28                   ; 5C0A  75 1c
        MOV	BX, WORD PTR DS:[1EF8H] ; 5C0C  8b 1e f8 1e
        MOV	WORD PTR DS:[1EF6H], BX ; 5C10  89 1e f6 1e
        MOV	WORD PTR DS:[1EFEH], DX ; 5C14  89 16 fe 1e
        JMP	SHORT L5BEB             ; 5C18  eb d1
L5C1A:  SUB	AH, AH                  ; 5C1A  2a e4
        MOV	WORD PTR DS:[1EFEH], AX ; 5C1C  a3 fe 1e
        CALL	L5B57                  ; 5C1F  e8 35 ff
        CALL	sndb                   ; 5C22  e8 0e ff
        JMP	SHORT L5C3C             ; 5C25  eb 15
        NOP                         ; 5C27  90
L5C28:  CALL	sndd                   ; 5C28  e8 23 ff
        MOV	WORD PTR DS:[1EFEH], 0  ; 5C2B  c7 06 fe 1e 00 00
        MOV	WORD PTR DS:[1EF6H], DX ; 5C31  89 16 f6 1e
        MOV	WORD PTR DS:[1EFAH], DX ; 5C35  89 16 fa 1e
        JMP	SHORT L5C7C             ; 5C39  eb 41
        NOP                         ; 5C3B  90
L5C3C:  DEC	WORD PTR DS:[1EFEH]     ; 5C3C  ff 0e fe 1e
        CMP	WORD PTR DS:[1EFEH], 0  ; 5C40  83 3e fe 1e 00
        JG	L5C7C                    ; 5C45  7f 35
        MOV	WORD PTR DS:[1EFEH], 0  ; 5C47  c7 06 fe 1e 00 00
        JMP	SHORT L5C7C             ; 5C4D  eb 2d
        NOP                         ; 5C4F  90
L5C50:  MOV	BX, WORD PTR DS:[1EF6H] ; 5C50  8b 1e f6 1e
        MOV	CX, WORD PTR [BX]       ; 5C54  8b 0f
        MOV	AX, WORD PTR [BX+2]     ; 5C56  8b 47 02
        CMP	AX, CX                  ; 5C59  3b c1
        JNE	L5C71                   ; 5C5B  75 14
        CALL	sndd                   ; 5C5D  e8 ee fe
        MOV	WORD PTR DS:[1EFEH], 0  ; 5C60  c7 06 fe 1e 00 00
        MOV	WORD PTR DS:[1EF6H], DX ; 5C66  89 16 f6 1e
        MOV	WORD PTR DS:[1EFAH], DX ; 5C6A  89 16 fa 1e
        JMP	SHORT L5C7C             ; 5C6E  eb 0c
        NOP                         ; 5C70  90
L5C71:  CALL	L5B57                  ; 5C71  e8 e3 fe
        CALL	sndb                   ; 5C74  e8 bc fe
        MOV	AX, WORD PTR [BX+4]     ; 5C77  8b 47 04
        ADD	WORD PTR [BX], AX       ; 5C7A  01 07
L5C7C:  POP	AX                      ; 5C7C  58
        MOV	DS, AX                  ; 5C7D  8e d8
        POP	DX                      ; 5C7F  5a
        POP	CX                      ; 5C80  59
        POP	BX                      ; 5C81  5b
        POP	AX                      ; 5C82  58
        RET                         ; 5C83  c3
refresh:CMP	WORD PTR DS:[1F04H], 0  ; 5C84  83 3e 04 1f 00
        JNE	L5C97                   ; 5C89  75 0c
        MOV	WORD PTR DS:[1F04H], 1  ; 5C8B  c7 06 04 1f 01 00
        MOV	CX, 258H                ; 5C91  b9 58 02
        JMP	SHORT L5CA0             ; 5C94  eb 0a
        NOP                         ; 5C96  90
L5C97:  MOV	WORD PTR DS:[1F04H], 0  ; 5C97  c7 06 04 1f 00 00
        MOV	CX, 244H                ; 5C9D  b9 44 02
L5CA0:  CALL	L5B57                  ; 5CA0  e8 b4 fe
        CALL	sndb                   ; 5CA3  e8 8d fe
        CALL	vbend                  ; 5CA6  e8 f8 00
        CALL	sndc                   ; 5CA9  e8 92 fe
        MOV	CX, 8                   ; 5CAC  b9 08 00
L5CAF:  CALL	vbwait                 ; 5CAF  e8 e6 00
        CALL	vbend                  ; 5CB2  e8 ec 00
        LOOP	L5CAF                  ; 5CB5  e2 f8
        CALL	sndd                   ; 5CB7  e8 94 fe
        RET                         ; 5CBA  c3

PROG    ENDS
        END
