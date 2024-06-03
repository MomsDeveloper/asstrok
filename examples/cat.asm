INT:
    OUT R2
    ST R2, 0
    RST

START:
    LD R1, 0
    JE R1, END
    JMP START

END:
    HLT
