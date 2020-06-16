#!/usr/bin/env python3

import sys

"""Main."""

import sys
from cpu import *

if len(sys.argv) < 2:
    print("Please enter the file path of a program to run.")

else:

    program_path = sys.argv[1]

    with open(program_path, "r") as program_data:

        # remove whitespaces and comments and store in a new list
        program = []

        for line in program_data:

            # remove comments first
            code_and_comments = line.split("#")
            code = code_and_comments[0]

            # remove any whitespace in the remaining string
            code = code.strip()

            # convert strings to ints and add line to program list
            if len(code) > 0:
                program.append(int(code, 2))

    cpu = CPU()

    cpu.load(program)
    cpu.run()