import os


class CodeWriter:
    """
    Translates VM command into Hack assembly code.
    """
    def __init__(self, path):
        """
        Opens the output file and gets ready to write into it
        :param path: path of file or directory in order to generate output file accordingly
        """
        name = os.path.basename(path)
        w_file_path = os.path.split(path)[0]
        if os.path.isfile(path):
            name = name.strip(".vm")
        elif os.path.isdir(path):
            w_file_path = os.path.join(w_file_path, name)
        w_file_path = os.path.join(w_file_path, name)
        w_file_path = w_file_path + ".asm"
        self.w_file = open(w_file_path, "w")
        self.current_vm_file_name = ""
        self.labels_counter = 0
        self.function_calls_counter = 0
        self.current_function_name = ""
        self.write_init()

    def set_file_name(self, file_name):
        """
        Informs the code writer that the translation of a new VM file is started
        :param file_name: new vm file name
        """
        self.current_vm_file_name = file_name
        self.w_file.write("\n// FILE: " + file_name + "\n\n")

    def write_arithmetic(self, command):
        """
        Writes the assembly code that is the translation of the given arithmetic command
        :param command: given command (string)
        """
        self.w_file.write("// " + command + "\n")
        operator = get_suited_operator(command)
        asm_code = ""
        if command == "eq" or command == "gt" or command == "lt":
            self.labels_counter += 1
            lbl_c = str(self.labels_counter)
            asm_code = get_comparison_asm_command(command, lbl_c)
        elif command == "add" or command == "sub":
            asm_code = "@SP\nM=M-1\nA=M\nD=M\n@SP\nM=M-1\nA=M\nM=M" + operator + "D\n@SP\nM=M+1\n"
        elif command == "and" or command == "or":
            asm_code = "@SP\nM=M-1\nA=M\nD=M\n@SP\nM=M-1\nA=M\nD=D" + operator + "M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        elif command == "not" or command == "neg":
            asm_code = "@SP\nM=M-1\nA=M\nM=" + operator + "M\n@SP\nM=M+1\n"
        self.w_file.write(asm_code)

    def write_push_pop(self, command, segment, index):
        """
        Writes the assembly code that is the translation of the given command, where command is one of the two
         values: "C_PUSH" or "C_POP".
        :param command: command (string)
        :param segment: segment (string)
        :param index: index (string)
        """
        seg_dict = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
        self.w_file.write("// " + command + " " + segment + " " + index + "\n")
        index = get_suited_index(segment, index)
        asm_code = ""
        if command == "C_PUSH":
            push_asm = "@SP\nA=M\nM=D\n@SP\nM=M+1\n"  # insert D register value to stack & inc SP as expected
            if segment == "constant":
                asm_code = "@" + index + "\nD=A\n" + push_asm
            elif segment == "temp" or segment == "pointer":
                asm_code = "@" + index + "\nD=M\n" + push_asm
            elif segment == "static":
                asm_code = "@" + self.current_vm_file_name + "." + index + "\nD=M\n" + push_asm
            elif segment in seg_dict:
                asm_code = "@" + seg_dict[segment] + "\nD=M\n@" + index + "\nD=D+A\nA=D\nD=M\n" + push_asm
        elif command == "C_POP":
            pop_asm = "@SP\nM=M-1\nA=M\nD=M\n"  # pop stack value and insert it to D register
            if segment == "temp" or segment == "pointer":
                asm_code = pop_asm + "@" + index + "\nM=D\n"
            elif segment == "static":
                asm_code = pop_asm + "@" + self.current_vm_file_name + "." + index + "\nM=D\n"
            elif segment in seg_dict:
                asm_code = "@" + seg_dict[segment] + "\nD=M\n@" + index + "\nD=D+A\n@address\nM=D\n" + pop_asm + \
                           "@address\nA=M\nM=D\n"
        self.w_file.write(asm_code)

    def close(self):
        """
        closes the output file
        """
        self.w_file.close()

    def write_init(self):
        """
        Initializes the stack pointer and calls the Sys init function.
        :return: None
        """
        self.w_file.write("@256\nD=A\n@SP\nM=D\n")
        self.write_call("Sys.init", "0")

    def write_label(self, label):
        """
        writes the label code in assembly
        :param label: A string
        :return: None
        """
        label = label + "_" + self.current_function_name
        self.w_file.write("// label " + label + "\n")
        asm_code = "(" + label + ")\n"
        self.w_file.write(asm_code)

    def write_goto(self, label):
        """
        Writes the goto command in assembly
        :param label: A string
        :return: None
        """
        label = label + "_" + self.current_function_name
        self.w_file.write("// goto " + label + "\n")
        asm_code = "@" + label + "\n0;JMP\n"
        self.w_file.write(asm_code)

    def write_if(self, label):
        """
        Writes the if command in assembly code
        :param label: A string
        :return: None
        """
        label = label + "_" + self.current_function_name
        self.w_file.write("// if-goto " + label + "\n")
        asm_code = "@SP\nM=M-1\nA=M\nD=M\n@" + label + "\nD;JNE\n"
        self.w_file.write(asm_code)

    def write_call(self, function_name, args_num):
        """
        Writes the call function in assembly
        :param function_name: A string
        :param args_num: The number of arguments for
        the function ( A string)
        :return: None
        """
        self.w_file.write("// call " + function_name + " " + args_num + "\n")
        function_return_address = function_name + "_return_address_" + str(self.function_calls_counter)
        push_return_address = "@" + function_return_address + "\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        push_lcl = "@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        push_arg = "@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        push_this = "@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        push_that = "@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
        handle_arg = "@" + str(int(args_num) + 5) + "\nD=A\n@SP\nD=M-D\n@ARG\nM=D\n"
        handle_lcl = "@SP\nD=M\n@LCL\nM=D\n"
        goto = "@" + function_name + "\n0;JMP\n"
        return_address_label = "(" + function_return_address + ")\n"
        self.w_file.write(push_return_address)
        self.w_file.write(push_lcl)
        self.w_file.write(push_arg)
        self.w_file.write(push_this)
        self.w_file.write(push_that)
        self.w_file.write(handle_arg)
        self.w_file.write(handle_lcl)
        self.w_file.write(goto)
        self.w_file.write(return_address_label)
        self.function_calls_counter += 1

    def write_function(self, function_name, locals_num):
        """
        Writes the function command in assembly.
        :param function_name: A string
        :param locals_num: A string. The number of local variables
        :return: None
        """
        self.w_file.write("// function " + function_name + " " + locals_num + "\n")
        function_push_0 = "PUSH_0_" + function_name
        function_no_push = "NO_PUSH_" + function_name
        self.current_function_name = function_name
        asm_code_0 = "(" + function_name + ")\n"
        asm_code_1 = "@" + locals_num + "\nD=A\n@locals_num_var\nM=D\n@" + function_push_0 + "\nD;JGT\n"
        asm_code_2 = "@" + function_no_push + "\n0;JMP\n"
        asm_code_3 = "(" + function_push_0 + ")\n@SP\nA=M\nM=0\n@SP\nM=M+1\n@locals_num_var\nM=M-1\nD=M\n"
        asm_code_4 = "@" + function_push_0 + "\nD;JGT\n(" + function_no_push + ")\n"
        self.w_file.write(asm_code_0)
        self.w_file.write(asm_code_1)
        self.w_file.write(asm_code_2)
        self.w_file.write(asm_code_3)
        self.w_file.write(asm_code_4)

    def write_return(self):
        """
        Writes the return command for a function in assembly code
        :return: None
        """
        self.w_file.write("// return \n")
        frame = "@LCL\nD=M\n@frame\nM=D\n"
        ret = "@5\nD=D-A\nA=D\nD=M\n@ret\nM=D\n"
        dereference_arg = "@SP\nM=M-1\nA=M\nD=M\n@ARG\nA=M\nM=D\n"
        sp = "@ARG\nD=M\n@SP\nM=D+1\n"
        that = "@frame\nA=M-1\nD=M\n@THAT\nM=D\n"
        this = "@2\nD=A\n@frame\nA=M-D\nD=M\n@THIS\nM=D\n"
        arg = "@3\nD=A\n@frame\nA=M-D\nD=M\n@ARG\nM=D\n"
        lcl = "@4\nD=A\n@frame\nA=M-D\nD=M\n@LCL\nM=D\n"
        goto = "@ret\nA=M\n0;JMP\n"
        self.w_file.write(frame)
        self.w_file.write(ret)
        self.w_file.write(dereference_arg)
        self.w_file.write(sp)
        self.w_file.write(that)
        self.w_file.write(this)
        self.w_file.write(arg)
        self.w_file.write(lcl)
        self.w_file.write(goto)


