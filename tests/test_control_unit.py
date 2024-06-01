import unittest
from unittest.mock import MagicMock

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


class TestControlUnit(unittest.TestCase):
    def setUp(self) -> None:
        # Create a mock DataPath
        self.data_path = MagicMock(spec=DataPath)
        
        # Create a simple Program
        self.program = Program(entry=0, instructions=[])
        
        self.control_unit = ControlUnit(self.program, self.data_path)

    def test_control_unit_program_counter(self) -> None:
        self.control_unit.program_counter = 0
        self.control_unit.signal_latch_program_counter(Signals.NEXT_IP)
        self.assertEqual(self.control_unit.program_counter, 1)

    def test_control_unit_jump_instruction(self) -> None:
        instr = JumpInstruction(Opcode.JMP, 5)
        self.control_unit.signal_latch_program_counter(Signals.JMP_ARG, instr)
        self.assertEqual(self.control_unit.program_counter, 5)
    
    def test_control_unit_jump_eq_instruction(self) -> None:
        instr = JumpEqInstruction(Opcode.JE, Registers.R1, 5)
        self.data_path.zero_flag.return_value = True
        self.control_unit.decode_and_execute_control_flow_instruction(instr)
        self.assertEqual(self.control_unit.program_counter, 5)
    
    def test_control_unit_management_instruction(self) -> None:
        instr = ManagementInstruction(Opcode.HLT)
        with self.assertRaises(StopIteration):
            self.control_unit.decode_and_execute_control_flow_instruction(instr)
   
    def test_control_unit_call_instruction(self) -> None:
        instr = CallInstruction(Opcode.CALL, 5)
        self.control_unit.decode_and_execute_control_flow_instruction(instr)
        self.assertEqual(self.control_unit.program_counter, 5)

    def test_control_unit_ret_instruction(self) -> None:
        instr = RetInstruction(Opcode.RET)
        # Mock the alu_out attribute
        self.data_path.alu_out = 20

        self.control_unit.decode_and_execute_control_flow_instruction(instr)
        self.assertEqual(self.control_unit.program_counter, 20)
    
    def test_control_unit_tick(self) -> None:
        self.assertEqual(self.control_unit._tick, 0)
        self.control_unit.tick()
        self.assertEqual(self.control_unit._tick, 1)
    
    def test_control_unit_signal_latch_program_counter_put_data(self) -> None:
        # Mock the alu_out attribute
        self.data_path.alu_out = 10

        self.control_unit.signal_latch_program_counter(Signals.PUT_DATA)
        self.assertEqual(self.control_unit.program_counter, 10)
                

if __name__ == '__main__':
    unittest.main()
        

