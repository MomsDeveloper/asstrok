from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import Enum


class Opcode(Enum):
    LD = 0x01
    ST = 0x02
    ADD = 0x03
    SUB = 0x04
    JMP = 0x05
    JZ = 0x06
    IN = 0x07
    OUT = 0x08
    HLT = 0x09

    def __str__(self) -> str:
        return str(self.value)


@dataclass
class Instruction:
    opcode: Opcode
    reg: int
    value: int

    def pack(self) -> bytes:
        return struct.pack('BBB', self.opcode.value, self.reg, self.value)

    @classmethod
    def unpack(cls, data: bytes) -> Instruction:
        opcode, reg, value = struct.unpack('BBB', data)
        return cls(Opcode(opcode), reg, value)


Program = list[Instruction]


def pack_program(program: Program) -> bytes:
    return b''.join(instr.pack() for instr in program)
