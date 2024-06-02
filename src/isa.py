from __future__ import annotations

import struct
from dataclasses import dataclass
from enum import Enum
from typing import Literal, Protocol


class Opcode(Enum):
    # Arithmetic
    ADD = 0b0100
    SUB = 0b0101
    MUL = 0b0110
    DIV = 0b0111

    # Control
    JMP = 0b1000
    JE = 0b1001
    CALL = 0b1010
    RET = 0b1011

    # IO
    LD = 0b1100
    ST = 0b1101
    OUT = 0b1110
    RST = 0b1111

    # Management
    HLT = 0b0000

    def __str__(self) -> str:
        return self.name


class Registers(Enum):
    R1 = 0x0
    R2 = 0x1

    def __str__(self) -> str:
        return f"R{self.value + 1}"


class ArgType(Enum):
    REG = 0x0
    IMM = 0x1

    def __str__(self) -> str:
        return "REG" if self == ArgType.REG else "IMM"


@dataclass
class Instruction(Protocol):
    def pack(self) -> bytes:
        """Pack to 16-bit word."""


@dataclass
class ArithmeticInstruction(Instruction):
    opcode: Literal[Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV]
    dest: Registers
    src: int | Registers
    arg_type: ArgType


@dataclass
class ArithmeticInstructionReg(ArithmeticInstruction):
    opcode: Literal[Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV]
    src: Registers
    arg_type: Literal[ArgType.REG] = ArgType.REG
    
    def pack(self) -> bytes:
        packed_data = 0
        packed_data |= self.opcode.value << 12
        packed_data |= self.arg_type.value << 11
        packed_data |= self.dest.value << 10
        packed_data |= self.src.value << 9
        return struct.pack(">H", packed_data)


@dataclass
class ArithmeticInstructionImm(ArithmeticInstruction):
    opcode: Literal[Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV]
    src: int  # src must be between 0 and 0x3FF
    arg_type: Literal[ArgType.IMM] = ArgType.IMM

    def pack(self) -> bytes:
        packed_data = 0
        packed_data |= self.opcode.value << 12
        packed_data |= self.arg_type.value << 11
        packed_data |= self.dest.value << 10
        packed_data |= self.src & 0x3FF
        return struct.pack(">H", packed_data)


@dataclass
class ControlInstruction(Instruction):
    opcode: Literal[Opcode.JMP, Opcode.JE, Opcode.CALL, Opcode.RET]


@dataclass
class CallInstruction(ControlInstruction):
    opcode: Literal[Opcode.CALL]
    addr: int

    def pack(self) -> bytes:
        packed_data = 0
        packed_data |= self.opcode.value << 12
        packed_data |= 0x0 << 11
        packed_data |= self.addr & 0x3FF
        return struct.pack(">H", packed_data)


@dataclass
class RetInstruction(ControlInstruction):
    opcode: Literal[Opcode.RET]

    def pack(self) -> bytes:
        return struct.pack(">H", self.opcode.value << 12)


@dataclass
class JumpEqInstruction(ControlInstruction):
    opcode: Literal[Opcode.JE]
    src: Registers
    addr: int

    def pack(self) -> bytes:
        packed_data = 0
        packed_data |= self.opcode.value << 12
        packed_data |= self.src.value << 11
        packed_data |= self.addr & 0x3FF
        return struct.pack(">H", packed_data)


@dataclass
class JumpInstruction(ControlInstruction):
    opcode: Literal[Opcode.JMP]
    addr: int

    def pack(self) -> bytes:
        packed_data = 0
        packed_data |= self.opcode.value << 12
        packed_data | 0x0 << 11
        packed_data |= self.addr & 0x3FF
        return struct.pack(">H", packed_data)
    

@dataclass
class IOInstruction(Instruction):
    opcode: Literal[Opcode.LD, Opcode.ST, Opcode.OUT, Opcode.RST]


@dataclass
class IOMemoryInstruction(IOInstruction):
    opcode: Literal[Opcode.LD, Opcode.ST]
    src: Registers
    addr: int

    def pack(self) -> bytes:
        packed_data = 0
        packed_data |= self.opcode.value << 12
        packed_data |= self.src.value << 11
        packed_data |= self.addr & 0x3FF
        return struct.pack(">H", packed_data)


@dataclass
class IOOutInstruction(IOInstruction):
    opcode: Literal[Opcode.OUT]
    src: Registers

    def pack(self) -> bytes:
        packed_data = 0
        packed_data |= self.opcode.value << 12
        packed_data |= self.src.value << 11
        packed_data |= 0x0
        return struct.pack(">H", packed_data)


@dataclass
class IORstInstruction(IOInstruction):
    opcode: Literal[Opcode.RST]

    def pack(self) -> bytes:
        packed_data = 0
        packed_data |= self.opcode.value << 12
        return struct.pack(">H", packed_data)


@dataclass
class ManagementInstruction(Instruction):
    opcode: Literal[Opcode.HLT]

    def pack(self) -> bytes:
        return struct.pack(">H", self.opcode.value << 12)


def unpack(data: bytes) -> Instruction:
    # fukin' mypy cannot narrow literal using 'in {...}' syntax, 
    # so we end up with type ignores
    unpacked_data: int = struct.unpack(">H", data)[0]
    opcode = Opcode((unpacked_data >> 12) & 0x000F)
    if opcode in {Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV}:
        arg_type = ArgType((unpacked_data >> 11) & 0x0001)
        dest = Registers((unpacked_data >> 10) & 0x0001)
        if arg_type == ArgType.REG:
            src_reg = Registers((unpacked_data >> 9) & 0x0001)
            return ArithmeticInstructionReg(opcode, dest, src_reg)  # type: ignore
        else:
            src_imm = unpacked_data & 0x03FF
            return ArithmeticInstructionImm(opcode, dest, src_imm)  # type: ignore
    elif opcode == Opcode.CALL:
        addr = unpacked_data & 0x03FF
        return CallInstruction(opcode, addr)
    elif opcode == Opcode.RET:
        return RetInstruction(opcode)
    elif opcode == Opcode.JMP:
        addr = unpacked_data & 0x03FF
        return JumpInstruction(opcode, addr)
    elif opcode == Opcode.JE:
        src = Registers((unpacked_data >> 11) & 0x0001)
        addr = unpacked_data & 0x03FF
        return JumpEqInstruction(opcode, src, addr)
    elif opcode in {Opcode.LD, Opcode.ST}: 
        src = Registers((unpacked_data >> 11) & 0x0001)
        addr = unpacked_data & 0x03FF
        return IOMemoryInstruction(opcode, src, addr)  # type: ignore
    elif opcode == Opcode.OUT:
        src = Registers((unpacked_data >> 11) & 0x0001)
        return IOOutInstruction(opcode, src)
    elif opcode == Opcode.RST:
        return IORstInstruction(opcode)
    elif opcode == Opcode.HLT:
        return ManagementInstruction(opcode)
    else:
        raise ValueError(f"Unknown opcode: {opcode}")


@dataclass
class Program:
    entry: int  # start 16-bit address
    instructions: list[Instruction]


def pack_program(program: Program) -> bytes:
    # entry should be two bytes
    entry = struct.pack(">H", program.entry)
    instr = program.instructions
    # return b''.join(instr.pack() for instr in program)
    return entry + b''.join(instr.pack() for instr in instr)


def unpack_program(data: bytes) -> Program:
    entry = struct.unpack(">H", data[:2])[0]
    instructions = []
    i = 2
    while i < len(data):
        instr = unpack(data[i:i + 2])
        instructions.append(instr)
        i += 2
    return Program(entry, instructions)
