
class Parser:
    """
    Encapsulates access to the input code. Reads a VM command, parse it, and provides convenient access to its
    components. In addition, Removes all white space and comments.
    """
    def __init__(self, file_path):
        """
        function opens the input file and gets ready to parse it
        :param file_path: input file path
        """
        self.file = open(file_path)
        self.current_command = ""
        self.next_command = ''
        self.action_or_memory_segment = ""
        self.index = ""

    def has_more_commands(self):
        """
        function checks if there are more command in the file or we reached EOF and returns True or False accordingly
        """
        self.next_command = self.file.readline()
        if self.next_command == '':
            self.file.close()
            return False
        self.next_command = self.next_command.lstrip()  # removing whitespaces at the beginning of the command line
        self.next_command = self.next_command.split("//")[0]  # removing comments on command line
        while self.next_command == '':  # skipping comments and empty lines
            self.next_command = self.file.readline()
            if self.next_command == '':
                self.file.close()
                return False
            self.next_command = self.next_command.lstrip()  # removing whitespaces at the beginning of the command line
            self.next_command = self.next_command.split("//")[0]  # removing comments on command line
        return True

    def advance(self):
        """
        function makes the next command in the input file the current command
        """
        self.current_command = self.next_command

    def command_type(self):
        """
        function returns the type of the current command
        :return: "C_ARITHMETIC" or "C_PUSH" or "C_POP" according to the command type
        """
        self.action_or_memory_segment = ""  # initializing arguments values for each command
        self.index = ""
        command_parts = self.current_command.split()
        action = command_parts[0]  # action to be performed
        arithmetic_and_logical_commands = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"]
        if action == "return":
            return "C_RETURN"
        if action in arithmetic_and_logical_commands:
            self.action_or_memory_segment = action
            return "C_ARITHMETIC"
        self.action_or_memory_segment = command_parts[1]  # memory segment described in command
        if action == "pop" or action == "push" or action == "call" or action == "function":
            self.index = command_parts[2]  # index described in command
        if action == "push":
            return "C_PUSH"
        if action == "pop":
            return "C_POP"
        if action == "label":
            return "C_LABEL"
        if action == "goto":
            return "C_GOTO"
        if action == "if-goto":
            return "C_IF"
        if action == "function":
            return "C_FUNCTION"
        if action == "call":
            return "C_CALL"

    def arg1(self):
        """
        function returns the first argument of the current command
        """
        return self.action_or_memory_segment

    def arg2(self):
        """
        function returns the second argument of the current command
        """
        return self.index
