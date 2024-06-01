from pathlib import Path
from typing import Optional

from src.compiler import main as write
from src.datapath import DataPath
from src.isa import (
    ArgType,
    ArithmeticInstructionImm,
    ArithmeticInstructionReg,
    CallInstruction,
    Instruction,
    IOMemoryInstruction,
    IOOutInstruction,
    JumpEqInstruction,
    JumpInstruction,
    ManagementInstruction,
    Opcode,
    Program,
    Registers,
    RetInstruction,
    pack_program,
)
from src.machine_signals import Signals


class ControlUnit:
    # program memory
    program: Program

    program_counter: int

    data_path: DataPath

    _tick: int

    def __init__(self, program: Program, data_path: DataPath) -> None:
        self.program = program
        self.data_path = data_path
        self.program_counter = 0
        self._tick = 0
    
    def tick(self) -> None:
        self._tick += 1
    
    def signal_latch_program_counter(
        self, 
        sel: Signals, 
        instr: Optional[Instruction] = None
    ) -> None:
        match sel:
            case Signals.PUT_DATA:
                self.program_counter = self.data_path.alu_out
                pass
            case Signals.JMP_ARG:
                assert isinstance(instr, (JumpInstruction, JumpEqInstruction, 
                                         CallInstruction))
                self.program_counter = instr.addr
            case Signals.NEXT_IP:
                self.program_counter += 1
    
    def decode_and_execute_control_flow_instruction(self, instr: Instruction) -> bool:
        if isinstance(instr, JumpInstruction):
            self.signal_latch_program_counter(Signals.JMP_ARG, instr)
            self.tick()

            return True
        elif isinstance(instr, ManagementInstruction):
            raise StopIteration()
        elif isinstance(instr, JumpEqInstruction):
            if self.data_path.zero_flag(instr.src):
                self.signal_latch_program_counter(Signals.JMP_ARG, instr)
            self.tick()
            return True
        elif isinstance(instr, CallInstruction):
            self.data_path.signal_latch_alu_l(Signals.DATA_R1)
            self.data_path.signal_latch_alu_r(Signals.LOAD_ARG, 0)
            self.data_path.execute_alu(Opcode.ADD)
            self.data_path.signal_write(Signals.SP_DEC)
            self.tick()

            self.data_path.signal_latch_alu_l(Signals.DATA_R2)
            self.data_path.signal_latch_alu_r(Signals.LOAD_ARG, 0)
            self.data_path.execute_alu(Opcode.ADD)
            self.data_path.signal_write(Signals.SP_DEC)
            self.tick()

            self.data_path.signal_latch_alu_l(Signals.LOAD_PC, self.program_counter)
            self.data_path.signal_latch_alu_r(Signals.LOAD_ARG, 0)
            self.data_path.execute_alu(Opcode.ADD)
            self.data_path.signal_write(Signals.SP_DEC)
            self.tick()

            self.signal_latch_program_counter(Signals.JMP_ARG, instr)
            self.tick()

            return True
        elif isinstance(instr, RetInstruction):
            self.data_path.signal_read(Signals.SP_INC)
            self.data_path.signal_latch_r1(Signals.MEM_DATA_OUT)
            self.data_path.signal_latch_alu_l(Signals.DATA_R1)
            self.data_path.signal_latch_alu_r(Signals.LOAD_ARG, 0)
            self.data_path.execute_alu(Opcode.ADD)
            self.program_counter = self.data_path.alu_out
            self.tick()

            self.data_path.signal_read(Signals.SP_INC)
            self.data_path.signal_latch_r2(Signals.MEM_DATA_OUT)
            self.tick()

            self.data_path.signal_read(Signals.SP_INC)
            self.data_path.signal_latch_r1(Signals.MEM_DATA_OUT)
            self.tick()
            
            return True
        else:
            return False

    # def decode_and_execute_instruction(self, instr: Instruction) -> None:
    #     if instr.opcode == Opcode.ADD:
    #         self.data_path.add(instr.dest, instr.src)

    def check_int_request(self) -> None:
        pass


def main(code_file: Path) -> None:
    # read code_file and decode each instruction using unpack

    # with code_file.open("rb") as f:
    #     source = f.read()
    
    # program = unpack_program(source)

    # for instr in program.instructions:
    # print(instr)
        
    # control_unit = ControlUnit(program, DataPath(256))
    pass


if __name__ == "__main__":
    path = Path("examples/my_program.asm")
    # compiled = compile(path.read_text())
    output = path.with_suffix(".bin")
    write(path, output)
    compiled_path = path.with_suffix(".bin")
    main(compiled_path)