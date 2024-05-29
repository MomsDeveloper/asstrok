from dataclasses import dataclass
from pathlib import Path
from struct import unpack
from src.isa import Opcode, pack_program
from src.isa import Program
import sys


def get_meaningful_token(line: str) -> str:
    return line.split(";", 1)[0].strip()

def compile(source_path: str) -> Program:
    line = 0
    pos = 0
    return []


def main(source_path: Path, output_path: Path) -> None:
    source = ""
    with open(source_path, encoding="utf-8") as f:
        source = f.read()

    program: Program = compile(source) 

    output_path.write_bytes(pack_program(program))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise AssertionError("Wrong arguments: compiler.py <input_file> <target_file>")
    
    source_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    main(source_path, output_path)