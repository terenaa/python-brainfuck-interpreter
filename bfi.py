#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Brainfuck interpreter

(c) 2018 Krzysztof Janda
"""

import getopt
import sys


class BrainfuckException(Exception):
    pass


class Brainfuck:
    _INSTRUCTIONS = {
        ">": "_move_forward",
        "<": "_move_backward",
        "+": "_increase",
        "-": "_decrease",
        ".": "_print",
        ",": "_read",
        "[": "_loop_start",
        "]": "_loop_end"
    }

    _pointer = 0        # Instruction pointer
    _position = (0, 0)  # Instruction position
    _size = 1           # Memory size
    _script = []        # BF script
    _mem = [0]          # Script memory
    _loops_map = {}     # Loops start/end map
    _mem_dump = False   # Show memory dump at the end of execution

    def __init__(self, cell_size=8, memory_dump=False):
        self._mem_dump = memory_dump

        if cell_size < 1:
            raise BrainfuckException("[Interpreter exception] Cell size cannot be less than 1")

        self._MAX_CELL_VALUE = pow(2, int(cell_size)) - 1

    def _reset(self):
        """Reset all class variables to initial state
        """
        self._pointer = 0
        self._position = (0, 0)
        self._size = 1
        self._script = []
        self._mem = [0]
        self._loops_map = {}

    def run(self, file_name):
        """Run BF script from file of given name.

        Args:
            file_name (str): Name of the file to run
        """
        self.eval(Brainfuck._readfile(file_name))

    def eval(self, code):
        """Evaluate BF inline code

        Args:
            code (str): Brainfuck script
        """
        self._reset()
        self._script = [(i, ln) for i, ln in enumerate(code.splitlines()) if ln.strip()]

        self._build_loops_map()

        while self._position[0] < len(self._script):
            position_changed = False
            line = self._script[self._position[0]]

            while self._position[1] < len(line[1]):
                instruction = line[1][self._position[1]]

                if instruction in self._INSTRUCTIONS:
                    position_changed = getattr(self, "%s" % self._INSTRUCTIONS[instruction])()

                    if position_changed:
                        break

                self._position = (self._position[0], self._position[1] + 1)

            if position_changed is False:
                self._position = (self._position[0] + 1, 0)

        print("")

        if self._mem_dump:
            print("Memory: %s" % str(self._mem))

    @staticmethod
    def _readfile(file_name):
        try:
            with open(file_name, "r") as f:
                data = f.read()

            return data
        except IOError as error:
            sys.exit(str(error))

    def _build_loops_map(self):
        """Build map of opening and closing brackets in the script
        """
        line_index, stack = 0, []

        while line_index < len(self._script):
            for position, instruction in enumerate(self._script[line_index][1]):
                line_no = self._script[line_index][0]
                instruction_position = (line_index, position)

                if "[" == instruction:
                    stack.append((line_no, instruction_position))
                elif "]" == instruction:
                    if 0 == len(stack):
                        raise BrainfuckException(
                            "[Syntax error] Unexpected closing bracket in line %s at position %s" % (
                                line_no + 1, position + 1))

                    start = stack.pop()
                    self._loops_map[start[1]] = instruction_position
                    self._loops_map[instruction_position] = start[1]

            line_index += 1

        if len(stack) > 0:
            bracket_position = stack.pop()

            raise BrainfuckException("[Syntax error] Unclosed bracket in line %s at position %s" % (
                bracket_position[0] + 1, bracket_position[1][1] + 1))

    def _move_forward(self):
        if self._pointer + 1 >= self._size:
            self._expand_buffer()

        self._pointer += 1

    def _move_backward(self):
        if self._pointer - 1 >= 0:
            self._pointer -= 1

    def _increase(self):
        new_value = self._mem[self._pointer] + 1

        self._mem[self._pointer] = new_value if new_value <= self._MAX_CELL_VALUE else 0

    def _decrease(self):
        new_value = self._mem[self._pointer] - 1

        self._mem[self._pointer] = new_value if new_value >= 0 else self._MAX_CELL_VALUE

    def _print(self):
        sys.stdout.write(chr(self._mem[self._pointer]))

    def _read(self):
        sys.stdout.write("Enter a character: ")
        char = sys.stdin.read(1)

        self._mem[self._pointer] = ord(char) % self._MAX_CELL_VALUE

    def _loop_start(self):
        if 0 != self._mem[self._pointer]:
            return False

        # Go to the end of loop
        self._position = self._loops_map[self._position]

        return True

    def _loop_end(self):
        if 0 == self._mem[self._pointer]:
            return False

        # Go back to loop start
        self._position = self._loops_map[self._position]

        return True

    def _expand_buffer(self):
        self._mem.append(0)
        self._size += 1


if "__main__" == __name__:
    def usage():
        print("""Usage: ./bfi.py [OPTIONS] <file_name>
    --help\t\tThis help
    --cell-size=NUM\tSet single cell size in bits (default = 8)
    --memory-dump\tShow memory dump at the end of script execution
        """)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["cell-size=", "memory-dump", "help"])
    except getopt.GetoptError as e:
        print(str(e))
        sys.exit(2)

    c_size, mem_dump, help = 8, False, False

    for o, a in opts:
        if "--help" == o:
            help = True
        elif "--cell-size" == o:
            c_size = a
        elif "--memory-dump" == o:
            mem_dump = True

    if help or len(sys.argv) - len(opts) < 2:
        usage()
        sys.exit()

    try:
        Brainfuck(cell_size=c_size, memory_dump=mem_dump).run(sys.argv[-1])
    except BrainfuckException as e:
        print(str(e))
