TYPE_INDEX = 0
KIND_INDEX = 1
RUNNING_INDEX = 2


class SymbolTable:
    """
    A symbol table for a vm file
    """
    def __init__(self):
        self.class_symbol_table = {}
        self.subroutine_symbol_table = {}
        self.kinds_var_counters_dict = {"STATIC": 0, "FIELD": 0, "ARG": 0, "VAR": 0}

    def start_subroutine(self):
        """
        Starts a new subroutine function with a new subroutine
        symbol table
        :return:
        """
        self.subroutine_symbol_table = {}
        self.kinds_var_counters_dict["ARG"] = 0
        self.kinds_var_counters_dict["VAR"] = 0

    def define(self, name, type, kind):
        """
        Adds a new variable to the symbol table
        :param name: The name of the variable
        :param type: The type of the variable
        :param kind:The kind either "STATIC", "FIELD", "ARG" or "VAR"
        :return: None
        """
        if kind in ["STATIC", "FIELD"]:
            self.class_symbol_table[name] = [type, kind, self.var_count(kind)]
        else:
            self.subroutine_symbol_table[name] = [type, kind, self.var_count(kind)]

        self.kinds_var_counters_dict[kind] += 1

    def var_count(self, kind):
        """
        The number of variables with the same kind
        :param kind:  "STATIC", "FIELD", "ARG" or "VAR"
        :return: The number of variables
        """
        return self.kinds_var_counters_dict[kind]

    def kind_of(self, name):
        """
        :param name: A variable name
        :return: The kind of the variable
        """
        if name in self.class_symbol_table:
            return self.class_symbol_table[name][KIND_INDEX]
        elif name in self.subroutine_symbol_table:
            return self.subroutine_symbol_table[name][KIND_INDEX]
        else:
            return "NONE"

    def type_of(self, name):
        """
        :param name: The variable name
        :return: The type of the variable
        """
        if name in self.class_symbol_table:
            return self.class_symbol_table[name][TYPE_INDEX]
        else:
            return self.subroutine_symbol_table[name][TYPE_INDEX]

    def index_of(self, name):
        """
        :param name: The variable name
        :return: The index of the variable
        """
        if name in self.class_symbol_table:
            return self.class_symbol_table[name][RUNNING_INDEX]
        else:
            return self.subroutine_symbol_table[name][RUNNING_INDEX]
