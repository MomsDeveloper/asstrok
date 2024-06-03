import struct

import pytest

from src.isa import (
    ArithmeticInstructionImm,
    ArithmeticInstructionReg,
    Instruction,
    IOMemoryInstructionImm,
    IOMemoryInstructionReg,
    IOOutInstruction,
    JumpEqInstruction,
    JumpInstruction,
    ManagementInstruction,
    Opcode,
    Registers,
    unpack,
)

test_instruction_packing_cases = [
    (
        ArithmeticInstructionReg(Opcode.ADD, Registers.R1, Registers.R1), 
        struct.pack(">H", 0b0100_0000_0000_0000),
    ),
    (
        ArithmeticInstructionReg(Opcode.SUB, Registers.R1, Registers.R2),
        struct.pack(">H", 0b0101_0010_0000_0000),
    ),
    (
        ArithmeticInstructionReg(Opcode.MUL, Registers.R2, Registers.R1),
        struct.pack(">H", 0b0110_0100_0000_0000),
    ),
    (
        ArithmeticInstructionReg(Opcode.DIV, Registers.R2, Registers.R2),
        struct.pack(">H", 0b0111_0110_0000_0000),
    ),
    (
        ArithmeticInstructionImm(Opcode.ADD, Registers.R1, 0x1),
        struct.pack(">H", 0b0100_1000_0000_0001),
    ),
    (
        ArithmeticInstructionImm(Opcode.SUB, Registers.R2, 0x3FF),
        struct.pack(">H", 0b0101_1111_1111_1111),
    ),
    (
        JumpInstruction(Opcode.JMP, 0x1),
        struct.pack(">H", 0b1000_0000_0000_0001),
    ),
    (
        JumpEqInstruction(Opcode.JE, Registers.R1, 0x3FF),
        struct.pack(">H", 0b1001_0011_1111_1111),
    ),
    (
        JumpEqInstruction(Opcode.JE, Registers.R2, 0x11),
        struct.pack(">H", 0b1001_1000_0001_0001),
    ),
    (
        ManagementInstruction(Opcode.HLT),
        struct.pack(">H", 0b0000_0000_0000_0000),
    ),
    (
        IOMemoryInstructionReg(Opcode.LD, Registers.R1, Registers.R1),
        struct.pack(">H", 0b1100_0000_0000_0000),
    ),
    (
        IOMemoryInstructionReg(Opcode.ST, Registers.R2, Registers.R2),
        struct.pack(">H", 0b1101_0110_0000_0000),
    ),
    (
        IOMemoryInstructionImm(Opcode.LD, Registers.R1, 0x1),
        struct.pack(">H", 0b1100_1000_0000_0001),
    ),
    (
        IOMemoryInstructionImm(Opcode.ST, Registers.R2, 0x3FF),
        struct.pack(">H", 0b1101_1111_1111_1111),
    ),
    (
        IOOutInstruction(Opcode.OUT, Registers.R1),
        struct.pack(">H", 0b1110_0000_0000_0000),
    ),
]


@pytest.mark.parametrize(
    argnames=("instr", "expected"),
    argvalues=test_instruction_packing_cases, 
    ids=[str(instr) for instr, _ in test_instruction_packing_cases]
)
def test_instruction_packing_successful(instr: Instruction, expected: bytes) -> None:
    assert instr.pack() == expected
    assert instr == unpack(expected)
