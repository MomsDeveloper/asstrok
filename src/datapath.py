from typing import List, Literal

from src.isa import Opcode, Registers
from src.machine_signals import Signals


class DataPath:
    data_memory_size: int
    data_memory: List[int]
    data_out: int
    r1: int
    r2: int
    alu_out: int
    alu_l: int
    alu_r: int
    stack_pointer: int
    address_register: int

    def __init__(self, data_memory_size: int) -> None:
        self.data_memory_size = data_memory_size
        self.data_memory = [0] * data_memory_size
        self.r1 = 0
        self.r2 = 0
        self.alu_out = 0
        self.stack_pointer = data_memory_size - 1
        self.data_out = 0
        self.alu_l = 0
        self.alu_r = 0
    
    def signal_latch_r1(self, sel: Signals) -> None:
        if sel == Signals.MEM_DATA_OUT:
            self.r1 = self.data_out
        elif sel == Signals.ALU_OUT:
            self.r1 = self.alu_out
        else:
            raise ValueError(f"Unknown signal {sel}")
        
    def signal_latch_r2(self, sel: Signals, value: int = 0) -> None:
        if sel == Signals.MEM_DATA_OUT:
            self.r2 = self.data_out
        elif sel == Signals.ALU_OUT:
            self.r2 = self.alu_out
        elif sel == Signals.INPUT:
            self.r2 = value
        else:
            raise ValueError(f"Unknown signal {sel}")

    def signal_read(
        self, 
        sel: Literal[
            Signals.SP_INC, 
            Signals.ADDR_IMM, 
            Signals.ADDR_R1, 
            Signals.ADDR_R2
        ],
        addr: int = 0,
    ) -> None:
        if sel == Signals.SP_INC:
            if self.stack_pointer == self.data_memory_size:
                raise ValueError("Stack underflow")
            self.stack_pointer += 1
            self.data_out = self.data_memory[self.stack_pointer]
        elif sel == Signals.ADDR_IMM:
            self.data_out = self.data_memory[addr]
        elif sel == Signals.ADDR_R1:
            self.data_out = self.data_memory[self.r1]
        elif sel == Signals.ADDR_R2:
            self.data_out = self.data_memory[self.r2]
    
    def signal_latch_alu_l(self, sel: Signals, value: int = 0) -> None:
        if sel == Signals.DATA_R1:
            self.alu_l = self.r1
        elif sel == Signals.DATA_R2:
            self.alu_l = self.r2
        elif sel == Signals.LOAD_PC:
            self.alu_l = value
        else:
            raise ValueError(f"Unknown signal {sel}")
    
    def signal_latch_alu_r(self, sel: Signals, value: int = 0) -> None:
        if sel == Signals.DATA_R1:
            self.alu_r = self.r1
        elif sel == Signals.DATA_R2:
            self.alu_r = self.r2
        elif sel == Signals.LOAD_ARG:
            self.alu_r = value
        else:
            raise ValueError(f"Unknown signal {sel}")
    
    def execute_alu(self, opcode: Opcode) -> None:
        if opcode == Opcode.ADD:
            self.alu_out = self.alu_l + self.alu_r
        elif opcode == Opcode.SUB:
            self.alu_out = self.alu_l - self.alu_r
        elif opcode == Opcode.MUL:
            self.alu_out = self.alu_l * self.alu_r
        elif opcode == Opcode.DIV:
            self.alu_out = self.alu_l // self.alu_r
        else:
            raise ValueError(f"Unknown opcode {opcode}")
    
    def signal_write(
        self, 
        sel: Literal[
            Signals.SP_DEC, 
            Signals.ADDR_IMM, 
            Signals.ADDR_R1, 
            Signals.ADDR_R2
        ],
        addr: int = 0,
    ) -> None:
        if sel == Signals.SP_DEC:
            if self.stack_pointer == 0:
                raise ValueError("Stack overflow")
            self.data_memory[self.stack_pointer] = self.alu_out
            self.stack_pointer -= 1
        elif sel == Signals.ADDR_IMM:
            self.data_memory[addr] = self.alu_out
        elif sel == Signals.ADDR_R1:
            self.data_memory[self.r1] = self.alu_out
        elif sel == Signals.ADDR_R2:
            self.data_memory[self.r2] = self.alu_out
        else:
            raise ValueError(f"Unknown signal {sel}")

    def zero_flag(self, reg: Registers) -> bool:
        if reg == Registers.R1:
            return self.r1 == 0
        elif reg == Registers.R2:
            return self.r2 == 0
        else:
            raise ValueError(f"Unknown register {reg}")


            


