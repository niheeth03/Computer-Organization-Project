import re
file = open("../fd.asm", "r")
lines = file.readlines()
file.close()

global ProgramCounter
ProgramCounter = 0

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
'r': 0, 
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
        if position>=0:
            j = position
            lines[i] = lines[i][:j]
            lines[i]=lines[i].strip()
        i += 1

global Memory, Memory_iter, Memory_label
Memory = []
Memory_iter = 0
Memory_label = {}


def DataProcess():
    Memory.clear()
    i = 0
    while i < len(lines):
        if re.search(r"^\.data", lines[i]):
            while True:
                i += 1
                if re.findall(r"^\.text", lines[i]):
                    i -= 1
                    break
                if lines[i][0] != '.':
                    s = lines[i].split(sep=':', maxsplit=1)
                    lines[i] = s[1].strip()
                    s = s[0].strip()
                    global Memory_iter
                    Memory_label[s] = Memory_iter
                
                if re.findall(r"^\.asciiz", lines[i]):
                    line = lines[i][9:len(lines[i]) - 1]
                    line = re.sub(r"\\n", "\n", line)
                    line = re.sub(r"\\t", "\t", line)
                    Memory.append(line)
                    Memory_iter += 1

                elif re.findall(r"^\.word", lines[i]):
                    line = lines[i][6:]
                    line = line.split(sep=',')
                    for l in line:
                        l = l.strip()
                        Memory.append(int(l))
                        Memory_iter += 1
                else:
                    SyntaxError.error(i)
                    return
        if re.findall(r"^\.globl", lines[i]):
            i += 1
            break

        i += 1

    print("Initial Memory:\n", Memory)
    global ProgramCounter
    ProgramCounter = i

global labelnames
labelnames={}

def labelstore():
    i=ProgramCounter
    #print(i)
    while i < len(lines):
        if re.findall(r"^\w*:", lines[i]):
            label = lines[i].split(sep=":", maxsplit=1)
            label=label[0].strip()
            labelnames[label] = i

        if re.findall(r"^\w*\s*:", lines[i]):
            label = lines[i].split(sep=":", maxsplit=1)
            label = label[0].strip()
            labelnames[label] =i
        
        i+=1

def executeline():
    global ProgramCounter
    ProgramCounter = Instruction(lines[ProgramCounter])

global Console
Console=[]


def main():
    removeCOMMandEMPLIN()
    DataProcess()
    labelstore()
    while ProgramCounter<len(lines):
        executeline()
    print("Final Memory state: \n", Memory)
    print("=" * 100)
    print("Register values: \n", Reg)
    print("Console:\n",Console)
    #print(labelnames)
    #print(lines[ProgramCounter-1])



def Instruction(line):
    if re.findall(r"^\w*\s*:", line):
        #print(234)
        return ProgramCounter + 1

    instructionopcode = line.split(sep=" ", maxsplit=1)
    instructionopcode = instructionopcode[0]
    #print(instructionopcode)
    if instructionopcode == 'add':
        return add(line)
    elif instructionopcode == 'sub':
        return sub(line)
    elif instructionopcode == 'lw':
        return lw(line)
    elif instructionopcode == 'sw':
        return sw(line)
    elif instructionopcode == 'li':
        return li(line)
    elif instructionopcode == 'la':
        return la(line)
    elif instructionopcode == 'sll':
        return sll(line)
    elif instructionopcode == 'srl':
        return srl(line)
    elif instructionopcode == 'bne':
        return bne(line)
    elif instructionopcode == 'beq':
        return beq(line)
    elif instructionopcode == 'addi':
        return addi(line)
    elif instructionopcode == 'j':
        return j(line)
    elif instructionopcode == 'jr':
        return len(lines)
    elif instructionopcode == 'lui':
            return lui(line)
    elif instructionopcode == 'ecall':
        # print(1)
        return ecall()
    else:
        print("Invalid Instruction Set ")
        SyntaxError.error(ProgramCounter)
        return len(lines)

