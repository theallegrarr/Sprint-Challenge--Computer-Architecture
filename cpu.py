"""CPU functionality."""

import sys

SP = 7
class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.program_counter = 0

        # instruction register records running instructions
        # ram
        self.ram = [0]*256
        # register
        self.reg = [0] * 8
        self.halt = False
        self.reg[SP] = 0
        self.comp = ''

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]
        program = []
        try:
            filename = sys.argv[1]
        except:
            print('Please add a valid file path')
        print(filename)
        with open(filename) as f:
            for line in f:
                line = line.split('#')[0]
                line = line.strip()

                if line == '':
                    continue

                # val = int(line)
                # print(line)
                program.append(int(line, 2))

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'CMP':
            value1 = self.reg[reg_a]
            value2 = self.reg[reg_b]

            if value1 == value2:
                self.comp = 'E'

            if value1 < value2:
                self.comp = 'L'

            if value1 > value2:
                self.comp = 'G'
        else:
            raise Exception("Unsupported ALU operation")

    # JMP  01010100 00000rrr
    # JEQ  01010101 00000rrr
    # CMP  10100111 00000aaa 00000bbb
    def operation(self, identifier):
        if identifier == 0b00000001:
            return "HLT"
        elif identifier == 0b10000010:
            return "LDI"
        elif identifier == 0b01000111:
            return "PRN"
        elif identifier == 0b10100000:
            return "ADD"
        elif identifier == 0b10100010:
            return "MUL"
        elif identifier == 0b01000101:
            return "PUSH"
        elif identifier == 0b01000110:
            return "POP"
        elif identifier == 0b01010000:
            return "CALL"
        elif identifier == 0b00010001:
            return "RET"
        elif identifier == 0b01010100:
            return "JMP"
        elif identifier == 0b01010101:
            return "JEQ"
        elif identifier == 0b10100111:
            return "CMP"
        elif identifier == 0b01010110:
            return "JNE"
        return None

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.program_counter,
            #self.fl,
            #self.ie,
            self.ram_read(self.program_counter),
            self.ram_read(self.program_counter + 1),
            self.ram_read(self.program_counter + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

    def HLT(self):
        self.halt = True
    
    def run(self):
        """Run the CPU."""
        
        while not self.halt:
            inc_size=0;
            instruction = self.ram_read(self.program_counter)
            # get operation name and values
            operation = self.operation(instruction)
            instruct_a = self.ram_read(self.program_counter + 1)
            instruct_b = self.ram_read(self.program_counter + 2)
            # print(operation)
            
            if operation == 'HLT':
                self.HLT()

            # if operation is LDI
            if operation == 'LDI':
                # get the two arguments, registry and value
                self.reg[instruct_a] = instruct_b
                inc_size = 3

            # if operation is PRN
            if operation == 'PRN':
                reg_index = instruct_a
                num = self.reg[reg_index]
                print(num)
                inc_size = 2
            
            if operation == 'ADD':
                self.alu("ADD", instruct_a, instruct_b)
                inc_size = 3

            if operation == 'MUL':
                self.alu("MUL", instruct_a, instruct_b)
                inc_size = 3

            if operation == 'PUSH':
                value = self.reg[instruct_a]
                # PUSH
                self.reg[SP] -= 1
                self.ram_write(self.reg[SP], value)
                inc_size = 2
                self.op_pc = False

            if operation == 'POP':
                value = self.ram_read(self.reg[SP])
                # POP
                self.reg[SP] += 1
                self.reg[instruct_a] = value
                inc_size = 2

            if operation == 'CALL':
                self.reg[SP] -= 1
                self.ram_write(self.reg[SP], self.program_counter + 2)
                self.program_counter = self.reg[instruct_a]

            if operation == 'RET':
                self.program_counter = self.ram_read(self.reg[SP])
                self.reg[SP] += 1

            if operation == 'CMP':
                self.alu('CMP',instruct_a,instruct_b)
                inc_size=3

            if operation == 'JEQ':
                if self.comp == 'E':
                    self.program_counter = self.reg[instruct_a]
                else:
                    inc_size += 2

            if operation == 'JNE':
                if self.comp == 'L' or self.comp == 'G':
                    self.program_counter = self.reg[instruct_a]
                else:
                    inc_size += 2

            if operation == 'JMP':
                print('JUMPING')
                self.program_counter = self.reg[instruct_a]

            
            self.program_counter += inc_size
            
    def ram_write(self, address, value):
        self.ram[address] = value
        return self.ram[address]
    
    def ram_read(self, address):
        return self.ram[address]

    def LDI(self, register, value):
        self.reg[int(register)] = value
        self.program_counter += 1
        return self.reg[int(register)]

    def PRN(self, register):
        print(int(self.reg[int(register)]))
        self.program_counter += 1
        return True