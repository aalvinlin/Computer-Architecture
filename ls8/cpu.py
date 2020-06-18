"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        
        # RAM
        self.ram = [0] * 256

        # general-purpose registers
        self.registers = [0] * 8
        self.registers[7] = 0xF4    # stack pointer
        self.sp = self.registers[7] # alias for stack pointer

        # internal registers
        self.pc = 0   # program counter
        self.ir = None   # instruction register
        self.mar = None  # memory address register
        self.mdr = None  # memory data register
        self.fl = 0   # flags

        # keep track of whether program is running
        # HALT will set this variable to false
        self.is_running = True

        # define instructions
        
        def call(register):

            # store the line to return to onto the stack
            # can't use push() because it stores the contents of the line instead
            self.sp -= 1
            self.ram[self.sp] = self.pc + 2
            
            # get the address to call
            register_containing_address = self.ram[self.pc + 1]

            # set program counter to address of the subroutine
            self.pc = self.ram[register_containing_address]

        def hlt():
            self.is_running = False

        def ld(register1, register2):
            self.ram[register1] = self.ram[register2]

        def ldi(register, value):
            self.ram[register] = value

        def is_equal():
            return self.fl & 0b00000001
        
        def is_less_than():
            return self.fl & 0b00000100
        
        def is_greater_than():
            return self.fl & 0b00000010
        
        def jeq(register):

            print("in JEQ:", is_equal())

            if is_equal():
                self.pc = self.ram[register]
            else:
                self.pc += 2

        def jge(register):
            if is_greater_than() or is_equal():
                self.pc = self.ram[register]
            else:
                self.pc += 2

        def jgt(register):
            if is_greater_than():
                self.pc = self.ram[register]
            else:
                self.pc += 2

        def jle(register):
            if is_less_than() or is_equal():
                self.pc = self.ram[register]
            else:
                self.pc += 2

        def jlt(register):
            if is_less_than():
                self.pc = self.ram[register]
            else:
                self.pc += 2

        def jmp(register):
            self.pc = self.ram[register]

        def pop(register):
            self.ram[register] = self.ram[self.sp]
            self.sp += 1
            
        def pra(register):
            print(chr(self.ram[register]))

        def prn(register):
            print(self.ram[register])

        def push(register):
            self.sp -= 1
            self.ram[self.sp] = self.ram[register]
        
        def ret():
            # set program counter to the last-pushed value on the stack, which is the line to return to
            self.pc = self.ram[self.sp]

            # increment stack pointer by one
            self.sp += 1

        # hold a mapping of instructions to functions
        self.instructions = dict()
        self.instructions[0b10100000] = lambda operand_a, operand_b: self.alu("ADD", operand_a, operand_b)
        self.instructions["AND"] = None
        self.instructions[0b01010000] = call
        self.instructions[0b10100111] = lambda operand_a, operand_b: self.alu("CMP", operand_a, operand_b)
        self.instructions[0b01100110] = lambda operand_a: self.alu("DEC", operand_a)
        self.instructions[0b10100011] = lambda operand_a, operand_b: self.alu("DIV", operand_a, operand_b)
        self.instructions[0b00000001] = hlt
        self.instructions[0b01100101] = lambda operand_a: self.alu("INC", operand_a)
        self.instructions["INT"] = None
        self.instructions["IRET"] = None
        self.instructions[0b01010101] = jeq
        self.instructions[0b01011010] = jge
        self.instructions[0b01010111] = jgt
        self.instructions[0b01011001] = jle
        self.instructions[0b01011000] = jlt
        self.instructions[0b01010100] = jmp
        self.instructions["JNE"] = None
        self.instructions[0b10000011] = ld
        self.instructions[0b10000010] = ldi
        self.instructions["MOD"] = lambda operand_a, operand_b: self.alu("MOD", operand_a, operand_b)
        self.instructions[0b10100010] = lambda operand_a, operand_b: self.alu("MUL", operand_a, operand_b)
        self.instructions["NOP"] = None
        self.instructions["NOT"] = None
        self.instructions["OR"] = None
        self.instructions[0b01000110] = pop
        self.instructions[0b01001000] = pra
        self.instructions[0b01000111] = prn
        self.instructions[0b01000101] = push
        self.instructions[0b00010001] = ret
        self.instructions["SHL"] = None
        self.instructions["SHR"] = None
        self.instructions["ST"] = None
        self.instructions[0b10100001] = lambda operand_a, operand_b: self.alu("SUB", operand_a, operand_b)
        self.instructions["XOR"] = None

    # retrieve the value stored in the specifed register, and store it in the MDR register
    def ram_read(self, address):

        self.mdr = self.ram[address]

        return self.mdr

    # write the specified value into the specifed register
    def ram_write(self, value, address):
        self.ram[address] = value

    def load(self, program):
        """Load a program into memory."""

        address = 0

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b=None):
        """ALU operations."""

        if op == "ADD":
            self.ram[reg_a] += self.ram[reg_b]
        elif op == "SUB":
            self.ram[reg_a] -= self.ram[reg_b]
        elif op == "MUL":
            self.ram[reg_a] *= self.ram[reg_b]
        elif op == "DIV":
            if reg_b == 0:
                print("Cannot divide by zero.")
                self.instructions[0b00000001]() # halt
            else:
                self.ram[reg_a] = self.ram[reg_a] // self.ram[reg_b]
        elif op == "MOD":
            if reg_b == 0:
                print("Cannot mod by zero.")
                self.instructions[0b00000001]() # halt
            else:
                self.ram[reg_a] %= self.ram[reg_b]
        
        elif op == "DEC":
            self.ram[reg_a] -= 1
        elif op == "INC":
            self.ram[reg_a] += 1

        elif op == "CMP":

            # reset the flags register
            self.fl = 0

            # set the equal flag
            if self.ram[reg_a] == self.ram[reg_b]:
                self.fl = self.fl | 0b00000001
            
            # set the less than flag
            if self.ram[reg_a] < self.ram[reg_b]:
                self.fl = self.fl | 0b00000100

            # set the greater than flag
            if self.ram[reg_a] > self.ram[reg_b]:
                self.fl = self.fl | 0b00000010

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.registers[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while self.is_running:

            print("self.pc:", self.pc)

            # store memory address in instruction register
            self.ir = self.ram_read(self.pc)

            # retrieve the next two bytes of data in case they are used as operands
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # determine the number of operands used by the instruction
            first_two_bits = self.ir >> 6
            number_of_operands = first_two_bits

            # execute the instruction
            if self.ir in self.instructions and self.instructions[self.ir] is not None:

                # execute the instructions with any required operands
                if number_of_operands == 0:
                    self.instructions[self.ir]()
                
                elif number_of_operands == 1:
                    self.instructions[self.ir](operand_a)
                
                else:
                    self.instructions[self.ir](operand_a, operand_b)

            else:
                print("Invalid instruction", self.ir)
                pass

            # determine whether the instruction sets the program counter (specified in 5th bit)
            fifth_bit_masked = self.ir & 0b00010000
            modifies_program_counter = fifth_bit_masked >> 4

            # if the instruction doesn't modify the program counter directly (CALL, RET, JMP, etc.), then increment the program counter automatically
            if not modifies_program_counter:
                
                # update program counter to point to the next instruction
                self.pc += number_of_operands + 1
