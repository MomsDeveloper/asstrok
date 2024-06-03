INT: RST
START:
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

    ; SPACE
    SUB R1, R1
    ADD R1, 32
    OUT R1

    ; W
    SUB R1, R1
    ADD R1, 119
    OUT R1

    ; O
    SUB R1, R1
    ADD R1, 111
    OUT R1

    ; R
    SUB R1, R1
    ADD R1, 114
    OUT R1

    ; L
    SUB R1, R1
    ADD R1, 108
    OUT R1

    ; D
    SUB R1, R1
    ADD R1, 100
    OUT R1

    ; !
    SUB R1, R1
    ADD R1, 33
    OUT R1

    ; NULL-TERMINATOR
    SUB R1, R1
    ADD R1, 0
    OUT R1

    ; HALT
    HLT
