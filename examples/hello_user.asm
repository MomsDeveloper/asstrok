INT:
    LD R1, 0
    ADD R1, 1
    ST R1, 0
    ST R2, R1

    JE R2, GREET
    RST

GREET:
    ; H
    SUB R1, R1
    ADD R1, 104
    OUT R1
    ; E
    SUB R1, R1
    ADD R1, 101
    OUT R1
    ; L
    SUB R1, R1
    ADD R1, 108
    OUT R1
    ; L
    SUB R1, R1
    ADD R1, 108
    OUT R1
    ; O
    SUB R1, R1
    ADD R1, 111
    OUT R1
    ; ,
    SUB R1, R1
    ADD R1, 44
    OUT R1
    ; SPACE
    SUB R1, R1
    ADD R1, 32
    OUT R1

PRINT_NAME:
    SUB R1, R1
    ADD R1, 1

    PRINT_CHAR:
        LD R2, R1
        OUT R2
        LD R2, 0
        SUB R2, 1
        ADD R1, 1
        ST R2, 0
        JE R2, END
        JMP PRINT_CHAR

END:
    HLT


START:
    ; W
    SUB R1, R1
    ADD R1, 87
    OUT R1
    ; H
    SUB R1, R1
    ADD R1, 72
    OUT R1
    ; O
    SUB R1, R1
    ADD R1, 79
    OUT R1
    ; ?
    SUB R1, R1
    ADD R1, 63
    OUT R1

    LOOP: JMP LOOP
