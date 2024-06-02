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
from src.machine_signals import Signals

# class IOController:
#     input_buffer: list[tuple[int, int]]
#     output_buffer: list[int]

#     interaption_flag: bool

#     def __init__(self) -> None:
#         self.input_buffer = {}
#         self.output_buffer = []
#         self.interaption_flab = False

#     def set_interaption_flag(self) -> None:
#         self.interaption_flag = True

# cu = ControlUnit(Program(0, []), DataPath(256))
# queue = [("1", "h"), ("2", "h"), ("3", "h")]
# controller = IOController()
# for i in range(256):
#     if queue[0][0] < cu.tick:
#         controller.input_buffer[queue[0][0]] = queue[0][1]
#         queue.pop(0)
#         controller.set_interaption_flag()
#     cu.check_int_request()
#     #


class ControlUnit:
    # program memory
    program: Program
    program_counter: int
    data_path: DataPath
    _tick: int
    input_buffer: dict[int, int]
    output_buffer: list[int]

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

        elif isinstance(instr, ManagementInstruction):
            raise StopIteration()
        elif isinstance(instr, JumpEqInstruction):
            if self.data_path.zero_flag(instr.src):
                self.signal_latch_program_counter(Signals.JMP_ARG, instr)
            self.tick()
        elif isinstance(instr, CallInstruction):
            self.data_path.signal_latch_alu_l(
                Signals.LOAD_PC, self.program_counter)
            self.data_path.signal_latch_alu_r(Signals.LOAD_ARG, 0)
            self.data_path.execute_alu(Opcode.ADD)
            self.data_path.signal_write(Signals.SP_DEC)
            self.tick()

            self.signal_latch_program_counter(Signals.JMP_ARG, instr)
            self.tick()

        elif isinstance(instr, RetInstruction):
            self.data_path.signal_read(Signals.SP_INC)
            self.data_path.signal_latch_r1(Signals.MEM_DATA_OUT)
            self.data_path.signal_latch_alu_l(Signals.DATA_R1)
            self.data_path.signal_latch_alu_r(Signals.LOAD_ARG, 0)
            self.data_path.execute_alu(Opcode.ADD)
            self.program_counter = self.data_path.alu_out
            self.tick()
        else:
            return False
        return True

    def decode_and_execute_instruction(self, instr: Instruction) -> bool:
        if isinstance(instr, ArithmeticInstructionReg):
            match instr.arg_type:
                case ArgType.REG:
                    if instr.dest == Registers.R1:
                        self.data_path.signal_latch_alu_l(Signals.DATA_R1)
                        self.data_path.signal_latch_alu_r(Signals.DATA_R2)
                        self.data_path.execute_alu(instr.opcode)
                        self.data_path.signal_latch_r1(Signals.ALU_OUT)
                    else:
                        self.data_path.signal_latch_alu_l(Signals.DATA_R2)
                        self.data_path.signal_latch_alu_r(Signals.DATA_R1)
                        self.data_path.execute_alu(instr.opcode)
                        self.data_path.signal_latch_r2(Signals.ALU_OUT)
                    self.tick()
                case ArgType.IMM:
                    self.data_path.signal_latch_alu_l(Signals.DATA_R1)
                    self.data_path.signal_latch_alu_r(
                        Signals.LOAD_ARG, instr.src)
                    self.data_path.execute_alu(instr.opcode)
                    self.data_path.signal_latch_r1(Signals.ALU_OUT)
                    self.tick()
        elif isinstance(instr, IOMemoryInstruction):
            if instr.opcode == Opcode.LD:
                self.data_path.signal_read(Signals.INPUT_ADDR, instr.addr)
                if instr.src == Registers.R1:
                    self.data_path.signal_latch_r1(Signals.MEM_DATA_OUT)
                else:
                    self.data_path.signal_latch_r2(Signals.MEM_DATA_OUT)
                self.tick()
            elif instr.opcode == Opcode.ST:
                if instr.src == Registers.R1:
                    self.data_path.signal_latch_alu_l(Signals.DATA_R1)
                else:
                    self.data_path.signal_latch_alu_l(Signals.DATA_R2)
                self.data_path.signal_latch_alu_r(Signals.LOAD_ARG, 0)
                self.data_path.execute_alu(Opcode.ADD)
                self.data_path.signal_write(Signals.INPUT_ADDR, instr.addr)
                self.tick()
        elif isinstance(instr, IORstInstruction):
            # when we call interaption handler we store r1, r2, ip in stack
            # then we call handler of interaption which also store ip in stack
            # that is why we need to pop first value as it is reference to handler
            self.data_path.signal_read(Signals.SP_INC)
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
        else:
            return False

        return True

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
