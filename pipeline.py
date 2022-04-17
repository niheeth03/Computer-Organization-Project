import simuRisc as simuRisc
import re

clocks = 0
stalls = 0


class pipelinestages:
    def __init__(self, currentline, forward, stallsleft, breakdown):
        self.currentline = currentline
        self.stallsleft = stallsleft
        self.breakdown = []
        self.forward = forward
        self.data = []

    @staticmethod
    def breakinstruction(currentline):
        breakdown = []
        # print("crl: ",currentline)
        line = simuRisc.lines[currentline].strip()
        line = line.split(sep=" ", maxsplit=1)
        #print(line,"sdsf")
        f=line[1]
        #print(line)
        breakdown.append(line[0].strip()) 
        line[1] = re.findall("[a-z][0-9]", line[1])
        for l in line[1]:
            l = l.strip()
            if l[0]!='x':
                breakdown.append(l)
        f = re.findall("zero", f)
        for l in f:
            l = l.strip()
            breakdown.append(l)
        
        
        return breakdown





        
               
simuRisc.removeCOMMandEMPLIN()
simuRisc.DataProcess()
base_instructionline_ProgramCounter = simuRisc.ProgramCounter
enable = False
ProgramDone = False


if input("Want to enable data forwarding?(y/n)").lower() == "y":
    enable = True
    print("Data Forwarding Enabled")
else:
    print("Data Forwarding Disabled")

pipelineunits = [
    pipelinestages(currentline=simuRisc.ProgramCounter, stallsleft=0, breakdown=[], forward=enable),  # IF
    pipelinestages(currentline=simuRisc.ProgramCounter, stallsleft=0, breakdown=[], forward=enable),  # ID
    pipelinestages(currentline=simuRisc.ProgramCounter, stallsleft=0, breakdown=[], forward=enable),  # EX
    pipelinestages(currentline=simuRisc.ProgramCounter, stallsleft=0, breakdown=[], forward=enable),  # MEM
    pipelinestages(currentline=simuRisc.ProgramCounter, stallsleft=0, breakdown=[], forward=enable)]  # WB


def loadtonextstage(pipelinenumber):
    pipelineunits[pipelinenumber].currentline += 1

while not ProgramDone:
    #print(base_instructionline_ProgramCounter)
    for i in range(5):        pipelineunits[i].stallsleft = max(0, pipelineunits[i].stallsleft - 1)
    clocks += 1

    print("Clock cycle Number",clocks)

# Write Back


    if len(pipelineunits[4].data) < 1:
        loadtonextstage(4)
        print("Write_Back is free")

    else:
        (instructiostallcode, instructionline, memorylocation) = pipelineunits[4].data[0]
        pipelineunits[4].data.pop(0)
        successful_write = 1
        if instructiostallcode not in ("sw", "bne", "beq", "jr", "j", "stall"):

            
            if instructiostallcode in "lw":
                memoryresult = memorylocation
                successful_write = simuRisc.writeback(instructionline, memoryresult)

 
            elif instructiostallcode in ("add", "sub", "lui", "addi", "li", "sll", "srl", "slt"):
                operationresult = memorylocation
                successful_write = simuRisc.writeback(instructionline, operationresult)

            if successful_write == -1:
                
                ProgramDone = True

        print("Executed WB on line ", instructiostallcode, instructionline)

# Memory
    
    if len(pipelineunits[3].data) < 1:
        loadtonextstage(3)
        print("Memory is free")
    else:
        (instructiostallcode, instructionline, operationresult) = pipelineunits[3].data[0]
        pipelineunits[3].data.pop(0)
        if instructiostallcode in ("lw", "sw"):
            memoryresult = simuRisc.memori(instructiostallcode, instructionline, operationresult)
            pipelineunits[3].currentline += 1
            pipelineunits[4].data.append((instructiostallcode, instructionline, memoryresult))
        else:
            loadtonextstage(3)
            pipelineunits[4].data.append((instructiostallcode, instructionline, operationresult))

        print("Executed MEM on line ", instructiostallcode, instructionline)

# Execute
   
    if len(pipelineunits[2].data) < 1:
        loadtonextstage(2)
        print("Execute is free") 
    else:
        
        (instructiostallcode, instructionline) = pipelineunits[2].data[0]
        # print(pipelineunits[2].data[0])
        # print(instructionline,instructiostallcode)
        if instructiostallcode !="stall":
            s= instructiostallcode+" "+instructionline

            (operationresult, instructionline) = simuRisc.Instruction(s)
        elif instructiostallcode=="stall":
            operationresult=0
            instructionline=0
        pipelineunits[2].data.pop(0)



        pipelineunits[2].currentline += 1


        pipelineunits[3].data.append((instructiostallcode, instructionline, operationresult))

        if (instructiostallcode in ("add", "slt", "srl", "sll", "addi", "sll", "lui", "sub")) and enable:
            successful_write = simuRisc.writeback(instructionline, operationresult)

        print("Executed EX on line ", instructiostallcode, instructionline)

#ID/RF

    if len(pipelineunits[1].data) < 1 or pipelineunits[1].stallsleft:
        loadtonextstage(1)
        print("Instruction Decode/Register fetch is free")
    else:


        
            linefetch = pipelineunits[1].data[0]
            pipelineunits[1].data.pop(0)
            (instructiostallcode, instructionline) = simuRisc.instructiontype(linefetch)
            pipelineunits[2].data.append((instructiostallcode, instructionline))

            if instructiostallcode in ("bne", "beq", "j"):

                if instructiostallcode == "bne":
                    return_bne_line = simuRisc.bne(instructionline, pipelineunits[0].currentline - 1)
                    if return_bne_line != pipelineunits[0].currentline:
                        pipelineunits[0].currentline = return_bne_line
                        stalls += 1
                        pipelineunits[0].stallsleft += 1
                elif instructiostallcode == "beq":
                    return_bne_line = simuRisc.beq(instructionline, pipelineunits[0].currentline - 1)
                    if return_bne_line != pipelineunits[0].currentline:
                        pipelineunits[0].currentline = return_bne_line
                        stalls += 1
                        pipelineunits[0].stallsleft += 1
                elif instructiostallcode == "j":
                    return_bne_line = simuRisc.j(instructionline)
                    pipelineunits[0].currentline = return_bne_line
                    stalls += 1
                    pipelineunits[0].stallsleft += 1

        # else:

                pipelineunits[1].currentline += 1

            print("Executed ID/RF on line ", linefetch)    


# Instruction fetch
    def instruction_fetch():
        linefetch = simuRisc.lines[pipelineunits[0].currentline]
        pipelineunits[0].currentline += 1
        return linefetch

    if pipelineunits[0].stallsleft or pipelineunits[0].currentline >= simuRisc.Reg["ra"]:
        print("Execution halted due to a stall")
        print(" ")

    else:      
        
        linefetch = instruction_fetch()
        pipelineunits[1].data.append(linefetch)
        print("Executed IF on line ", linefetch)
        print(" ")

    
    if len(simuRisc.ecalls) and pipelineunits[0].currentline - 1 == simuRisc.ecalls[0]:
        simuRisc.syscall_instr(simuRisc.ecalls[0])
        simuRisc.ecalls.pop(0)


    if (len(pipelineunits[2].data) == 0) and (len(pipelineunits[2].data) == 0) and (len(
            pipelineunits[3].data) == 0) and (len(pipelineunits[4].data) == 0) and pipelineunits[0].currentline >= simuRisc.Reg["ra"]:
                ProgramDone = True


print("Total Clock Cycles: ", clocks)
print("Total Stalls: ", stalls)
