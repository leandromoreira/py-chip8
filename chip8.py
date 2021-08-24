# ..................................
# Memory Map
# ..................................
# Total space  : 0x000 -- 0xFFF
# Start Address: 0x200
# Display Refre: 0xF00-0xFFF
# Call stack   : 0xEA0-0xEFF
# ..................................
class Memory(object):
    memory_size = 0x1000
    program_address = 0x200

    def __init__(self):
        self.memory = [0] *  Memory.memory_size

    def write(self, address, value):
        self.memory[address] = value

    def read(self, address):
        return self.memory[address]

class CPU(object):
    def __init__(self):
        # The VF register should not be used by any program, as it is used as
        # a flag by some instructions.
        self.V = [0] * 0x10 # 16 registers (8 bit)
        self.I = 0x0000 # so only the lowest (rightmost) 12 bits are usually used
        self.DELAY = 0x0000
        self.SOUND = 0x0000
        self.PC = 0x0000
        self.SP = 0xEFF

