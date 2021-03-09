import CompilationEngine as CE
import os
import sys


def main():
    """
    A function that runs all the program
    """
    path = os.path.normpath(sys.argv[1])
    if os.path.isdir(path):
        generate_vm_for_directory(path)
    elif os.path.isfile(path):
        generate_vm_file(path)


def generate_vm_file(file_path):
    """
    function gets a jack file path and generates it into a vm file
    :param file_path: assembly file path
    """
    file_name = os.path.basename(file_path)
    dot_ind = file_name.find(".")
    file_name = file_name[:dot_ind] + ".vm"

    vm_file_address = os.path.split(file_path)[0]
    if vm_file_address == "":
        vm_file_address = file_name
    else:
        vm_file_address = os.path.join(vm_file_address, file_name)
    CE.CompilationEngine(file_path, vm_file_address)


def generate_vm_for_directory(path):
    """
    function gets directory path and translates all its jack files into vm files
    :param path: directory path
    """
    for file in os.listdir(path):
        if file.endswith(".jack"):
            file_path = os.path.join(path, file)
            generate_vm_file(file_path)


if __name__ == '__main__':
    main()
