
import pytest

from src.datapath import DataPath
from src.isa import Opcode, Registers
from src.machine_signals import Signals


@pytest.fixture
def data_path() -> DataPath:
    return DataPath(256)


def test_signal_latch_r1(data_path: DataPath) -> None:
    data_path.data_out = 10
    data_path.signal_latch_r1(Signals.MEM_DATA_OUT)
    assert data_path.r1 == 10

    data_path.alu_out = 20
    data_path.signal_latch_r1(Signals.ALU_OUT)
    assert data_path.r1 == 20


def test_signal_latch_r2(data_path: DataPath) -> None:
    data_path.data_out = 15
    data_path.signal_latch_r2(Signals.MEM_DATA_OUT)
    assert data_path.r2 == 15

    data_path.alu_out = 25
    data_path.signal_latch_r2(Signals.ALU_OUT)
    assert data_path.r2 == 25


def test_signal_read(data_path: DataPath) -> None:
    data_path.data_memory[100] = 35
    data_path.signal_read(Signals.ADDR_IMM, 100)
    assert data_path.data_out == 35

    data_path.stack_pointer = 10
    data_path.data_memory[11] = 45
    data_path.signal_read(Signals.SP_INC)
    assert data_path.stack_pointer == 11
    assert data_path.data_out == 45

    data_path.stack_pointer = 11
    data_path.signal_read(Signals.SP_INC)
    assert data_path.stack_pointer == 12


def test_signal_latch_alu_l(data_path: DataPath) -> None:
    data_path.r1 = 50
    data_path.signal_latch_alu_l(Signals.DATA_R1)
    assert data_path.alu_l == 50

    data_path.r2 = 60
    data_path.signal_latch_alu_l(Signals.DATA_R2)
    assert data_path.alu_l == 60

    data_path.signal_latch_alu_l(Signals.LOAD_PC, 70)
    assert data_path.alu_l == 70


def test_signal_latch_alu_r(data_path: DataPath) -> None:
    data_path.r1 = 80
    data_path.signal_latch_alu_r(Signals.DATA_R1)
    assert data_path.alu_r == 80

    data_path.r2 = 90
    data_path.signal_latch_alu_r(Signals.DATA_R2)
    assert data_path.alu_r == 90

    data_path.signal_latch_alu_r(Signals.LOAD_ARG, 100)
    assert data_path.alu_r == 100


def test_execute_alu(data_path: DataPath) -> None:
    data_path.alu_l = 10
    data_path.alu_r = 5

    data_path.execute_alu(Opcode.ADD)
    assert data_path.alu_out == 15

    data_path.execute_alu(Opcode.SUB)
    assert data_path.alu_out ==  5

    data_path.execute_alu(Opcode.MUL)
    assert data_path.alu_out == 50

    data_path.execute_alu(Opcode.DIV)
    assert data_path.alu_out ==  2


def test_signal_write(data_path: DataPath) -> None:
    data_path.data_out = 5
    data_path.alu_out = 99

    data_path.signal_latch_r2(Signals.INPUT, 75)
    data_path.signal_latch_alu_l(Signals.DATA_R2)
    data_path.signal_latch_alu_r(Signals.LOAD_ARG, 0)        
    data_path.execute_alu(Opcode.ADD)

    data_path.signal_write(Signals.SP_DEC)
    assert data_path.data_memory[data_path.stack_pointer + 1] == 75


def test_zero_flag(data_path: DataPath) -> None:
    data_path.r1 = 0
    assert data_path.zero_flag(Registers.R1)

    data_path.r2 = 1
    assert not data_path.zero_flag(Registers.R2)
