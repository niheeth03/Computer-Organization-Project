import re

file = open("fd.asm", "r")
lines = file.readlines()
file.close()

global ProgramCounter
ProgramCounter = 0
ecalls=[]

class ErrorInSyntax:
    def __init__(self, error, linenumber):
        self.error = error
        self.linenumber = linenumber

    def error(self, index):
        print("We are unable to process the line '", lines[index], "Sorry for the inconvenience.")
        self.error = True
        self.linenumber = index
        global ProgramCounter
        ProgramCounter = len(lines)


global i

Reg = {
    'zero': 0,
    'ra': 0,
    'sp': 0,
    'gp': 0,
    'tp': 0,
    't0': 0,
    't1': 0,
    't2': 0,
    's0': 0,
    's1': 0,
    'a0': 0,
    'a1': 0,
    'a2': 0,
    'a3': 0,
    'a4': 0,
    'a5': 0,
    'a6': 0,
    'a7': 0,
    's2': 0,
    's3': 0,
    's4': 0,
    's5': 0,
    's6': 0,
    's7': 0,
    's8': 0,
    's9': 0,
    's10': 0,
    's11': 0,
    't3': 0,
    't4': 0,
    't5': 0,
    't6': 0,
    
}

Address = "0x1000"

SyntaxError = ErrorInSyntax(error=False, linenumber=0)


def removeCOMMandEMPLIN():
    global i
    i = 0
    while i < len(lines):
        lines[i] = lines[i].strip()
        if re.findall(r"^# *", lines[i]) or (re.findall(r"^\n", lines[i]) and len(lines[i] == '\n'.length())):
            lines.remove(lines[i])
            i -= 1
        if len(lines[i]) == 0:
            lines.remove(lines[i])
            i -= 1
        position = lines[i].find('#')
        if position >= 0:
            j = position
            lines[i] = lines[i][:j]
            lines[i] = lines[i].strip()
        if re.findall(r"^ecall", lines[i]):
            ecalls.append(i - 1)
            lines.remove(lines[i])

        i += 1


global Memory, Memory_iter, Memory_label
Memory = []
Memory_iter = 0
Memory_label = {}


def pre_process_data(i, lines):
    # print("In data section")
    i += 1
    while i < len(lines):

        lines[i] = lines[i].strip()
        # Process data segment until .text is seen
        if re.findall(r"^\.text", lines[i]):
            i -= 1
            # print("Exiting data section")
            # print("i", i)
            return i
        if re.findall(r"^\.globl", lines[i]):
            continue

        # Process labels
        if lines[i][0] != '.':
            # print(lines[i])
            s = lines[i].split(sep=':', maxsplit=1)  # new line after label for .word
            lines[i] = s[1].strip()

            s = s[0].strip()
            global Memory_iter
            Memory_label[s] = 10010000+(4*Memory_iter)
            Memory_label[s]="0x"+str(Memory_label[s])

        # Process int values
        if re.findall(r"^\.word", lines[i]):
            #print(lines[i])
            line = lines[i][6:]
            # line = re.sub(r',', '', line)
            line = line.split(sep=',')  # rm spaces for array
            for l in line:
                l = l.strip()
                Memory.append(int(l))
                Memory_iter += 1

        # Process strings
        elif re.findall(r"^\.asciiz", lines[i]):
            # print(lines[i])
            line = lines[i][9:len(lines[i]) - 1]
            line = re.sub(r"\\n", "\n", line)
            line = re.sub(r"\\t", "\t", line)
            Memory.append(line)
            Memory_iter += 1

        else:
            SyntaxError.error(i)
            return
        i += 1
    return i


def pre_process_text(i, lines):
    ProgramCounter = i
    # print("In text section")
    while i < len(lines):
        # print(i)

        pos = lines[i].find('#')
        if re.findall(r"^\.data", lines[i]):
            i = i - 1
            break
        if re.findall(r"^\.globl", lines[i]):
            i = i + 1
            continue
        if pos >= 0:
            j = pos
            while lines[i][j - 1] == ' ':
                j -= 1
            lines[i] = lines[i][:j]
        i += 1

    # print("Processed labels")

    i = ProgramCounter
    while i < len(lines):
        lines[i] = lines[i].strip()
        if re.findall(r"^\.data", lines[i]):
            i = i - 1
            return i
        if re.findall(r"^\w*:", lines[i]):
            label_name_array = lines[i].split(sep=":", maxsplit=1)
            label_name = label_name_array[0].strip()
            if len(label_name_array[1]) == 0:
                lines.remove(lines[i])
            labelnames[label_name] = i


        i += 1
    return i