def add(instructionregister):
    instructionregister=instructionregister.split(" ")
    instructionregister=instructionregister[1]
    instructionregister = instructionregister.split(",")
    for l in range(len(instructionregister)):
        instructionregister[l] = str(instructionregister[l].strip())
    if type(Reg[instructionregister[1]])==str and type(Reg[instructionregister[2]])==str :
        Reg[instructionregister[0]] = int(Reg[instructionregister[1]][2:]) + int(Reg[instructionregister[2][2:]])
        Reg[instructionregister[0]] = "0x" + str(Reg[instructionregister[0]])
    if  type(Reg[instructionregister[1]])==str and type(Reg[instructionregister[2]])==int:
        Reg[instructionregister[0]] = int(Reg[instructionregister[1]][2:]) + int(Reg[instructionregister[2]])
        Reg[instructionregister[0]] = "0x" + str(Reg[instructionregister[0]])
    elif type(Reg[instructionregister[1]])==int and type(Reg[instructionregister[2]])==str:
        Reg[instructionregister[0]] = int(Reg[instructionregister[1]]) // 4 + int(Reg[instructionregister[2]][2:])
        Reg[instructionregister[0]] = "0x" + str(Reg[instructionregister[0]])
    elif type(Reg[instructionregister[1]])==int and type(Reg[instructionregister[2]])==int:
        Reg[instructionregister[0]] = int(Reg[instructionregister[1]]) + int(Reg[instructionregister[2]])
    else:
        SyntaxError.error(ProgramCounter)
    return ProgramCounter+1


def sub(instructionregister):
    instructionregister=instructionregister.split(" ")
    instructionregister=instructionregister[1]
    instructionregister = instructionregister.split(",")
    for l in range(len(instructionregister)):
        instructionregister[l] = str(instructionregister[l].strip())
    if type(Reg[instructionregister[1]])==str and type(Reg[instructionregister[2]])==str :
        Reg[instructionregister[0]] = int(Reg[instructionregister[1]][2:]) - int(Reg[instructionregister[2][2:]])
        Reg[instructionregister[0]] = "0x" + str(Reg[instructionregister[0]])
    elif type(Reg[instructionregister[1]])==str and type(Reg[instructionregister[2]])==int:
        Reg[instructionregister[0]] = int(Reg[instructionregister[1]][2:]) - int(Reg[instructionregister[2]])
        Reg[instructionregister[0]] = "0x" + str(Reg[instructionregister[0]])
    elif type(Reg[instructionregister[1]])==int and type(Reg[instructionregister[2]])==str:
        Reg[instructionregister[0]] = int(Reg[instructionregister[1]]) // 4 - int(Reg[instructionregister[2]][2:])
        Reg[instructionregister[0]] = "0x" + str(Reg[instructionregister[0]])
    elif type(Reg[instructionregister[1]])==int and type(Reg[instructionregister[2]])==int:
        Reg[instructionregister[0]] = int(Reg[instructionregister[1]]) - int(Reg[instructionregister[2]])

    else:
        SyntaxError.error(ProgramCounter)
    return ProgramCounter+1


