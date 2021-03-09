import sys
import os


def main():
    """
    main function that runs the program
    """
    path = os.path.normpath(sys.argv[1])
    if os.path.isdir(path):
        generate_hack_for_directory(path)
    elif os.path.isfile(path):
        generate_hack_file(path)


def get_comp_bin(comp_str):
    """
    function gets assembly comp command value and returns suited binary comp command value as described in the
     machine language.
    :param comp_str: assembly comp command value (string)
    :return: suited binary comp command value as described in the machine language.
    """
    comp_dict = {"0": "110101010", "1": "110111111", "-1": "110111010", "D": "110001100",
                 "A": "110110000", "!D": "110001101", "!A": "110110001", "-D": "110001111",
                 "-A": "110110011", "D+1": "110011111", "A+1": "110110111", "D-1": "110001110",
                 "A-1": "110110010", "D+A": "110000010", "D-A": "110010011", "A-D": "110000111",
                 "D&A": "110000000", "D|A": "110010101", "M": "111110000", "!M": "111110001",
                 "-M": "111110011", "M+1": "111110111", "M-1": "111110010", "D+M": "111000010",
                 "D-M": "111010011", "M-D": "111000111", "D&M": "111000000", "D|M": "111010101",
                 "D<<": "010110000", "D>>": "010010000", "A<<": "010100000",
                 "A>>": "010000000", "M<<": "011100000", "M>>": "011000000"}
    return comp_dict[comp_str]


def get_dest_bin(dest_str):
    """
    function gets assembly dest command value and returns suited binary dest command value as described in the
     machine language.
    :param dest_str: assembly dest command value (string)
    :return: suited binary dest command value as described in the machine language.
    """
    dest_dict = {"null": "000", "M": "001", "D": "010", "MD": "011",
                 "A": "100", "AM": "101", "AD": "110", "AMD": "111"}
    return dest_dict[dest_str]


