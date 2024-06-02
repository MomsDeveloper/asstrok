SM: LD R1, 0
INT: 
    ADD R1, 666
    ST R2, 0
    RST

ADD R2, 4
START:
    ADD R1, 10
    SUB R2, 1
    ADD R1, R2
    LD R2, 0
    OUT R2
    JE R2, START
    HLT
