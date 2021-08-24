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


if __name__ == '__main__':
    unittest.main()