def get_comparison_asm_command(command, lbl_c):
    """
    function gets command and labels counter and returns translation to suited assembly code
    :param command: command (string)
    :param lbl_c: labels counter (string)
    :return:
    """
    asm_code = ""
    suited_jmp = get_suited_jmp(command)
    load_stack_value = "@SP\nM=M-1\nA=M\nD=M\n"  # load stack value into D register and decrement SP value
    asm_code_end = "@INSERT_TRUE_" + lbl_c + "\nD;" + suited_jmp + "\nD=0\n@END_" + lbl_c + \
                   "\n0;JMP\n(INSERT_TRUE_" + lbl_c + ")\nD=-1\n(END_" + lbl_c + ")\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
    if command == "eq":
        asm_code = load_stack_value + "@SP\nM=M-1\nA=M\nD=M-D\n" + asm_code_end
    elif command == "gt" or command == "lt":
        v1, v2 = "0", "-1"  # variables to insert False or True to stack
        if command == "lt":
            v1, v2 = "-1", "0"
        asm_code = load_stack_value + "@y\nM=D\n" + load_stack_value + "@x\nM=D\n@y\nD=M\n@Y_POS_" + lbl_c + \
                   "\nD;JGT\n@Y_NEG_" + lbl_c + "\nD;JLT\n" + \
                   "(Y_POS_" + lbl_c + ")\n" + "@x\nD=M\n@BOTH_SAME_" + lbl_c + "\nD;JGT\nD=" + v1 + \
                   "\n@END_" + lbl_c + "\n0;JMP\n" + \
                   "(Y_NEG_" + lbl_c + ")\n@x\nD=M\n@BOTH_SAME_" + lbl_c + "\nD;JLT\nD=" + v2 + \
                   "\n@END_" + lbl_c + "\n0;JMP\n" + \
                   "(BOTH_SAME_" + lbl_c + ")\n@y\nD=M\n@x\nD=M-D\n" + asm_code_end
    return asm_code


def get_suited_index(segment, index):
    """
    function gets segment and index and returns suited index for the assembly translation
    :param segment: segment (string)
    :param index: index (string)
    :return: suited index for the assembly translation (string)
    """
    index = int(index)
    if segment == "pointer":
        index += 3
    elif segment == "temp":
        index += 5
    index = str(index)
    return index


def get_suited_jmp(command):
    """
    function gets command and returns suited jmp string for the assembly translation
    :param command: command (string)
    :return: suited jmp string for the assembly translation
    """
    if command == "eq":
        return "JEQ"
    elif command == "gt":
        return "JGT"
    elif command == "lt":
        return "JLT"


def get_suited_operator(command):
    """
    function gets command and returns suited operator string for the assembly translation
    :param command: command (string)
    :return: suited operator string for the assembly translation
    """
    if command == "add":
        return "+"
    elif command == "sub":
        return "-"
    elif command == "and":
        return "&"
    elif command == "or":
        return "|"
    elif command == "not":
        return "!"
    elif command == "neg":
        return "-"
