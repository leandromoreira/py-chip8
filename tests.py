import unittest
import chip8

class TestChip8(unittest.TestCase):

    def test_memory_write(self):
        mem = chip8.Memory()
        mem.write(0xCAF, 0xBE)

        self.assertEqual(mem.read(0xCAF), 0xBE)

    def test_cpu_stack_start(self):
        cpu = chip8.CPU()

        self.assertEqual(cpu.SP, 0xEFF)

    def test_cpu_add_7xkk(self):
        machine = chip8.Machine()
        # zeroed
        self.assertEqual(machine.cpu.V[0x2], 0x0)

        # starts here
        machine.cpu.PC = 0x00 # memory address 0x00

        # filling memory
        machine.mem.write(0x00, 0x72) # 7(x) byte
        machine.mem.write(0x01, 0x10) # (kk) byte

        machine.execute()

        self.assertEqual(machine.cpu.V[0x2], 0x10)


if __name__ == '__main__':
    unittest.main()
