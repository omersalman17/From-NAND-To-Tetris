import sys
import os
import Parser as Pr
import CodeWriter as CW


def main():
    """
    main function that runs the program
    """
    path = os.path.normpath(sys.argv[1])
    writing_file = CW.CodeWriter(path)
    if os.path.isdir(path):
        generate_asm_for_directory(path, writing_file)
    elif os.path.isfile(path):
        generate_asm_file(path, writing_file)
    writing_file.close()


def generate_asm_file(file_abs_path, writing_file):
    """
    function generates .asm file
    :param file_abs_path: reading file absolute path
    :param writing_file: output file
    """
    file = Pr.Parser(file_abs_path)
    writing_file.set_file_name(os.path.basename(file_abs_path).strip(".vm"))
    while file.has_more_commands():
        file.advance()
        command_type = file.command_type()
        if command_type == "C_ARITHMETIC":
            command = file.arg1()
            writing_file.write_arithmetic(command)
        elif command_type == "C_PUSH" or command_type == "C_POP":
            segment = file.arg1()
            index = file.arg2()
            writing_file.write_push_pop(command_type, segment, index)
        elif command_type == "C_LABEL" or command_type == "C_GOTO" or command_type == "C_IF":
            label = file.arg1().upper()
            if command_type == "C_LABEL":
                writing_file.write_label(label)
            elif command_type == "C_GOTO":
                writing_file.write_goto(label)
            elif command_type == "C_IF":
                writing_file.write_if(label)
        elif command_type == "C_CALL" or command_type == "C_FUNCTION":
            function_name = file.arg1()
            if command_type == "C_CALL":
                args_num = file.arg2()
                writing_file.write_call(function_name, args_num)
            elif command_type == "C_FUNCTION":
                locals_num = file.arg2()
                writing_file.write_function(function_name, locals_num)
        elif command_type == "C_RETURN":
            writing_file.write_return()


def generate_asm_for_directory(dir_abs_path, writing_file):
    """
    function generates .asm file when given path points to a directory
    :param dir_abs_path: directory absolute path
    :param writing_file: output file
    """
    for file in os.listdir(dir_abs_path):
        if file.endswith(".vm"):
            file_abs_path = os.path.join(dir_abs_path, file)
            generate_asm_file(file_abs_path, writing_file)


if __name__ == '__main__':
    main()
