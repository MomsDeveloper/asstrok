import pytest

from src.control_unit import ControlUnit
from src.datapath import DataPath
from src.isa import (
    CallInstruction,
    JumpEqInstruction,
    JumpInstruction,
    ManagementInstruction,
    Opcode,
    Program,
    Registers,
    RetInstruction,
)
from src.machine_signals import Signals


@pytest.fixture
def control_unit() -> ControlUnit:
    data_path = DataPath(256)
    program = Program(entry=0, instructions=[])
    return ControlUnit(program, data_path)


def test_control_unit_program_counter(control_unit: ControlUnit) -> None:
    control_unit.program_counter = 0
    control_unit.signal_latch_program_counter(Signals.NEXT_IP)
    assert control_unit.program_counter == 1


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
    instr = CallInstruction(Opcode.CALL, 5)
    control_unit.decode_and_execute_control_flow_instruction(instr)
    assert control_unit.program_counter == 5


def test_control_unit_ret_instruction(control_unit: ControlUnit) -> None:
    control_unit.data_path.r1 = 1
    control_unit.data_path.r2 = 2
    control_unit.program_counter = 10
    instr_1 = CallInstruction(Opcode.CALL, 5)
    control_unit.decode_and_execute_control_flow_instruction(instr_1)
    assert control_unit.program_counter == 5

    instr_2 = RetInstruction(Opcode.RET)
    control_unit.decode_and_execute_control_flow_instruction(instr_2)
    assert control_unit.data_path.r1 == 1
    assert control_unit.data_path.r2 == 2
    assert control_unit.program_counter == 10


def test_control_unit_signal_latch_program_counter_put_data(
    control_unit: ControlUnit
) -> None:
    control_unit.data_path.alu_out = 10

    control_unit.signal_latch_program_counter(Signals.PUT_DATA)
    assert control_unit.program_counter == 10
