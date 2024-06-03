; If we list all the natural numbers below 10 that are multiples of 3 or 5, we get 3, 5, 6 and 9. The sum of these multiples is 23.
; Find the sum of all the multiples of 3 or 5 below 1000.
; THERE ONLY R1 AND R2 REGISTERS
; DOES NOT SUPPORT MOD, ONLY ADD, SUB, MUL, DIV
; DOES NOT SUPPORT MOV

INT: RST

START:
    ; 0 CELL IS THE SUM

    ; SET LOOP COUNTER TO 1000
    SUB R2, R2
    ADD R2, 1000

    LOOP:
        ; DECREMENT LOOP COUNTER
        SUB R2, 1

        ; IF LOOP COUNTER IS 0, EXIT
        JE R2, END

        ; CHECK IF LOOP COUNTER IS MULTIPLE OF 3
        SUB R1, R1
        ADD R1, R2
        DIV R1, 3
        MUL R1, 3
        SUB R1, R2
        JE R1, ADD_TO_SUM

        ; CHECK IF LOOP COUNTER IS MULTIPLE OF 5
        SUB R1, R1
        ADD R1, R2
        DIV R1, 5
        MUL R1, 5
        SUB R1, R2
        JE R1, ADD_TO_SUM

        ; IF NOT MULTIPLE OF 3 OR 5, CONTINUE LOOP
        JMP LOOP

    ADD_TO_SUM:
        ; ADD LOOP COUNTER TO SUM
        LD R1, 0
        ADD R1, R2
        ST R1, 0
        JMP LOOP

    END:
        ; PRINT SUM
        LD R1, 0
        OUT R1
        HLT
