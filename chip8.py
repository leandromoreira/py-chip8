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
        self.PC = Memory.program_address
        self.SP = 0xEFF

class RomFile(object):
    def load(self, file_path):
        raw_array = []
        with open(file_path, "rb") as f:
            chars = f.read()

            for char in chars:
                raw_array.append(char)
        return raw_array

class Machine(object):
    def __init__(self, screen):
        self.mem = Memory()
        self.cpu = CPU()
        self.screen = screen

        rom = RomFile().load("ibm.ch8")

        for address, value in enumerate(rom):
            self.mem.write(Memory.program_address + address, value)

    def print_state(self):
        print("############ Cpu State ###########")
        print("\n")
        print("PC = " + hex(self.cpu.PC) + " I = " + hex(self.cpu.I))
        for i in range(16):
            separator = "  "
            if i % 3 == 0:
                separator = "\n"
            print("V[" + hex(i) + "] = " + hex(self.cpu.V[i]), end=separator)
        print("")


        print("########## Memory viewer #############")
        first = True
        first_address = max(0, self.cpu.PC - 16)

        for address in range(first_address, self.cpu.PC + 16 + 1):
            if first:
                print(hex(self.__create_16bit_two_complement(address)), end=": ")
                first = False
            print(hex(self.mem.read(address)), end="  ")

        print("")

    def __create_16bit_two_complement(self, value):
        # the machine works with 2's complement representation
        if( (value&(1<<(16-1))) != 0 ):
            value = value - (1<<16)
        return value

    def execute(self):
        # fetch
        opcode = self.mem.read(self.cpu.PC) # 1st Byte
        operand = self.mem.read(self.cpu.PC + 1) # 2nd Byte


        # decode
        if opcode == 0x0 and operand == 0xE0:
            self.cpu.PC += 2
        elif opcode >> 0x4 == 0x1:
            self.cpu.PC = ((opcode & 0xF) << 8) | operand
        elif opcode >> 0x4 == 0x6:
            x = opcode & 0b1111
            self.cpu.V[x] = operand
            self.cpu.PC += 2
        elif opcode >> 0x4 == 0x7:
            x = opcode & 0b1111
            self.cpu.V[x] = (operand + self.cpu.V[x]) & 0xFF
            self.cpu.PC += 2
        elif opcode >> 0x4 == 0xA:
            self.cpu.I = ((opcode & 0xF) << 8) | operand
            self.cpu.PC += 2
        elif opcode >> 0x4 == 0xD:
            self.draw_sprite(opcode, operand)
            self.cpu.PC += 2

    def draw_sprite(self, opcode, operand):
        """
        Dxyn - DRAW x, y, num_bytes
        Draws the sprite pointed to in the index register at the specified
        x and y coordinates. Drawing is done via an XOR routine, meaning that
        if the target pixel is already turned on, and a pixel is set to be
        turned on at that same location via the draw, then the pixel is turned
        off. The routine will wrap the pixels if they are drawn off the edge
        of the screen. Each sprite is 8 bits (1 byte) wide. The num_bytes
        parameter sets how tall the sprite is. Consecutive bytes in the memory
        pointed to by the index register make up the bytes of the sprite. Each
        bit in the sprite byte determines whether a pixel is turned on (1) or
        turned off (0). For example, assume that the index register pointed
        to the following 7 bytes:
                       bit 0 1 2 3 4 5 6 7
           byte 0          0 1 1 1 1 1 0 0
           byte 1          0 1 0 0 0 0 0 0
           byte 2          0 1 0 0 0 0 0 0
           byte 3          0 1 1 1 1 1 0 0
           byte 4          0 1 0 0 0 0 0 0
           byte 5          0 1 0 0 0 0 0 0
           byte 6          0 1 1 1 1 1 0 0
        This would draw a character on the screen that looks like an 'E'. The
        x_source and y_source tell which registers contain the x and y
        coordinates for the sprite. If writing a pixel to a location causes
        that pixel to be turned off, then VF will be set to 1.
           Bits:  15-12     11-8      7-4       3-0
                  unused    x_source  y_source  num_bytes
        """
        x_source = opcode & 0xF
        y_source = operand >> 4
        num_bytes = operand & 0xF

        self.cpu.V[0xF] = 0
        x_pos = self.cpu.V[x_source]
        y_pos = self.cpu.V[y_source]

        self.draw_normal(x_pos, y_pos, num_bytes, self.cpu.I)

    def draw_normal(self, x_pos, y_pos, num_bytes, I_register):
        """
        Draws a sprite on the screen while in NORMAL mode.
        :param x_pos: the X position of the sprite
        :param y_pos: the Y position of the sprite
        :param num_bytes: the number of bytes to draw
        """
        for y_index in range(num_bytes):

            current_byte = self.mem.read(I_register + y_index)

            y_coord = y_pos + y_index
            y_coord = y_coord % self.screen.get_height()

            for x_index in range(8):

                x_coord = x_pos + x_index
                x_coord = x_coord % self.screen.get_width()

                color = current_byte >> (7 - x_index) & 0b1
                current_color = self.screen.get_pixel(x_coord, y_coord)

                if color == 1 and current_color == 1:
                    self.cpu.V[0xF] |= 1
                    color = 0

                elif color == 0 and current_color == 1:
                    color = 1

                self.screen.draw_pixel(x_coord, y_coord, color)

        self.screen.update()


import pygame
import screen

def main_loop():
    graphic = screen.Chip8Screen(10)
    graphic.init_display()
    machine = Machine(graphic) #.execute()

    pygame.init()
    running = True

    while running:
        machine.execute()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

main_loop()
