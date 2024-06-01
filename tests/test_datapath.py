import unittest

from src.datapath import DataPath
from src.isa import Opcode, Registers
from src.machine_signals import Signals


class TestDataPath(unittest.TestCase):
    def setUp(self) -> None:
        self.data_memory_size = 256
        self.data_path = DataPath(self.data_memory_size)

    def test_signal_latch_r1(self) -> None:
        self.data_path.data_out = 10
        self.data_path.signal_latch_r1(Signals.MEM_DATA_OUT)
        self.assertEqual(self.data_path.r1, 10)

        self.data_path.alu_out = 20
        self.data_path.signal_latch_r1(Signals.ALU_OUT)
        self.assertEqual(self.data_path.r1, 20)

    def test_signal_latch_r2(self) -> None:
        self.data_path.data_out = 15
        self.data_path.signal_latch_r2(Signals.MEM_DATA_OUT)
        self.assertEqual(self.data_path.r2, 15)

        self.data_path.alu_out = 25
        self.data_path.signal_latch_r2(Signals.ALU_OUT)
        self.assertEqual(self.data_path.r2, 25)

    def test_signal_read(self) -> None:
        self.data_path.data_memory[100] = 35
        self.data_path.signal_read(Signals.INPUT_ADDR, 100)
        self.assertEqual(self.data_path.data_out, 35)

        self.data_path.stack_pointer = 10
        self.data_path.data_memory[11] = 45
        self.data_path.signal_read(Signals.SP_INC)
        self.assertEqual(self.data_path.stack_pointer, 11)
        self.assertEqual(self.data_path.data_out, 45)

        self.data_path.stack_pointer = 11
        self.data_path.signal_read(Signals.SP_DEC)
        self.assertEqual(self.data_path.stack_pointer, 10)

    def test_signal_latch_alu_l(self) -> None:
        self.data_path.r1 = 50
        self.data_path.signal_latch_alu_l(Signals.DATA_R1)
        self.assertEqual(self.data_path.alu_l, 50)

        self.data_path.r2 = 60
        self.data_path.signal_latch_alu_l(Signals.DATA_R2)
        self.assertEqual(self.data_path.alu_l, 60)

        self.data_path.signal_latch_alu_l(Signals.LOAD_PC, 70)
        self.assertEqual(self.data_path.alu_r, 70)

    def test_signal_latch_alu_r(self) -> None:
        self.data_path.r1 = 80
        self.data_path.signal_latch_alu_r(Signals.DATA_R1)
        self.assertEqual(self.data_path.alu_r, 80)

        self.data_path.r2 = 90
        self.data_path.signal_latch_alu_r(Signals.DATA_R2)
        self.assertEqual(self.data_path.alu_r, 90)

        self.data_path.signal_latch_alu_r(Signals.LOAD_ARG, 100)
        self.assertEqual(self.data_path.alu_r, 100)

    def test_execute_alu(self) -> None:
        self.data_path.alu_l = 10
        self.data_path.alu_r = 5

        self.data_path.execute_alu(Opcode.ADD)
        self.assertEqual(self.data_path.alu_out, 15)

        self.data_path.execute_alu(Opcode.SUB)
        self.assertEqual(self.data_path.alu_out, 5)

        self.data_path.execute_alu(Opcode.MUL)
        self.assertEqual(self.data_path.alu_out, 50)

        self.data_path.execute_alu(Opcode.DIV)
        self.assertEqual(self.data_path.alu_out, 2)

    def test_signal_write(self) -> None:
        self.data_path.data_out = 5
        self.data_path.alu_out = 99

        self.data_path.signal_latch_r2(Signals.INPUT, 75)
        self.data_path.signal_latch_alu_l(Signals.DATA_R2)
        self.data_path.signal_latch_alu_r(Signals.LOAD_ARG, 0)        
        self.data_path.execute_alu(Opcode.ADD)

        self.data_path.signal_write()
        self.assertEqual(self.data_path.data_memory[self.data_path.stack_pointer], 75)

    def test_zero_flag(self) -> None:
        self.data_path.r1 = 0
        self.assertTrue(self.data_path.zero_flag(Registers.R1))

        self.data_path.r2 = 1
        self.assertFalse(self.data_path.zero_flag(Registers.R2))


if __name__ == '__main__':
    unittest.main()
