import sys

PC = 0
ACC = 0

REGISTERS = [0] * 255

# ran out of binary, cheated a bit and used another digit instead of refactoring
# code
OPCODES = {
    "OUT":"0001",
    "STA":"0010",
    "LAD":"0011",
    "ADD":"0100",
    "SUB":"0101",
    "JMP":"0111",
    "JNE":"1000",
    "JIE":"1001",
    "CMP":"1010",
    "HLT":"1011",
    "INP":"1101",
    "JIL":"1110",
    "JIG":"1111",
    "JGE":"1112",
    "JLE":"1121",
}

# work out base to store the program in the last registers of memory
def calc_base():
    base = 0
    with open(sys.argv[1], "r") as f:
        for line in f:
            base += 1
    base = 254-base
    return base

# hold an operation and its opcodes e.g. ADD 1, 2
class Instruction:
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand

    def print_operation(self):
        str = self.op + " " + ",".join(self.operand)
        print(str)


class CPU:
    def __init__(self, REGISTERS, PC, ACC, OPCODES):
        self.REGISTERS = REGISTERS
        self.PC = PC
        self.ACC = ACC
        self.OPCODES = OPCODES

    # encode and write the instructions to memory
    def write_instructions(self, instructions, base):
        operations = []

        with open(instructions, "r") as f:

            for line in f:

                instruction = line.replace("\n","")
                
                # retrieve the operation e.g. ADD  
                op = instruction.split()[0]
                
                # get the opcode for the said operation
                opcode = self.OPCODES[op]

                #retrieve the data being operated on, "+1" because there is a space
                operand = instruction[len(op)+1:]
                operand = operand.replace(",", " ")
                operands = operand.split(" ")
                bin_operands = ""

                for data in operands:
                    
                    if data == "":
                        continue
                    
                    # if register 
                    # TODO: CHARACTER INPUT
                    if data[0] == "R":
                        # make binary data 8bit
                        formatted_data = format(int(data[1:]),"08b")
                        # set leading bit to 1 to represent register
                        formatted_data = "1" + formatted_data

                        bin_operands += formatted_data
                    elif not data[0].isnumeric():
                        asc = ord(data[0])
                        formatted_data = format(asc, "08b")
                        bin_operands += formatted_data
                    else:
                        # make binary data 8bit
                        formatted_data = format(int(data),"08b")
                        # as it is not a register let leading bit to 0
                        formatted_data = "0" + formatted_data
                        bin_operands += formatted_data

                encoded_op = opcode + bin_operands
                operations.append(encoded_op)
        
        self.PC = base

        for op in operations:
            # save the encoded operation into memory 
            self.REGISTERS[self.PC] = op 
            self.PC += 1

        top = self.PC
        self.PC = 0
        return top


    # fetch the binary instructions from memory
    def fetch(self, base, top):
        bin_instructions = [] 
        self.PC = base
        # fetch all instructions between the base and the top
        while self.PC < top:
            bin_instructions.append(self.REGISTERS[self.PC])
            self.PC += 1

        return bin_instructions


    # decode the binary instructions into the Instruction class
    def decode(self, bin_instructions):
        decoded = []

        for instruction in bin_instructions:
            #retrieve the opcode
            opcode = instruction[:4]
            # retrieve the name of the operand e.g. 0010 -> STA
            op = list(self.OPCODES.keys())[list(self.OPCODES.values()).index(opcode)]
            decoded_operands = []
            # retrieve the operations
            operands = instruction[4:]
            # set index to 9 as each operand is 9 bits (with the leading bit)
            # will retrieve everything before this index 
            index = 9
            n = len(operands) + 9

            while index < n :
                # retrieve the data/register specified by the first 9 bits of the 
                # operand, will shorted so the first 9 bits will always be the next
                # register
                bin_operand = operands[:index]
                # remove the retrieved operand from the list of the operands
                # so the next time you check the first 9 digits, they will be the 
                # new next operand
                operands = operands[index:]
                # if the leading bit is a 1, preceed the decoded instruction with
                # an "R" to show it is a register
                data = "R" if bin_operand[0] == "1" else ""
                # ignore leading bit to get the value of the operand
                operand_wo = bin_operand[1:]
                # add the base 10 number to the decoded operand, will be preceeded
                # with an "R" if it is a register
                data += str(int(operand_wo,2))
                decoded_operands.append(data)
                # increase index by 9 as you want the next 9 digits
                index += 9

            # save decoded instruction inside an Instruction class
            operation = Instruction(op,decoded_operands)
            decoded.append(operation)

        return decoded

    def interpret(self, op):
        if op.op == "ADD":
            # store the result
            sum = 0
            # summ up all data in the operand
            for n in op.operand:
                if n[0] == "R":
                    # if it is a register sum the data in the register
                    register = n[1:]
                    sum += int(self.REGISTERS[int(register)])
                else:
                    sum += int(n)
            # set the ACC to the sum
            self.ACC = sum

        if op.op == "SUB":
            #subtract all values in the operand from the first value in the 
            # operand
            if op.operand[0][0] == "R":
                # if register get value in register
                # register [1:] because ignore the leading "R"
                register = op.operand[0][1:]
                total = int(self.REGISTERS[int(register)])
            else:
                total = int(op.operand[0])


            for i,n in enumerate(op.operand):
                # subtract all from first operand, so make sure it is not the 
                # first operand
                if i != 0:
                    if n[0] == "R":
                        # if register get value in register
                        # register [1:] because ignore the leading "R"
                        register = n[1:]
                        total -= int(self.REGISTERS[int(register)])
                    else:
                        total -= int(n)

                # set the ACC to the result of the calculation
                self.ACC = total
            

        if op.op == "OUT":
            # if printing a register print data from register
            if len(op.operand) > 0:
                register = op.operand[0][1:]
                print(self.REGISTERS[int(register)])
            # if no operand print ACC
            else:
                print(self.ACC)

        # store value in the ACC
        if op.op == "STA":
            register = op.operand[0][1:]    
            # if no data specified, store value in the ACC
            if len(op.operand) == 1:
                self.REGISTERS[int(register)] = self.ACC
            else:
                data = op.operand[1]
                # if data is reigster store data in register
                if data[0] == "R":
                    data_register = data[1:]
                    data = self.REGISTERS[int(data_register)]
                elif not data[0].isnumeric():
                    char = data[0]
                    data = ord(char)
                    
                self.REGISTERS[int(register)] = data 

        # load instruction 
        if op.op == "LAD":
            for n in op.operand:
                # if register load data in the register to the ACC else,
                # load the number
                if n[0] == "R":
                    register = n[1:]
                    self.ACC = self.REGISTERS[int(register)]
                elif not n[0].isnumeric():
                    char = n[0]
                    self.ACC = ord(char)
                else:
                    self.ACC = int(n)


        if op.op == "INP":
            data = input(":")
            if not data[0].isnumeric():
                data = ord(data[0])
            self.ACC = data

    
    def excecute(self, instructions):
        print("")
        print("-"*10,"OUT","-"*10)
        
        self.PC = 0
            
        # loop through instruction with the PC to point to the current instruction
        # the PC will be changes with the JUMPS
        while self.PC < len(instructions): 
            # get current operation
            op = instructions[self.PC]
            
            self.interpret(op)
            self.PC += 1

            if op.op == "JMP":
                self.PC = int(op.operand[0]) - 1

            # jump if equal to 0
            if op.op == "JIE":
                if self.REGISTERS[254] == 0:
                    self.PC = int(op.operand[0]) - 1

            # jump not if equal to 0: equal to 1
            if op.op == "JNE":
                if self.REGISTERS[254] != 0:
                    self.PC = int(op.operand[0]) - 1

            if op.op == "JIG":
                if self.REGISTERS[254] > 0:
                    self.PC = int(op.operand[0]) - 1
            

            if op.op == "JIL":
                if self.REGISTERS[254] < 0:
                    self.PC = int(op.operand[0]) - 1
            

            if op.op == "JGE":
                if self.REGISTERS[254] >= 0:
                    self.PC = int(op.operand[0]) - 1


            if op.op == "JLE":
                if self.REGISTERS[254] <= 0:
                    self.PC = int(op.operand[0]) - 1

            if op.op == "CMP":
                val = op.operand[0]

                # if value is a register fetch data from register
                if val[0] == "R":
                    register = val[1:]
                    val = self.REGISTERS[int(register)]

                val = int(val)

                # if the value in the ACC and the value bring compared are the same
                # set the result to 0 else set it to 1
                res = val - int(self.ACC) 

                # the last register represents the EAX register and is where 
                # ther result of comparisons are stored
                self.REGISTERS[254] = res
            

    def run(self, base,top):
        # Fetch binary instruction from memory
        bin_instructions = self.fetch(base, top)

        # Decode the binary instruction and save in array 
        decoded = self.decode(bin_instructions)


        self.excecute(decoded)
        print(self.REGISTERS)


    def encode(self, instructions, base):
        top = self.write_instructions(instructions, base)
        return top



CPU = CPU(REGISTERS,PC,ACC,OPCODES)

base = calc_base()

# Store the Assembly program in memory in binary

top = CPU.encode(sys.argv[1],base)

# Fetch - Decode - Excecute
CPU.run(base,top)



