from src.isa import ArithmeticInstructionImm, Opcode, Registers

with open("examples/prob1.bin", "rb") as f:
    data = f.read()

    for i in range(0, len(data), 2):
        instr_data = data[i:i + 2]
        print("".join(f"{byte:08b}" for byte in instr_data))