def DataProcess():
    Memory.clear()
    i = 0
    while i < len(lines):
        # .data
        lines[i] = lines[i].strip()
        #print(lines[i])
        if re.search(r"^\.data", lines[i]):
            i = pre_process_data(i, lines)
        elif re.findall(r"^\.globl", lines[i]):
            i = i + 1
            continue
        elif re.findall(r"^\.text", lines[i]):
            i = pre_process_text(i, lines)
        i = i + 1
    Reg["ra"]=len(lines)
    print("\n")
    print("Initial Memory:")
    for x in Memory:
        print(str(x)+" ",end=" ")
    print("\n")
    
    Reg["ra"] = len(lines)
    global ProgramCounter
    ProgramCounter = labelnames["main"]+1


global labelnames
labelnames = {}

def memori(word,line,offset):
   # print("LINEE",Reg[line[1]])
    if word=="lw":
        
        print(Reg[line[1]][2:])
        result = Memory[(int(Reg[line[1]][2:]) - 10010000 + offset) // 4]
    elif word=="sw":
        Memory[(int(Reg[line[1]][2:]) - 10010000 + offset) // 4] = int(
            Reg[line[0]])
        result=Memory[(int(Reg[line[1]][2:]) - 10010000 + offset) // 4] 
    return result

def writeback(line,result):
    Reg[line[0]]=result


class Line(object):
    def __init__(self,text):
        self.text=text

    def add(self,instructionregister):
        #print(instructionregister)
        instructionregister =  instructionregister.split(" ",maxsplit=1)
        instructionregister = instructionregister[1]
        instructionregister = instructionregister.split(",")
        for l in range(len(instructionregister)):
            instructionregister[l] = str(instructionregister[l].strip())
        if type(Reg[instructionregister[1]]) == str and type(Reg[instructionregister[1]]) == str:
            result = int(Reg[instructionregister[1]][2:]) + int(Reg[instructionregister[2][2:]])
            result = "0x" + str(Reg[instructionregister[0]])
        if type(Reg[instructionregister[1]]) == str and type(Reg[instructionregister[2]]) == int:
            result = int(Reg[instructionregister[1]][2:]) + int(Reg[instructionregister[2]])
            result = "0x" + str(Reg[instructionregister[0]])
        elif type(Reg[instructionregister[1]]) == int and type(Reg[instructionregister[2]]) == str:
            result = int(Reg[instructionregister[1]])  + int(Reg[instructionregister[2]][2:])
            result = "0x" + str(Reg[instructionregister[0]])
        elif type(Reg[instructionregister[1]]) == int and type(Reg[instructionregister[2]]) == int:
            result = int(Reg[instructionregister[1]]) + int(Reg[instructionregister[2]])
        else:
            SyntaxError.error(ProgramCounter)
            result=-1
        return result,instructionregister

    def sub(self,instructionregister):
        #print(instructionregister)
        instructionregister =  instructionregister.split(" ",maxsplit=1)
        instructionregister = instructionregister[1]
        instructionregister = instructionregister.split(",")
        for l in range(len(instructionregister)):
            instructionregister[l] = str(instructionregister[l].strip())
        if type(Reg[instructionregister[1]]) == str and type(Reg[instructionregister[2]]) == str:
            result = int(Reg[instructionregister[1]][2:]) - int(Reg[instructionregister[2][2:]])
            result = "0x" + str(Reg[instructionregister[0]])
        elif type(Reg[instructionregister[1]]) == str and type(Reg[instructionregister[2]]) == int:
            result = int(Reg[instructionregister[1]][2:]) - int(Reg[instructionregister[2]])
            result = "0x" + str(Reg[instructionregister[0]])
        elif type(Reg[instructionregister[1]]) == int and type(Reg[instructionregister[2]]) == str:
            result = int(Reg[instructionregister[1]]) - int(Reg[instructionregister[2]][2:])
            result = "0x" + str(Reg[instructionregister[0]])
        elif type(Reg[instructionregister[1]]) == int and type(Reg[instructionregister[2]]) == int:
            result = int(Reg[instructionregister[1]]) - int(Reg[instructionregister[2]])

        else:
            SyntaxError.error(ProgramCounter)
            result=-1
        return result,instructionregister

    def lw(self, instructionregister):
        #print(instructionregister)
        instructionregister = instructionregister.split(" ", maxsplit=1)
        instructionregister = instructionregister[1]
        instructionregister = instructionregister.split(",")
        instructionregister[0] = str(instructionregister[0].strip())
        instructionregister[1] = instructionregister[1].strip()
        offset = int(instructionregister[1].split(sep="(", maxsplit=1)[0])
        # print(offset)
        instructionregister[1] = instructionregister[1].split(sep="(", )[1][:-1]
        #print(Reg[instructionregister[0]],instructionregister[0])
       # print(Reg[instructionregister[1]],instructionregister[1],Memory[(int(Reg[instructionregister[1]][2:]) - 10010000 + offset) // 4])

        return offset,instructionregister

    def sw(self, instructionregister):
        #print(instructionregister)
        instructionregister = instructionregister.split(" ", maxsplit=1)
        instructionregister = instructionregister[1]
        instructionregister = instructionregister.split(",")
        instructionregister[0] = str(instructionregister[0].strip())
        instructionregister[1] = instructionregister[1].strip()
        offset = int(instructionregister[1].split(sep="(", maxsplit=1)[0])
        instructionregister[1] = instructionregister[1].split(sep="(")[1][:-1]
        return offset,instructionregister

    def bne(self,instructionregister,PC):
        #print(instructionregister)
        instructionregister =  instructionregister.split(" ",maxsplit=1)
        instructionregister = instructionregister[1]
        instructionregister = instructionregister.split(",")
        for l in range(len(instructionregister)):
            instructionregister[l] = str(instructionregister[l].strip())
        if Reg[instructionregister[0]] == Reg[instructionregister[1]]:
            return PC + 1
        return int(labelnames[instructionregister[2]])

    def beq(self,instructionregister,PC):
        #print(instructionregister)
        instructionregister =  instructionregister.split(" ",maxsplit=1)
        instructionregister = instructionregister[1]
        instructionregister = instructionregister.split(",")
        for l in range(len(instructionregister)):
            instructionregister[l] = str(instructionregister[l].strip())
        if Reg[instructionregister[0]] != Reg[instructionregister[1]]:
            return PC + 1
        return int(labelnames[instructionregister[2]])

    def j(self,instructionregister):
        #print(instructionregister)
        instructionregister = instructionregister.split(" ", maxsplit=1)
        instructionregister = instructionregister[1]
        return labelnames[instructionregister]

    def lui(self, instructionregister):
        #print(instructionregister)
        instructionregister = instructionregister.split(" ", maxsplit=1)
        instructionregister = instructionregister[1]
        instructionregister = instructionregister.split(",")
        instructionregister[0] = instructionregister[0].strip()
        instructionregister[1] = instructionregister[1].strip()
        global Address
        Address=str(instructionregister[1])
        return instructionregister[1],instructionregister

    def addi(self, instructionregister):
        #print(instructionregister)
        instructionregister = instructionregister.split(" ", maxsplit=1)
        instructionregister = instructionregister[1]
        instructionregister = instructionregister.split(",")
        for l in range(len(instructionregister)):
            instructionregister[l] = str(instructionregister[l].strip())
        #print(Reg[instructionregister[1]], "addi")
        if isinstance(Reg[instructionregister[1]], str):
            result = int(Reg[instructionregister[1]][2:]) + int(instructionregister[2])
            result = "0x" + str(Reg[instructionregister[0]])
        else:
            result = int(Reg[instructionregister[1]]) + int(instructionregister[2])
        #print(Reg[instructionregister[0]])
        return result,instructionregister

    def sll(self,instructionregister):
        #print(instructionregister)
        instructionregister =  instructionregister.split(" ",maxsplit=1)
        instructionregister = instructionregister[1]
        instructionregister = instructionregister.split(",")
        for l in range(len(instructionregister)):
            instructionregister[l] = str(instructionregister[l].strip())
        result = int(Reg[instructionregister[1]]) * pow(2, int(instructionregister[2]))
        return result,instructionregister

    def slt(self,instructionregister):
        # slt $t4, $s3, $s4               #set $t4 = 1 if $s3 < $s4
        #print(instructionregister)
        instructionregister = instructionregister.split(" ", maxsplit=1)
        instructionregister = instructionregister[1]
        instructionregister = instructionregister.split(",")
        for l in range(len(instructionregister)):
            instructionregister[l] = str(instructionregister[l].strip())
        result = int(int(Reg[instructionregister[1]]) < int(Reg[instructionregister[2]]))
        return result,instructionregister

    def srl(self,instructionregister):
        #print(instructionregister)
        instructionregister = instructionregister.split(" ", maxsplit=1)
        instructionregister = instructionregister[1]
        instructionregister = instructionregister.split(",")

        for l in range(len(instructionregister)):
            instructionregister[l] = str(instructionregister[l].strip())
        result= int(Reg[instructionregister[1]]) // pow(2, int(instructionregister[2]))
        return result,instructionregister

    def li(self,instructionregister):
        #print(instructionregister)

        instructionregister =  instructionregister.split(" ",maxsplit=1)
        instructionregister = instructionregister[1]
        instructionregister = instructionregister.split(",")

        for l in range(len(instructionregister)):
            instructionregister[l] = str(instructionregister[l].strip())
        instructionregister[1] = instructionregister[1].strip()
        result = int(instructionregister[1])
        #print(Reg[instructionregister[0]],"li")
        return result,instructionregister

    def la(self,instructionregister):
        #print(instructionregister)
        instructionregister = instructionregister.split(" ",maxsplit=1)

        instructionregister = instructionregister[1]
        instructionregister = instructionregister.split(",")
        instructionregister[0] = str(instructionregister[0].strip())
        instructionregister[1] = str(instructionregister[1].strip())
        result =Memory_label[instructionregister[1]]
        return result,instructionregister

    def jal(self,instructionregister):
        instructionregister = instructionregister.split(" ", maxsplit=1)
        instructionregister = instructionregister[1]
        global ProgramCounter
        Reg["ra"]= ProgramCounter + 1
        ProgramCounter=labelnames[instructionregister]
        return ProgramCounter

    def move(self,instructionregister):
        instructionregister = instructionregister.split(" ", maxsplit=1)

        instructionregister = instructionregister[1]
        instructionregister = instructionregister.split(",")
        instructionregister[0] = str(instructionregister[0].strip())
        instructionregister[1] = str(instructionregister[1].strip())
        result=Reg[instructionregister[1]]
        return result,instructionregister

    def jr(self,instructionregister):
        ProgramCounter=Reg["ra"]
        return ProgramCounter




    def bge(self,instructionregister):
        instructionregister = instructionregister.split(" ", maxsplit=1)

        instructionregister = instructionregister[1]
        instructionregister = instructionregister.split(",")
        instructionregister[0] = str(instructionregister[0].strip())
        instructionregister[1] = str(instructionregister[1].strip())

        if(Reg[instructionregister[0]]>=Reg[instructionregister[1]]):
            return labelnames[str(instructionregister[2].strip())]
        else:
            return ProgramCounter+1

    def mul(self,instructionregister):
        instructionregister = instructionregister.split(" ", maxsplit=1)

        instructionregister = instructionregister[1]
        instructionregister = instructionregister.split(",")
        for l in range(len(instructionregister)):
            instructionregister[l] = str(instructionregister[l].strip())
        Reg[instructionregister[0]] = int(Reg[instructionregister[1]])*int(Reg[instructionregister[2]])

    def div(self, instructionregister):
        instructionregister = instructionregister.split(" ", maxsplit=1)

        instructionregister = instructionregister[1]
        instructionregister = instructionregister.split(",")
        for l in range(len(instructionregister)):
            instructionregister[l] = str(instructionregister[l].strip())
        Reg[instructionregister[0]] = int(Reg[instructionregister[1]])//int(Reg[instructionregister[2]])


    def ecall(self,instructionregister):
        value=Reg["a7"]

        if int(value) == 10:
            return len(lines)


        if int(value) == 1:
            Console.append(Reg["a0"])
            # print(Reg[line2[1][1]])
        elif int(value) == 4:
            address=Reg["a0"][2:]
            location=(int(address)-10010000)//4
            String=Memory[location]
            Console.append(String)

        elif int(value) == 5:
            num = input()
            Reg["a7"] = int(num)
        else:
            Console.append()

        return ProgramCounter + 1
    def generic(self):
        SyntaxError.error(ProgramCounter)
        return len(lines)




def executeline():
    global ProgramCounter
    ProgramCounter = Instruction(lines[ProgramCounter])


global Console
Console = []


def main():
    removeCOMMandEMPLIN()
    DataProcess()

    # print(labelnames)
    

    print("Registers: \n")
    j=0
    for key,values in Reg.items():
        print("\t\t\t\t"+"x"+str(j)+"\t\t"+key+"\t\t"+str(values))
        j=j+1
    
    print("Final Memory: ")
    for x in Memory:
        print(str(x)+" ",end=" ")
    print("\n")
    print("Console:")
    for x in Memory:
        print(str(x)+" ",end=" ")
    print("\n")
    # print(labelnames)
    # print(lines[ProgramCounter-1])
def instructiontype(line):
    
    word = line.split(sep=" ", maxsplit=1)
    try:
        line = word[1]
    except:
        pass
    word = word[0]

    return word, line

def Instruction(line):
    x=Line(line)
    #print(x)
    if re.findall(r"^\w*\s*:", x.text):
        return ProgramCounter + 1

    instructiostallcode = line.split(sep=" ", maxsplit=1)
    instructiostallcode = instructiostallcode[0]
    visitor = getattr(x, instructiostallcode)
    return visitor(line)

main()
