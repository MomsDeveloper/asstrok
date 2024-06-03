| Код операции | Формат инструкции |
|--------------|-------------------|
| `ADD`        | `0100 A D S/LIT`     |
| `SUB`        | `0101 A D S/LIT`     |
| `MUL`        | `0110 A D S/LIT`     |
| `DIV`        | `0111 A D S/LIT`     |

| `JMP`        | `1000 0 ADDR`        |
| `JE `        | `1001 R ADDR`        |
| `CALL`       | `1010 0 ADDR`        |
| `RET`        | `1011 0 ---`         |

| `LD`         | `1100 R ADDR`        |
| `ST`         | `1101 R ADDR`        |
| `OUT`        | `1110 R ---`         |
| `RST`        | `1111 ---`           |

| `HLT`        | `0000 ---`           |

A - выбор (r, r или r/lit) D - dest S - source LIT - literal
R - выбор регистра (0 или 1)
ADDR - адрес в памяти


ADD, SUB, MUL, DIV - First operand is one of the registers, second operand is either a register or a literal.

CALL, JMP - Single operand is either a literal address or a label.
JE - First operand is one of the registers, second operand is either a literal address or a label.

LD, ST - First operand is one of the registers, second operand is either a literal address or one of the registers.

OUT - Single operand is one of the registers.