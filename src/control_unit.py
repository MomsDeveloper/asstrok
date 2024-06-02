from typing import Optional

from src.datapath import DataPath
from src.io_controller import IOController
from src.isa import (
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
)
from src.machine_signals import Signals


class ControlUnit:

    program: Program
    data_path: DataPath
    controller: IOController

    program_counter: int
    _tick: int

    def __init__(
        self, program: Program, data_path: DataPath, controller: IOController
    ) -> None:
        self.program = program
        self.data_path = data_path
        self.controller = controller
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

    def decode_and_execute_instruction(self, instr: Instruction) -> None:
        if isinstance(instr, ArithmeticInstructionReg):
            self.data_path.signal_latch_alu_l(Signals.DATA_R1)
            self.data_path.signal_latch_alu_r(Signals.DATA_R2)
            self.data_path.execute_alu(instr.opcode)
            if instr.dest == Registers.R1:
                self.data_path.signal_latch_r1(Signals.ALU_OUT)
            else:
                self.data_path.signal_latch_r2(Signals.ALU_OUT)
            self.tick()
            self.signal_latch_program_counter(Signals.NEXT_IP)
        elif isinstance(instr, ArithmeticInstructionImm):
            self.data_path.signal_latch_alu_r(
                Signals.LOAD_ARG, instr.src)
            if instr.dest == Registers.R1:
                self.data_path.signal_latch_alu_l(Signals.DATA_R1)
                self.data_path.execute_alu(instr.opcode)
                self.data_path.signal_latch_r1(Signals.ALU_OUT)
            else:
                self.data_path.signal_latch_alu_l(Signals.DATA_R2)
                self.data_path.execute_alu(instr.opcode)
                self.data_path.signal_latch_r2(Signals.ALU_OUT)
            self.tick()
            self.signal_latch_program_counter(Signals.NEXT_IP)
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
            self.signal_latch_program_counter(Signals.NEXT_IP)
        elif isinstance(instr, IOOutInstruction):
            if instr.src == Registers.R1:
                self.data_path.signal_latch_alu_l(Signals.DATA_R1)
            else:
                self.data_path.signal_latch_alu_l(Signals.DATA_R2)
            self.data_path.signal_latch_alu_r(Signals.LOAD_ARG, 0)
            self.data_path.execute_alu(Opcode.ADD)
            self.controller.output_buffer.append(self.data_path.alu_out)
            self.tick()
            self.signal_latch_program_counter(Signals.NEXT_IP)
        if isinstance(instr, JumpInstruction):
            self.signal_latch_program_counter(Signals.JMP_ARG, instr)
            self.tick()

        elif isinstance(instr, ManagementInstruction):
            raise StopIteration()
        elif isinstance(instr, JumpEqInstruction):
            if self.data_path.zero_flag(instr.src):
                self.signal_latch_program_counter(Signals.JMP_ARG, instr)
            else:
                self.signal_latch_program_counter(Signals.NEXT_IP)
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

    def check_int_request(self) -> None:
        if self.controller.interruption_flag:
            self.controller.interruption_flag = False

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

            self.data_path.signal_latch_alu_l(
                Signals.LOAD_PC, self.program_counter
            )
            self.data_path.signal_latch_alu_r(Signals.LOAD_ARG, 0)
            self.data_path.execute_alu(Opcode.ADD)
            self.data_path.signal_write(Signals.SP_DEC)
            self.tick()

            self.program_counter = 0
            self.data_path.signal_latch_r2(
                Signals.INPUT, self.controller.input_buffer.pop(0)[1]
            )
            self.tick()
        
    def __repr__(self) -> str:
        datapath_repr = f"R1: {self.data_path.r1}\tR2: {self.data_path.r2}\tSP: {self.data_path.stack_pointer}"  # noqa: E501
        cu_repr = f"TICK: {self._tick}\tPC: {self.program_counter}"
        instr_repr = self.program.instructions[self.program_counter]
        stack_repr = f"STACK: {
            self.data_path.data_memory[self.data_path.stack_pointer + 1:]}"
        alu_repr = f"ALU_L: {self.data_path.alu_l}\tALU_R: {
            self.data_path.alu_r}\tALU_OUT: {self.data_path.alu_out}"
        return (
            f"Current State:"
            f"{'\nInterrupted' if self.controller.interruption_flag else ''}"
            f" {'with input: ' +
                chr(self.controller.input_buffer[0][1]) if self.controller.interruption_flag else ''}\n"  # noqa: E501
            f"{cu_repr}\n"
            f"{alu_repr}\n"
            f"{datapath_repr}\n"
            f"{stack_repr}\n"
            f"{'Instruction to execute:\n' +
                str(instr_repr) if not self.controller.interruption_flag else ''}"
        )
