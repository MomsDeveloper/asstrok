import logging
import sys
from pathlib import Path

from src.control_unit import ControlUnit
from src.datapath import DataPath
from src.io_controller import IOController
from src.isa import Program, unpack_program


class Machine:
    cu: ControlUnit
    datapath: DataPath
    io_controller: IOController
    program: Program

    def __init__(self) -> None:
        self.data_memory_size = 256
        self.datapath = DataPath(self.data_memory_size)
        self.io_controller = IOController()
        self.program = Program(entry=0, instructions=[])
        self.cu = ControlUnit(self.program, self.datapath, self.io_controller)
    
    def load_program(self, program: Program) -> None:
        self.program = program
        self.cu.program = program

    def simulate(self, 
        input_buffer: list[tuple[int, int]], 
        program: Program, data_memory_size: int = 100, 
        limit: int = 100000
    ) -> None:
        self.load_program(program)
        self.io_controller.input_buffer = input_buffer
        self.datapath.data_memory_size = data_memory_size
        self.cu.program_counter = program.entry

        logging.info("Starting simulation")
        logging.info(self.cu)
        logging.info("")

        count = 0
        controller_in_buffer = self.io_controller.input_buffer

        while count < limit:
            count += 1
            if (len(controller_in_buffer) > 0 and 
                self.cu._tick >= controller_in_buffer[0][0]):
                self.io_controller.interruption_flag = True
            
            instr = program.instructions[self.cu.program_counter]
            self.cu.decode_and_execute_instruction(instr)

            logging.info(self.cu)
            logging.info("")
            
            self.cu.check_int_request()
        
        raise StopIteration()


def main(code_file: Path, input_file: Path) -> None:
    # read code_file and decode each instruction using unpack
    with code_file.open("rb") as f:
        source = f.read()

    program = unpack_program(source)

    with open(input_file) as file:
        data = eval(file.read())

    converted_data = [(int(x[0]), ord(x[1])) for x in data]
    
    machine = Machine()
    try:
        machine.simulate(converted_data, program)
    except StopIteration:
        logging.info("Simulation finished")
        logging.info("Output buffer:")
        print([
            chr(c)
            for c in machine.io_controller.output_buffer
        ])

        

if __name__ == "__main__":
    assert len(sys.argv) == 3, "Usage: python machine.py <compiled.bin> <input.txt>"
    logging.basicConfig(level=logging.INFO)
    compiled_path = Path(sys.argv[1])
    input_path = Path(sys.argv[2])
    main(compiled_path, input_path)
