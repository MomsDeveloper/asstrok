import sys
from pathlib import Path
from typing import Dict, List, Tuple

from src.isa import (
    ArithmeticInstructionImm,
    ArithmeticInstructionReg,
    CallInstruction,
    Instruction,
    IOMemoryInstructionImm,
    IOMemoryInstructionReg,
    IOOutInstruction,
    IORstInstruction,
    JumpEqInstruction,
    JumpInstruction,
    ManagementInstruction,
    Opcode,
    Program,
    Registers,
    RetInstruction,
    pack_program,
)


def get_meaningful_token(line: str) -> str:
    return line.split(";", 1)[0].strip()


def extract_labels(lines: List[str]) -> Tuple[List[str], Dict[str, int], int]:
    labels: Dict[str, int] = {}
    clean_lines: List[str] = []
    # entry point of the program
    start = 0

    for line in lines:
        line = get_meaningful_token(line)
        if not line:
            continue

        pc = len(clean_lines)
        parts = line.split()
        # If the line store the label and the instruction
        if parts[0].endswith(":") and len(parts) > 1:
            label = parts[0][:-1]
            assert label not in labels, f"Label {label} already defined"
            labels[label] = pc
            clean_lines.append(" ".join(parts[1:]))
            start = pc if parts[0] == "START:" else start
        # If the line store only the label
        elif parts[0].endswith(":"):
            label = parts[0][:-1]
            assert label not in labels, f"Label {label} already defined"
            labels[label] = pc
            start = pc if parts[0] == "START:" else start
        else:
            clean_lines.append(line)

    return clean_lines, labels, start


LabelsMap = Dict[str, int]


def replace_labels_with_addresses(
    lines: List[str],
    labels: LabelsMap,
) -> List[str]:
    replaced_lines = []

    for line in lines:
        parts = line.split()
        if parts[0] in {"JMP", "JE", "CALL"} and parts[-1] in labels:
            parts[-1] = str(labels[parts[-1]])
        elif parts[0] not in {"JMP", "JE", "CALL"} and parts[-1] in labels:
            raise ValueError(
                f"Label {parts[-1]} is not allowed with {parts[0]}")
        replaced_lines.append(" ".join(parts))

    return replaced_lines


def parse_instructions(lines: List[str], start: int) -> Program:
    program: List[Instruction] = []
    for line in lines:
        parts = [
            part.strip(",")
            for part in line.strip().split()
        ]
        if not parts or parts[0].startswith(';'):
            continue  # Skip empty lines and comments

        opcode = Opcode[parts[0]]
        if opcode in {Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV}:
            dest = Registers[parts[1]]
            if parts[2] in {"R1", "R2"}:
                src = Registers[parts[2]]
                program.append(ArithmeticInstructionReg(
                    opcode, dest, src))  # type: ignore
            else:
                program.append(ArithmeticInstructionImm(
                    opcode, dest, int(parts[2])))  # type: ignore
        elif opcode == Opcode.RET:
            program.append(RetInstruction(opcode))
        elif opcode == Opcode.CALL:
            addr = int(parts[1])
            program.append(CallInstruction(opcode, addr))
        elif opcode == Opcode.JMP:
            addr = int(parts[1])
            program.append(JumpInstruction(opcode, addr))
        elif opcode == Opcode.JE:
            src = Registers[parts[1]]
            addr = int(parts[2])
            program.append(JumpEqInstruction(opcode, src, addr))
        elif opcode in {Opcode.LD, Opcode.ST}:
            dest = Registers[parts[1]]
            if parts[2] in {"R1", "R2"}:
                r = Registers[parts[2]]
                program.append(IOMemoryInstructionReg(opcode, dest, r))  # type: ignore
            else:
                addr = int(parts[2])
                program.append(IOMemoryInstructionImm(opcode, dest, addr))  # type: ignore

        elif opcode == Opcode.OUT:
            src = Registers[parts[1]]
            program.append(IOOutInstruction(opcode, src))
        elif opcode == Opcode.HLT:
            program.append(ManagementInstruction(opcode))
        elif opcode == Opcode.RST:
            program.append(IORstInstruction(opcode))
        else:
            raise ValueError(f"Unknown opcode: {parts[0]} at:\n{line}")

    return Program(start, program)


def compile(source: str) -> Program:
    lines = source.splitlines()
    lines.insert(0, "CALL INT")
    clean_lines, labels, start = extract_labels(lines)
    if "INT" and "START" not in labels:
        raise ValueError("INT and START labels are required")

    replaced_lines = replace_labels_with_addresses(clean_lines, labels)
    return parse_instructions(replaced_lines, start)


def main(source_path: Path, output_path: Path) -> None:
    with source_path.open() as f:
        source = f.read()

    program = compile(source)
    output_path.write_bytes(pack_program(program))


if __name__ == "__main__":
    assert len(sys.argv) == 2, "Usage: python compiler.py <source.asm>"
    path = Path(sys.argv[1])
    output = path.with_suffix(".bin")
    main(path, output)