def lw(instructionregister):
    instructionregister=instructionregister.split(" ")
    instructionregister=instructionregister[1]
    instructionregister = instructionregister.split(",")
    instructionregister[0] = str(instructionregister[0].strip())
    instructionregister[1] = instructionregister[1].strip()
    offset = int(instructionregister[1].split(sep="(", maxsplit=1)[0])
    #print(offset)
    instructionregister[1] = instructionregister[1].split(sep="(",)[1][:-1]
    Reg[instructionregister[0]] = Memory[(int(Reg[instructionregister[1]][2:])-int(Address[2:])+offset)//4]
    return ProgramCounter+1


def sw(instructionregister):
    instructionregister=instructionregister.split(" ")
    instructionregister=instructionregister[1]
    instructionregister = instructionregister.split(",")
    instructionregister[0] = str(instructionregister[0].strip())
    instructionregister[1] = instructionregister[1].strip()
    offset = int(instructionregister[1].split(sep="(", maxsplit=1)[0])
    instructionregister[1] = instructionregister[1].split(sep="(")[1][:-1]
    Memory[(int(Reg[instructionregister[1]][2:]) - int(Address[2:]) + offset)//4] = int(Reg[instructionregister[0]])
    return ProgramCounter+1


def bne(instructionregister):
    instructionregister=instructionregister.split(" ")
    instructionregister=instructionregister[1]
    instructionregister = instructionregister.split(",")
    for l in range(len(instructionregister)):
        instructionregister[l] = str(instructionregister[l].strip())
    if Reg[instructionregister[0]] == Reg[instructionregister[1]]:
        return ProgramCounter+1
    return int(labelnames[instructionregister[2]])


def beq(instructionregister):
    instructionregister=instructionregister.split(" ")
    instructionregister=instructionregister[1]
    instructionregister = instructionregister.split(",")
    for l in range(len(instructionregister)):
        instructionregister[l] = str(instructionregister[l].strip())
    if Reg[instructionregister[0]] != Reg[instructionregister[1]]:
        return ProgramCounter+1
    return int(labelnames[instructionregister[2]])


def j(instructionregister):
    instructionregister=instructionregister.split(" ")
    instructionregister=instructionregister[1]
    return labelnames[instructionregister]


def lui(instructionregister):
    instructionregister=instructionregister.split(" ")
    instructionregister=instructionregister[1]
    instructionregister = instructionregister.split(",")
    instructionregister[0] = instructionregister[0].strip()
    instructionregister[1] = instructionregister[1].strip()
    Reg[instructionregister[0]] = instructionregister[1]
    global Address
    Address = str(instructionregister[1])
    return ProgramCounter+1


def addi(instructionregister):
    instructionregister=instructionregister.split(" ")
    instructionregister=instructionregister[1]
    instructionregister = instructionregister.split(",")
    for l in range(len(instructionregister)):
        instructionregister[l] = str(instructionregister[l].strip())
    if type(Reg[instructionregister[1]])==str :
        Reg[instructionregister[0]] = int(Reg[instructionregister[1]][2:]) + int(instructionregister[2])// 4
        Reg[instructionregister[0]] = "0x" + str(Reg[instructionregister[0]])
    else:
        Reg[instructionregister[0]] = int(Reg[instructionregister[1]]) + int(instructionregister[2])
    return ProgramCounter+1

def sll(instructionregister):
    instructionregister=instructionregister.split(" ")
    instructionregister=instructionregister[1]
    instructionregister = instructionregister.split(",")
    for l in range(len(instructionregister)):
        instructionregister[l] = str(instructionregister[l].strip())
    Reg[instructionregister[0]] = int(Reg[instructionregister[1]]) * pow(2, int(instructionregister[2]))
    return ProgramCounter + 1


def srl(instructionregister):
    instructionregister=instructionregister.split(" ")
    instructionregister=instructionregister[1]
    instructionregister = instructionregister.split(",")
    for l in range(len(instructionregister)):
        instructionregister[l] = str(instructionregister[l].strip())
    Reg[instructionregister[0]] = int(Reg[instructionregister[1]]) // pow(2, int(instructionregister[2]))
    return ProgramCounter + 1


def li(instructionregister):
    instructionregister=instructionregister.split(" ")
    instructionregister=instructionregister[1]
    instructionregister = instructionregister.split(",")
    for l in range(len(instructionregister)):
        instructionregister[l] = str(instructionregister[l].strip())
    Reg[instructionregister[0]] = int(instructionregister[1])
    return ProgramCounter+1


def la(instructionregister):
    instructionregister=instructionregister.split(" ")
    instructionregister=instructionregister[1]
    instructionregister = instructionregister.split(",")
    instructionregister[0] = str(instructionregister[0].strip())
    instructionregister[1] = str(instructionregister[1].strip())
    Reg[instructionregister[0]] = int(Address[2:])+Memory_label[instructionregister[1]]
    Reg[instructionregister[0]] = "0x" + str(Reg[instructionregister[0]])
    return ProgramCounter+1


def ecall():
    line1 = lines[ProgramCounter - 1]
    line1 = line1.split(sep=" ")
    line1[1]= line1[1].split(sep=",")
    line1[0] = line1[0].strip()
    line1[1][0] = line1[1][0].strip()
    line1[1][1] = line1[1][1].strip()
    # print(line1[1][0])
    if line1[0]=="li" and line1[1][0]=='a7':
        if int(line1[1][1]) == 10:
            return len(lines)
        else:
            line2 =lines[ProgramCounter - 2]
            line2 =line2.split(sep=" ")
            line2[1]=line2[1].split(sep=",")
            line2[0]=line2[0].strip()
            line2[1][0]=line2[1][0].strip()
            line2[1][1]=line2[1][1].strip()
            
            if int(line1[1][1]) == 1:
                Console.append(Reg[line2[1][1]])
                # print(Reg[line2[1][1]])
            elif int(line1[1][1]) == 4:
                Console.append(Memory[Memory_label[line2[1][1]]])
                print(Memory[Memory_label[line2[1][1]]])
            elif int(line1[1][1])==5:
                line3=lines[ProgramCounter+1]
                line3=line3.split(sep=" ",maxsplit=1)
                line3[1]=line3[1].split(sep=",")
                line3[1][0]=line3[1][0].strip()
                num=input()
                Reg[line3[1][0]]=int(num)
            else:
                Console.append("Niheeth")

    return ProgramCounter+1

main()