def get_jmp_bin(jmp_str):
    """
    function gets assembly jmp command value and returns suited binary jmp command value as described in the
     machine language.
    :param jmp_str: assembly jmp command value (string)
    :return: suited binary jmp command value as described in the machine language.
    """
    jmp_dict = {"null": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
                "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}
    return jmp_dict[jmp_str]


def get_binary_rep_a(line):
    """
    function gets an assembly A_command line and returns it's translation to binary value according to the
     machine language.
    :param line: assembly A_command line (string)
    :return: command translation to binary value according to the machine language.
    """
    binary_rep = "{0:b}".format(int(line))
    binary_rep = str(binary_rep)
    num_of_zeros_to_add = 16 - len(binary_rep)
    while num_of_zeros_to_add != 0:
        binary_rep = "0" + binary_rep
        num_of_zeros_to_add = 16 - len(binary_rep)
    return binary_rep


def get_binary_rep_c(line):
    """
    function gets an assembly C_command line and returns it's translation to binary value according to the
     machine language.
    :param line: assembly C_command line (string)
    :return: command translation to binary value according to the machine language.
    """
    dest_ind = line.find("=")
    if dest_ind == -1:
        dest = "null"
    else:
        dest = line[:dest_ind]
    jmp_ind = line.find(";")
    if jmp_ind == -1:
        jmp = "null"
    else:
        jmp = line[jmp_ind + 1:]
    comp = "no comp value"
    if dest != "null" and jmp != "null":
        comp = line[dest_ind + 1:jmp_ind]
    elif dest == "null":
        comp = line[:jmp_ind]
    elif jmp == "null":
        comp = line[dest_ind + 1:]
    dest_bin = get_dest_bin(dest)
    comp_bin = get_comp_bin(comp)
    jmp_bin = get_jmp_bin(jmp)
    binary_rep = "1" + comp_bin + dest_bin + jmp_bin
    return binary_rep


def get_default_symbol_table():
    """
    function returns default symbol table (dictionary) as described in unit 6.
    """
    symbol_tabel = {"SP": "0", "LCL": "1", "ARG": "2", "THIS": "3",
                    "THAT": "4", "R1": "1", "R2": "2", "R3": "3",
                    "R4": "4", "R5": "5", "R6": "6", "R7": "7",
                    "R8": "8", "R9": "9", "R10": "10", "R11": "11",
                    "R12": "12", "R13": "13", "R14": "14", "R15": "15",
                    "SCREEN": "16384", "KBD": "24576", "R0": "0"}
    return symbol_tabel


def first_pass(asm_file_address, symbol_table):
    """
    first pass of the assembly program as described in the Hack Assembler implementation suggestion in unit 6.
    :param asm_file_address: address of the assembly file to be translated to machine language.
    :param symbol_table: symbol table sutied for the assembly file.
    """
    asm_file = open(asm_file_address)
    address_counter_rom = 0
    for line in asm_file:
        line = remove_line_comments_and_whitespaces(line)
        if line == '':
            continue
        if line.startswith("(") and line.endswith(")"):
            start_ind = line.find("(")
            end_ind = line.find(")")
            symbol = line[start_ind + 1:end_ind]
            symbol_table[symbol] = address_counter_rom
        else:
            address_counter_rom += 1
    asm_file.close()


def second_pass(asm_file_address, symbol_table):
    """
    second pass of the assembly program as described in the Hack Assembler implementation suggestion in unit 6.
    :param asm_file_address: address of the assembly file to be translated to machine language.
    :param symbol_table: symbol table sutied for the assembly file.
    """
    address_counter_ram = 16
    asm_file = open(asm_file_address)
    file_name = os.path.basename(asm_file_address)
    dot_ind = file_name.find(".")
    file_name = file_name[:dot_ind] + ".hack"
    hack_file_address = os.path.split(asm_file_address)[0]
    if hack_file_address == "":
        hack_file_address = file_name
    else:
        hack_file_address = os.path.join(hack_file_address, file_name)
    hack_file = open(hack_file_address, "w")
    for line in asm_file:
        line = remove_line_comments_and_whitespaces(line)
        if line == '' or line.startswith("("):
            continue
        if line.startswith("@"):
            address_counter_ram, line = get_decimal_value_a(line, symbol_table, address_counter_ram)
            binary_rep = get_binary_rep_a(line)
        else:
            binary_rep = get_binary_rep_c(line)
        hack_file.write(binary_rep + "\n")
    asm_file.close()
    hack_file.close()


def get_decimal_value_a(line, symbol_table, address_counter_ram):
    """
    function gets assembly A_command line, symbol table and counter of the RAM addresses being used by variables
     and returns updated RAM addresses counter and the decimal value of the variable/label described in the
      A_command according to the symbol table.
    :param line: assembly A_command line (string)
    :param symbol_table: symbol table of the assembly file
    :param address_counter_ram: counter of the RAM addresses being used by variables
    :return: updated RAM addresses counter and the decimal value of the variable/label described in the A_command
    according to the symbol table.
    """
    line = line.lstrip("@")
    if not line.isdigit():
        if line not in symbol_table:
            symbol_table[line] = address_counter_ram
            address_counter_ram += 1
        line = symbol_table[line]
    return address_counter_ram, line


def generate_hack_file(file_path):
    """
    function gets an assembly file path and generates its Hack translation file.
    :param file_path: assembly file path
    """
    symbol_table = get_default_symbol_table()
    first_pass(file_path, symbol_table)
    second_pass(file_path, symbol_table)


def generate_hack_for_directory(path):
    """
    function gets directory path and translates all it's assembly file ito Hack files.
    :param path: directory path
    """
    for file in os.listdir(path):
        if file.endswith(".asm"):
            file_abs_path = os.path.join(path, file)
            generate_hack_file(file_abs_path)


def remove_line_comments_and_whitespaces(line):
    """
    function gets a line in the assembly file, removes it's whitespaces and comments and returns the assembly command.
    :param line: a line in the assembly file (string)
    :return: only the assembly command without any whitespaces or comments.
    """
    line = "".join(line.split())  # removing whitespaces
    line = line.split("//")  # removing comments
    return line[0]


if __name__ == '__main__':
    main()
