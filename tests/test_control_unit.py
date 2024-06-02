from os import popen

import pytest

from src.control_unit import ControlUnit
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
from tests.test_datapath import data_path


@pytest.fixture
def control_unit() -> ControlUnit:
    data_path = DataPath(256)
    program = Program(entry=0, instructions=[])
    return ControlUnit(program, data_path)


def test_control_unit_program_counter(control_unit: ControlUnit) -> None:
    control_unit.program_counter = 0
    control_unit.signal_latch_program_counter(Signals.NEXT_IP)
    assert control_unit.program_counter == 1


def test_control_unit_signal_latch_program_counter_put_data(
    control_unit: ControlUnit
) -> None:
    control_unit.data_path.alu_out = 10

    control_unit.signal_latch_program_counter(Signals.PUT_DATA)
    assert control_unit.program_counter == 10


def test_control_unit_jump_instruction(control_unit: ControlUnit) -> None:
    instr = JumpInstruction(Opcode.JMP, 5)
    control_unit.signal_latch_program_counter(Signals.JMP_ARG, instr)
    assert control_unit.program_counter == 5


def test_control_unit_jump_eq_instruction(control_unit: ControlUnit) -> None:
    instr = JumpEqInstruction(Opcode.JE, Registers.R1, 5)
    control_unit.data_path.zero_flag(Registers.R1)
    control_unit.decode_and_execute_control_flow_instruction(instr)
    assert control_unit.program_counter == 5


def test_control_unit_management_instruction(control_unit: ControlUnit) -> None:
    instr = ManagementInstruction(Opcode.HLT)
    with pytest.raises(StopIteration):
        control_unit.decode_and_execute_control_flow_instruction(instr)


def test_control_unit_call_instruction(control_unit: ControlUnit) -> None:
    control_unit.program_counter = 10
    instr = CallInstruction(Opcode.CALL, 5)
    control_unit.decode_and_execute_control_flow_instruction(instr)
    assert control_unit.program_counter == 5
    assert control_unit.data_path.data_memory[255] == 10


def test_control_unit_ret_instruction(control_unit: ControlUnit) -> None:
    control_unit.program_counter = 10
    instr_1 = CallInstruction(Opcode.CALL, 5)
    control_unit.decode_and_execute_control_flow_instruction(instr_1)
    assert control_unit.program_counter == 5

    instr_2 = RetInstruction(Opcode.RET)
    control_unit.decode_and_execute_control_flow_instruction(instr_2)
    assert control_unit.program_counter == 10


def test_control_unit_arithmetic_instruction(control_unit: ControlUnit) -> None:
    instr_add = ArithmeticInstructionReg(Opcode.ADD, Registers.R1, Registers.R2)
    control_unit.data_path.r1 = 10
    control_unit.data_path.r2 = 20
    control_unit.decode_and_execute_instruction(instr_add)
    assert control_unit.data_path.alu_out == 30

    instr_sub = ArithmeticInstructionReg(Opcode.SUB, Registers.R1, Registers.R2)
    control_unit.decode_and_execute_instruction(instr_sub)
    assert control_unit.data_path.alu_out == 10

    instr_mul = ArithmeticInstructionReg(Opcode.MUL, Registers.R1, Registers.R2)
    control_unit.decode_and_execute_instruction(instr_mul)
    assert control_unit.data_path.alu_out == 200

    instr_div = ArithmeticInstructionReg(Opcode.DIV, Registers.R1, Registers.R2)
    control_unit.decode_and_execute_instruction(instr_div)
    assert control_unit.data_path.alu_out == 10


def test_control_unit_io_memory_instruction(control_unit: ControlUnit) -> None:
    instr_ld = IOMemoryInstruction(Opcode.LD, Registers.R1, 5)
    control_unit.data_path.data_memory[5] = 10
    control_unit.decode_and_execute_instruction(instr_ld)
    assert control_unit.data_path.r1 == 10

    instr_st = IOMemoryInstruction(Opcode.ST, Registers.R1, 5)
    control_unit.decode_and_execute_instruction(instr_st)
    assert control_unit.data_path.data_memory[5] == 10


def test_control_unit_io_rst_instruction(control_unit: ControlUnit) -> None:
    control_unit.data_path.r1 = 10
    control_unit.data_path.r2 = 20
    control_unit.program_counter = 50
    control_unit.data_path.signal_latch_alu_l(Signals.DATA_R1)
    control_unit.data_path.signal_latch_alu_r(Signals.LOAD_ARG, 0)
    control_unit.data_path.execute_alu(Opcode.ADD)
    control_unit.data_path.signal_write(Signals.SP_DEC)

    control_unit.data_path.signal_latch_alu_l(Signals.DATA_R2)
    control_unit.data_path.signal_latch_alu_r(Signals.LOAD_ARG, 0)
    control_unit.data_path.execute_alu(Opcode.ADD)
    control_unit.data_path.signal_write(Signals.SP_DEC)
    
    control_unit.data_path.signal_latch_alu_l(
        Signals.LOAD_PC, control_unit.program_counter
    )
    control_unit.data_path.signal_latch_alu_r(Signals.LOAD_ARG, 0)
    control_unit.data_path.execute_alu(Opcode.ADD)  
    control_unit.data_path.signal_write(Signals.SP_DEC)

    control_unit.data_path.r1 = 1
    control_unit.data_path.r2 = 2

    instr_call = CallInstruction(Opcode.CALL, 5)
    control_unit.decode_and_execute_control_flow_instruction(instr_call)
    
    instr_rst = IORstInstruction(Opcode.RST)
    control_unit.decode_and_execute_instruction(instr_rst)

    assert control_unit.data_path.r1 == 10
    assert control_unit.data_path.r2 == 20
    assert control_unit.program_counter == 50

