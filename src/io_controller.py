class IOController:
    input_buffer: list[tuple[int, int]]
    output_buffer: list[int]

    interruption_flag: bool

    def __init__(self) -> None:
        self.input_buffer = []
        self.output_buffer = []
        self.interruption_flag = False

    def set_interruption_flag(self) -> None:
        self.interruption_flag = True
    
    def push_to_output_buffer(self, data: int) -> None:
        self.output_buffer.append(data)
    
