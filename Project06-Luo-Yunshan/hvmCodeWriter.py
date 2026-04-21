"""
hvmCodeWriter.py -- Code Writer class for Hack VM translator
"""

import os
from hvmCommands import *

debug = False

class CodeWriter(object):
    
    def __init__(self, outputName):
        """
        Open 'outputName' and gets ready to write it.
        """
        self.file = open(outputName, 'w')
        self.SetFileName(outputName)

        self.labelNumber = 0
        self.returnLabel = None
        self.callLabel = None
        self.cmpLabels = {}
        self.needHalt = True


    def Debug(self, value):
        """
        Set debug mode.
        Debug mode writes useful comments in the output stream.
        """
        global debug
        debug = value


    def Close(self):
        """
        Write a jmp $ and close the output file.
        """
        if self.needHalt:
            if debug:
                self.file.write('    // <halt>\n')
            label = self._UniqueLabel()
            self._WriteCode('@%s, (%s), 0;JMP' % (label, label))
        self.file.close()


    def SetFileName(self, fileName):
        """
        Sets the current file name to 'fileName'.
        Restarts the local label counter.

        Strips the path and extension.  The resulting name must be a
        legal Hack Assembler identifier.
        """
        if (debug):
            self.file.write('    // File: %s\n' % (fileName))
        self.fileName = os.path.basename(fileName)
        self.fileName = os.path.splitext(self.fileName)[0]
        self.functionName = None


    def Write(self, line):
        """
        Raw write for debug comments.
        """
        self.file.write(line + '\n')

    def _UniqueLabel(self):
        """
        Make a globally unique label.
        The label will be _sn where sn is an incrementing number.
        """
        self.labelNumber += 1
        return '_' + str(self.labelNumber)


    def _LocalLabel(self, name):
        """
        Make a function/module unique name for the label.
        If no function has been entered, the name will be
        FileName$$name. Otherwise it will be FunctionName$name.
        """
        if self.functionName != None:
            return self.functionName + '$' + name
        else:
            return self.fileName + '$$' + name


    def _StaticLabel(self, index):
        """
        Make a name for static variable 'index'.
        The name will be FileName.index
        """
        return self.fileName + '.' + str(index)    


    def _WriteCode(self, code):
        """
        Write the comma separated commands in 'code'.
        """
        code = code.replace(',', '\n').replace(' ', '')
        self.file.write(code + '\n')
        



    def WritePushPop(self, commandType, segment, index):
        """
        Write Hack code for 'commandType' (C_PUSH or C_POP).
        'segment' (string) is the segment name.
        'index' (int) is the offset in the segment.
	To be implemented as part of Project 6
	
	    For push: Pushes the content of segment[index] onto the stack. It is a good idea to move the value to be pushed into a register first, then push the content of the register to the stack.
        For pop: Pops the top of the stack into segment[index]. You may need to use a general purpose register (R13-R15) to store some temporary results.
        Hint: Recall that there are 8 memory segments in the VM model, but only 5 of these exist in the assembly definition. Also, not all 8 VM segments allow to perform both pop and push on them. Chapter 7.3 of the book explains memory segment mapping.
        Hint: Use pen and paper first. Figure out how to compute the address of segment[index] (except for constant). Then figure out how you move the value of segment[index] into a register (by preference D). Then figure out how to push a value from a register onto the stack. 
        Hint: For pop, you already know how to compute the address of segment[index]. Store it in a temporary register (you can use R13 to R15 freely). Then read the value from the top of the stack, adjust the top of the stack, and then store the value at the location stored in the temporary register.
    
    PUSH constant is implemented as an example. Other solutions are possible too.

        """
        self.needHalt = False
        code = ''

        if commandType == C_PUSH:
            if segment in (T_ARGUMENT, T_LOCAL, T_THIS, T_THAT, T_STATIC):
                if segment == T_ARGUMENT:
                    segmentname = "ARG"
                elif segment == T_LOCAL:
                    segmentname = "LCL"
                elif segment == T_THIS:
                    segmentname = "THIS"
                elif segment == T_THAT:
                    segmentname = "THAT"
                elif segment == T_STATIC:
                    segmentname = str(self.fileName) + "." + str(index)
                self.Write("// push " + segment + " " + str(index))
                code += "@" + str(index) + "\n"
                code += "D=A" + "\n"
                code += "@" + segmentname + "\n"
                code += "D=D+M" + "\n"
                code += "A=D" + "\n"
                code += "D=M" + "\n"
                code += "@SP" + "\n"
                code += "A=M" + "\n"
                code += "M=D" + "\n"
                code += "@SP" + "\n"
                code += "M=M+1" + "\n"

            elif segment == T_TEMP:
                segmentname = "R" + str(5 + int(index))
                self.Write("// push " + segment + " " + str(index))
                code += "@" + segmentname + "\n"
                code += "D=M" + "\n"
                code += "@SP" + "\n"
                code += "A=M" + "\n"
                code += "M=D" + "\n"
                code += "@SP" + "\n"
                code += "M=M+1" + "\n"

            elif segment == T_CONSTANT:
                self.Write("// push " + segment + " " + str(index))
                code += "@" + str(index) + "\n"
                code += "D=A" + "\n"
                code += "@SP" + "\n"
                code += "A=M" + "\n"
                code += "M=D" + "\n"
                code += "@SP" + "\n"
                code += "M=M+1" + "\n"

            elif segment == T_POINTER:
                self.Write("// push " + segment + " " + str(index))
                if int(index) == 0:
                    code += "@THIS" + "\n"
                elif int(index) == 1:
                    code += "@THAT" + "\n"
                code += "D=M" + "\n"
                code += "@SP" + "\n"
                code += "A=M" + "\n"
                code += "M=D" + "\n"
                code += "@SP" + "\n"
                code += "M=M+1" + "\n"

            self.Write(code)

        elif commandType == C_POP:
            if segment in (T_ARGUMENT, T_LOCAL, T_THIS, T_THAT, T_STATIC):
                if segment == T_ARGUMENT:
                    segmentname = "ARG"
                elif segment == T_LOCAL:
                    segmentname = "LCL"
                elif segment == T_THIS:
                    segmentname = "THIS"
                elif segment == T_THAT:
                    segmentname = "THAT"
                elif segment == T_STATIC:
                    segmentname = str(self.fileName) + "." + str(index)
                self.Write("// pop " + segment + " " + str(index))
                code += "@" + str(index) + "\n"
                code += "D=A" + "\n"
                code += "@" + segmentname + "\n"
                code += "D=D+M" + "\n"
                code += "@R13" + "\n"
                code += "M=D" + "\n"
                code += "@SP" + "\n"
                code += "M=M-1" + "\n"
                code += "A=M" + "\n"
                code += "D=M" + "\n"
                code += "M=0" + "\n"
                code += "@R13" + "\n"
                code += "A=M" + "\n"
                code += "M=D" + "\n"

            elif segment == T_TEMP:
                segmentname = "R" + str(5 + int(index))
                self.Write("// pop " + segment + " " + str(index))
                code += "@" + segmentname + "\n"
                code += "D=A" + "\n"
                code += "@R13" + "\n"
                code += "M=D" + "\n"
                code += "@SP" + "\n"
                code += "M=M-1" + "\n"
                code += "A=M" + "\n"
                code += "D=M" + "\n"
                code += "M=0" + "\n"
                code += "@R13" + "\n"
                code += "A=M" + "\n"
                code += "M=D" + "\n"

            elif segment == T_POINTER:
                self.Write("// pop " + segment + " " + str(index))
                if int(index) == 0:
                    code += "@SP" + "\n"
                    code += "M=M-1" + "\n"
                    code += "A=M" + "\n"
                    code += "D=M" + "\n"
                    code += "M=0" + "\n"
                    code += "@THIS" + "\n"
                    code += "M=D" + "\n"
                elif int(index) == 1:
                    code += "@SP" + "\n"
                    code += "M=M-1" + "\n"
                    code += "A=M" + "\n"
                    code += "D=M" + "\n"
                    code += "M=0" + "\n"
                    code += "@THAT" + "\n"
                    code += "M=D" + "\n"

            self.Write(code)


    def WriteArithmetic(self, command):
        """
        Write Hack code for stack arithmetic 'command' (str).
    To be implemented as part of Project 6
        
        Compiles the arithmetic VM command into the corresponding ASM code. Recall that the operands (one or two, depending on the command) are on the stack and the result of the operation should be placed on the stack.
        The unary and the logical and arithmetic binary operators are simple to compile. 
         The three comparison operators (EQ, LT and GT) do not exist in the assembly language. The corresponding assembly commands are the conditional jumps JEQ, JLT and JGT. You need to implement the VM operations using these conditional jumps. You need two labels, one for the true condition and one for the false condition and you have to put the correct result on the stack.
        """
        if command == T_ADD:
            code = "@SP" + "\n"
            code += "M=M-1" + "\n"
            code += "A=M" + "\n"
            code += "D=M" + "\n"
            code += "A=A-1" + "\n"
            code += "M=D+M" + "\n"
            self.Write(code)

        elif command == T_SUB:
            code = "@SP" + "\n"
            code += "M=M-1" + "\n"
            code += "A=M" + "\n"
            code += "D=M" + "\n"
            code += "A=A-1" + "\n"
            code += "M=M-D" + "\n"
            self.Write(code)

        elif command == T_NEG:
            code = "@SP" + "\n"
            code += "A=M-1" + "\n"
            code += "M=-M" + "\n"
            self.Write(code)

        elif command == T_AND:
            code = "@SP" + "\n"
            code += "M=M-1" + "\n"
            code += "A=M" + "\n"
            code += "D=M" + "\n"
            code += "A=A-1" + "\n"
            code += "M=M&D" + "\n"
            self.Write(code)

        elif command == T_OR:
            code = "@SP" + "\n"
            code += "M=M-1" + "\n"
            code += "A=M" + "\n"
            code += "D=M" + "\n"
            code += "A=A-1" + "\n"
            code += "M=M|D" + "\n"
            self.Write(code)

        elif command == T_NOT:
            code = "@SP" + "\n"
            code += "A=M-1" + "\n"
            code += "M=!M" + "\n"
            self.Write(code)

        elif command in (T_EQ, T_GT, T_LT):
            label = self._UniqueLabel()
            true_label = "TRUE" + label
            end_label = "END" + label

            if command == T_EQ:
                jump = "JEQ"
            elif command == T_GT:
                jump = "JGT"
            else:
                jump = "JLT"

            # pop two values, compute x - y
            code = "@SP" + "\n"
            code += "M=M-1" + "\n"
            code += "A=M" + "\n"
            code += "D=M" + "\n"
            code += "A=A-1" + "\n"
            code += "D=M-D" + "\n"
            # jump to true if condition holds
            code += "@" + true_label + "\n"
            code += "D;" + jump + "\n"
            # false case: push 0
            code += "@SP" + "\n"
            code += "A=M-1" + "\n"
            code += "M=0" + "\n"
            code += "@" + end_label + "\n"
            code += "0;JMP" + "\n"
            # true case: push -1
            code += "(" + true_label + ")" + "\n"
            code += "@SP" + "\n"
            code += "A=M-1" + "\n"
            code += "M=-1" + "\n"
            code += "(" + end_label + ")" + "\n"
            self.Write(code)
    def WriteInit(self, sysinit = True):
        """
        Write the VM initialization code:
    To be implemented as part of Project 7
        """
        if (debug):
            self.file.write('    // Initialization code\n')


    def WriteLabel(self, label):
        """
        Write Hack code for 'label' VM command.
	To be implemented as part of Project 7

        """

    def WriteGoto(self, label):
        """
        Write Hack code for 'goto' VM command.
	To be implemented as part of Project 7
        """

    def WriteIf(self, label):
        """
        Write Hack code for 'if-goto' VM command.
	To be implemented as part of Project 7
        """
        

    def WriteFunction(self, functionName, numLocals):
        """
        Write Hack code for 'function' VM command.
	To be implemented as part of Project 7
        """


    def WriteReturn(self):
        """
        Write Hack code for 'return' VM command.
	To be implemented as part of Project 7
        """

    def WriteCall(self, functionName, numArgs):
        """
        Write Hack code for 'call' VM command.
	To be implemented as part of Project 7
        """

    
