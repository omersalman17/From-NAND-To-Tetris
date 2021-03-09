
SEGMENT_DICT = {"CONST": "constant", "ARG": "argument", "LOCAL": "local",
                "STATIC": "static", "THIS": "this", "THAT": "that",
                "POINTER": "pointer", "TEMP": "temp"}


class VMWriter:
    """
    This class writes vm into the files.
    """
    def __init__(self, output_filename):
        self.vm_file = open(output_filename, "w")

    def write_push(self, segment, index):
        """
        Writes a push command into a vm file
        :param segment: The segment to push
        :param index: An int
        :return: None
        """
        self.vm_file.write("push " + SEGMENT_DICT[segment] + " " + str(index) + "\n")

    def write_pop(self, segment, index):
        """
        Writes a pop command into a vm file
        :param segment: The segment to push
        :param index: An int
        :return: None
        """
        self.vm_file.write("pop " + SEGMENT_DICT[segment] + " " + str(index) + "\n")

    def write_arithmetic(self, command):
        """
        Writes an arithmetic command into a vm file
        :param command: The given arithmetic command
        :return: None
        """
        self.vm_file.write(command.lower()+"\n")

    def write_label(self, label):
        """
        Writes a label into a vm file
        :param label: A string
        :return: None
        """
        self.vm_file.write("label " + label + "\n")

    def write_goto(self, label):
        """
        Writes a goto statement into a vm file
        :param label: A string
        :return: None
        """
        self.vm_file.write("goto " + label + "\n")

    def write_if(self, label):
        """
        Writes a if statement into a vm file
        :param label: A string
        :return: None
        """
        self.vm_file.write("if-goto " + label + "\n")

    def write_call(self, name, num_of_args):
        """
        Writes a call command into a vm file
        :param name: The name of the function
        :param num_of_args: An int
        :return: None
        """
        self.vm_file.write("call " + name + " " + str(num_of_args) + "\n")

    def write_function(self, name, num_of_locals):
        """
        Writes a function into a vm file
        :param name: A name of the function
        :param num_of_locals: An int
        :return: None
        """
        self.vm_file.write("function " + name + " " + str(num_of_locals) + "\n")

    def write_return(self):
        """
        Writes a return command into a vm file
        :return: None
        """
        self.vm_file.write("return\n")

    def close(self):
        """
        closes the vm file
        :return:
        """
        self.vm_file.close()
