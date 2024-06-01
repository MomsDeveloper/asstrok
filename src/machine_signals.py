from enum import Enum, auto


class Signals(Enum):
    # program counter
    PUT_DATA = auto()
    JMP_ARG = auto()
    NEXT_IP = auto()

    MEM_DATA_OUT = auto()
    ALU_OUT = auto()
    MEM_DATA_IN = auto()

    SP_INC = auto()
    SP_DEC = auto()
    INPUT_ADDR = auto()

    DATA_R1 = auto()
    DATA_R2 = auto()
    LOAD_PC = auto()
    LOAD_ARG = auto()

    INPUT = auto()
