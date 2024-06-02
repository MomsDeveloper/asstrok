import pytest

from src.compiler import compile
from src.isa import (
    ArithmeticInstructionImm,
    ArithmeticInstructionReg,
    CallInstruction,
    IOMemoryInstruction,
    IOOutInstruction,
    JumpEqInstruction,
    JumpInstruction,
    Opcode,
    Program,
    Registers,
    RetInstruction,
)

test_compile_cases = [
    (
        """
        START:
        ADD R1 R1
        INT: ADD R1 R1   
        """,
        Program(
            entry=1,
            instructions=[
                CallInstruction(Opcode.CALL, 2),
                ArithmeticInstructionReg(Opcode.ADD, Registers.R1, Registers.R1),
                ArithmeticInstructionReg(Opcode.ADD, Registers.R1, Registers.R1),
            ]
        )
    ),
    (
        """
        LD R2, 10
        ADD R2, 4
        START:
        ADD R1, R2
        INT: SUB R2, 1
        JMP START
        """,
        Program(
            entry=3,
            instructions=[
                CallInstruction(Opcode.CALL, 4),
                IOMemoryInstruction(Opcode.LD, Registers.R2, 10),
                ArithmeticInstructionImm(Opcode.ADD, Registers.R2, 4),
                ArithmeticInstructionReg(Opcode.ADD, Registers.R1, Registers.R2),
                ArithmeticInstructionImm(Opcode.SUB, Registers.R2, 1),
                JumpInstruction(Opcode.JMP, 3),
            ]
        )
    ),
    (
        """
        INT:
        ; LD R1, 10
        ST: RET
        START:
            LD R1, 10
            LD R2, 20
            ADD R1, R2
            ST R1, 30
            OUT R1
            OUT R2
            JE R1, ST
        """,
        Program(
            entry=2,
            instructions=[
                CallInstruction(Opcode.CALL, 1),
                RetInstruction(Opcode.RET),
                IOMemoryInstruction(Opcode.LD, Registers.R1, 10),
                IOMemoryInstruction(Opcode.LD, Registers.R2, 20),
                ArithmeticInstructionReg(Opcode.ADD, Registers.R1, Registers.R2),
                IOMemoryInstruction(Opcode.ST, Registers.R1, 30),
                IOOutInstruction(Opcode.OUT, Registers.R1),
                IOOutInstruction(Opcode.OUT, Registers.R2),
                JumpEqInstruction(Opcode.JE, Registers.R1, 1),
            ]
        )

    ),
    (
        """
        INT:
        ; LD R1, 10
        ST: 
        RET
        START:
            LD R1, 10
            LD R2, 20
            ADD R1, R2
            ST R1, 30
            OUT R1
            ; OUT R2
            OUT R2
            JE R1, START
        """,
        Program(
            entry=2,
            instructions=[
                CallInstruction(Opcode.CALL, 1),
                RetInstruction(Opcode.RET),
                IOMemoryInstruction(Opcode.LD, Registers.R1, 10),
                IOMemoryInstruction(Opcode.LD, Registers.R2, 20),
                ArithmeticInstructionReg(Opcode.ADD, Registers.R1, Registers.R2),
                IOMemoryInstruction(Opcode.ST, Registers.R1, 30),
                IOOutInstruction(Opcode.OUT, Registers.R1),
                IOOutInstruction(Opcode.OUT, Registers.R2),
                JumpEqInstruction(Opcode.JE, Registers.R1, 2),
            ]
        )
    ),
]


@pytest.mark.parametrize(
    argnames=("code", "expected"),
    argvalues=test_compile_cases,
)
def test_compile(code: str, expected: Program) -> None:
    assert compile(code) == expected
