import JackTokenizer as JT
import VMWriter
import SymbolTable


class CompilationEngine:
    """
    Compilation Engine for jack files.
    Turns jack files into vm files
    """

    def __init__(self, input_file, output_filename):
        """
        Constructor
        :param input_file: A file
        :param output_file: A file
        """
        self.jack_tokenizer = JT.JackTokenizer(input_file)
        self.vm_writer = VMWriter.VMWriter(output_filename)
        self.class_name = ""
        self.subroutine_return_type = ""
        self.subroutine_call_arguments_num = 0
        self.labels_counter_if = 0
        self.labels_counter_while = 0
        self.symbol_table = SymbolTable.SymbolTable()
        self.compile_class()
        self.vm_writer.close()

    def compile_class(self):
        """
        This function compiles the complete class
        :return: None
        """
        # make current token not None
        self.jack_tokenizer.advance()

        # class
        self.jack_tokenizer.advance()

        # class Name
        self.class_name = self.get_current_token_and_advance()

        # {
        self.jack_tokenizer.advance()

        # classVarDec*
        while self.jack_tokenizer.current_token in ["static", "field"]:
            self.compile_class_var_dec()

        while self.jack_tokenizer.current_token in ["constructor", "function", "method"]:
            self.labels_counter_if = 0
            self.labels_counter_while = 0
            self.compile_subroutine()
        # }
        self.jack_tokenizer.advance()

    def compile_class_var_dec(self):
        """
        This function compiles a static of field declaration
        :return:
        """
        # static | field
        kind = self.get_current_token_and_advance()

        # type = int | char | boolean | className
        type_var = self.get_current_token_and_advance()

        # varName
        name = self.get_current_token_and_advance()

        # write into symbol table
        self.symbol_table.define(name, type_var, kind.upper())

        while self.jack_tokenizer.current_token == ",":
            # ,
            self.jack_tokenizer.advance()
            # varName
            name = self.get_current_token_and_advance()
            # write into symbol table
            self.symbol_table.define(name, type_var, kind.upper())

        # ;
        self.jack_tokenizer.advance()

    def compile_subroutine(self):
        """
        This function compiles the three different functions in a class
        method, function or constructor
        :return:
        """
        # initialize subroutine symbol table
        self.symbol_table.start_subroutine()

        # ('constructor' | 'function' | 'method')
        subroutine_keyword = self.get_current_token_and_advance()

        # ('void' | type)
        self.subroutine_return_type = self.get_current_token_and_advance()

        #  subroutineName
        subroutine_name = self.get_current_token_and_advance()

        # (
        self.jack_tokenizer.advance()

        # check if subroutine is method
        if subroutine_keyword == "method":
            self.symbol_table.define("this", self.class_name, "ARG")

        # ParameterList
        self.compile_parameter_list()

        # )
        self.jack_tokenizer.advance()

        # {
        self.jack_tokenizer.advance()

        while self.jack_tokenizer.current_token == "var":
            self.compile_var_dec()

        # write function
        self.vm_writer.write_function(self.class_name + "." + subroutine_name, self.symbol_table.var_count("VAR"))

        # if subroutine is constructor push the number of fields and calls Memory.alloc
        if subroutine_keyword == "constructor":
            # push number of fields
            self.vm_writer.write_push("CONST", self.symbol_table.var_count("FIELD"))

            # call Memory.alloc
            self.vm_writer.write_call("Memory.alloc", 1)

        # if subroutine is method initializes argument[0] = 'this'
        elif subroutine_keyword == "method":
            self.vm_writer.write_push("ARG", 0)

        # if subroutine is method or constructor initializes 'this' memory segment to current object
        if subroutine_keyword == "method" or subroutine_keyword == "constructor":
            self.vm_writer.write_pop("POINTER", 0)

        # statements
        self.compile_statements()

        # }
        self.jack_tokenizer.advance()

    def compile_parameter_list(self):
        """
        This function compiles a parameter list, not including the parenthesis
        :return:
        """
        if self.jack_tokenizer.current_token == ")":
            return

        # type = int | char | boolean | className
        parameter_type = self.get_current_token_and_advance()

        # varName
        parameter_name = self.get_current_token_and_advance()

        # add into subroutine symbol_table
        self.symbol_table.define(parameter_name, parameter_type, "ARG")

        while self.jack_tokenizer.current_token == ",":
            # ,
            self.jack_tokenizer.advance()

            # type = int | char | boolean | className
            parameter_type = self.get_current_token_and_advance()

            # varName
            parameter_name = self.get_current_token_and_advance()

            # add into subroutine symbol_table
            self.symbol_table.define(parameter_name, parameter_type, "ARG")

    def compile_var_dec(self):
        """
        This function compiles a var declaration
        :return:
        """
        # var
        self.jack_tokenizer.advance()

        # type = int | char | boolean | className
        variable_type = self.get_current_token_and_advance()

        # varName
        variable_name = self.get_current_token_and_advance()

        # add into symbol table
        self.symbol_table.define(variable_name, variable_type, "VAR")

        while self.jack_tokenizer.current_token == ",":
            # ,
            self.jack_tokenizer.advance()
            # varName
            variable_name = self.get_current_token_and_advance()

            # add into symbol table
            self.symbol_table.define(variable_name, variable_type, "VAR")
        # ;
        self.jack_tokenizer.advance()

    def compile_statements(self):
        """
        This function compiles a sequence of statements
        :return:
        """
        # letStatement | ifStatement | whileStatement | doStatement | returnStatement
        while self.jack_tokenizer.current_token in ["let", "if", "while", "do", "return"]:
            # letStatement
            if self.jack_tokenizer.current_token == "let":
                self.compile_let()

            # ifStatement
            elif self.jack_tokenizer.current_token == "if":
                self.compile_if()

            # whileStatement
            elif self.jack_tokenizer.current_token == "while":
                self.compile_while()

            # doStatement
            elif self.jack_tokenizer.current_token == "do":
                self.compile_do()

            # returnStatement
            elif self.jack_tokenizer.current_token == "return":
                self.compile_return()

    def compile_do(self):
        """
        This function compiles the do statement
        :return:
        """
        # do
        self.jack_tokenizer.advance()
        # subroutineName | className | varName
        first_name = self.get_current_token_and_advance()
        # subroutineCall
        self.handles_subroutine_call(first_name)

        # ;
        self.jack_tokenizer.advance()

        # pop temp 0 - removing dummy value from stack
        self.vm_writer.write_pop("TEMP", 0)

    def compile_let(self):
        """
        This function compiles the let statement
        :return:
        """
        is_array = False
        # let
        self.jack_tokenizer.advance()
        # varName
        var_name = self.get_current_token_and_advance()

        if self.jack_tokenizer.current_token == "[":
            is_array = True
            # [
            self.jack_tokenizer.advance()
            # expression
            self.compile_expression()
            # ]
            self.jack_tokenizer.advance()
            # push var_name
            self.push_variable(var_name)
            # add array address and expression
            self.vm_writer.write_arithmetic("ADD")
            #
        # =
        self.jack_tokenizer.advance()
        # expression
        self.compile_expression()
        # ;
        self.jack_tokenizer.advance()
        if is_array:
            # pop temp 0
            self.vm_writer.write_pop("TEMP", 0)
            # pop pointer 1
            self.vm_writer.write_pop("POINTER", 1)
            # push temp 0
            self.vm_writer.write_push("TEMP", 0)
            # push that 0
            self.vm_writer.write_pop("THAT", 0)
        # varName = expression
        else:
            variable_segment = self.symbol_table.kind_of(var_name)
            variable_index = self.symbol_table.index_of(var_name)
            if variable_segment == "STATIC":
                self.vm_writer.write_pop("STATIC", variable_index)
            elif variable_segment == "FIELD":
                self.vm_writer.write_pop("THIS", variable_index)
            elif variable_segment == "ARG":
                self.vm_writer.write_pop("ARG", variable_index)
            elif variable_segment == "VAR":
                self.vm_writer.write_pop("LOCAL", variable_index)

    def compile_while(self):
        """
        This function compiles the while statement
        :return:
        """
        # l1 and l2 labels
        l1_label = "WHILE_EXP" + str(self.labels_counter_while)
        l2_label = "WHILE_END" + str(self.labels_counter_while)
        self.labels_counter_while += 1

        # write label L1
        self.vm_writer.write_label(l1_label)

        # while
        self.jack_tokenizer.advance()
        # (
        self.jack_tokenizer.advance()
        # expression
        self.compile_expression()
        # )
        self.jack_tokenizer.advance()

        # negation
        self.vm_writer.write_arithmetic("NOT")

        # if-goto L2 label
        self.vm_writer.write_if(l2_label)
        # {
        self.jack_tokenizer.advance()
        # statements
        self.compile_statements()
        # }
        self.jack_tokenizer.advance()

        # goto L1 label
        self.vm_writer.write_goto(l1_label)

        # write label L2
        self.vm_writer.write_label(l2_label)

    def compile_return(self):
        """
        This function compiles the return statement
        :return:
        """

        # return
        self.jack_tokenizer.advance()
        # expression?
        if self.jack_tokenizer.current_token != ';':
            self.compile_expression()

        # insert dummy variable to stack in case of 'void' function
        if self.subroutine_return_type == "void":
            self.vm_writer.write_push("CONST", 0)
        # ;
        self.jack_tokenizer.advance()

        self.vm_writer.write_return()

    def compile_if(self):
        """
        This function compiles the if statement that may have an else clause.
        :return:
        """
        # if
        self.jack_tokenizer.advance()
        # (
        self.jack_tokenizer.advance()
        # expression
        self.compile_expression()
        # )
        self.jack_tokenizer.advance()
        # negation
        # self.vm_writer.write_arithmetic("NOT")

        # l1 and l2 labels
        l1_label = "IF_TRUE" + str(self.labels_counter_if)
        l2_label = "IF_FALSE" + str(self.labels_counter_if)
        end = "IF_END" + str(self.labels_counter_if)
        self.labels_counter_if += 1

        # if-goto L1
        self.vm_writer.write_if(l1_label)

        # goto l2 - False label
        self.vm_writer.write_goto(l2_label)

        # write True label
        self.vm_writer.write_label(l1_label)
        # {
        self.jack_tokenizer.advance()

        # statements
        self.compile_statements()

        # }
        self.jack_tokenizer.advance()

        # ( 'else' '{' statements '}' )?
        if self.jack_tokenizer.current_token == "else":
            # goto end
            self.vm_writer.write_goto(end)
            # write False label
            self.vm_writer.write_label(l2_label)
            # else
            self.jack_tokenizer.advance()
            # {
            self.jack_tokenizer.advance()
            # statements
            self.compile_statements()
            # }
            # write end label
            self.vm_writer.write_label(end)
            self.jack_tokenizer.advance()
        else:
            # write False label
            self.vm_writer.write_label(l2_label)

    def compile_expression(self):
        """
        This function compiles the an expression
        :return:
        """
        # term
        self.compile_term()
        op_list = ["+", "-", "*", "/", "&", "|", "<", ">", "="]

        expression_ops = []
        # expression_op = ''
        while self.jack_tokenizer.current_token in op_list:
            # op
            expression_ops.append(self.get_current_token_and_advance())
            # term
            self.compile_term()

        for op in reversed(expression_ops):

            if op == "+":
                self.vm_writer.write_arithmetic("ADD")

            elif op == "-":
                self.vm_writer.write_arithmetic("SUB")

            elif op == "*":
                self.vm_writer.write_call("Math.multiply", 2)

            elif op == "/":
                self.vm_writer.write_call("Math.divide", 2)

            elif op == "&":
                self.vm_writer.write_arithmetic("AND")

            elif op == "|":
                self.vm_writer.write_arithmetic("OR")

            elif op == "<":
                self.vm_writer.write_arithmetic("LT")

            elif op == ">":
                self.vm_writer.write_arithmetic("GT")

            elif op == "=":
                self.vm_writer.write_arithmetic("EQ")

    def compile_term(self):
        """
        This function compiles a term to vm
        :return:
        """
        # integerConstant
        if self.jack_tokenizer.token_type() == "INT_CONST":
            self.vm_writer.write_push("CONST", self.jack_tokenizer.int_val())
            # advance tokenizer
            self.jack_tokenizer.advance()

        # stringConstant
        elif self.jack_tokenizer.token_type() == "STRING_CONST":
            # push the length of string
            self.vm_writer.write_push("CONST", len(self.jack_tokenizer.string_val()))
            # call the String constructor
            self.vm_writer.write_call("String.new", 1)
            for char in self.jack_tokenizer.string_val():
                self.vm_writer.write_push("CONST", ord(char))
                self.vm_writer.write_call("String.appendChar", 2)
            # advance tokenizer
            self.jack_tokenizer.advance()

        # keywordConstant
        elif self.jack_tokenizer.token_type() == "KEYWORD":
            keyword_constant = self.jack_tokenizer.current_token
            if keyword_constant == "null" or keyword_constant == "false" or keyword_constant == "true":
                self.vm_writer.write_push("CONST", 0)
            if keyword_constant == "true":

                self.vm_writer.write_arithmetic("NOT")
            elif keyword_constant == "this":
                self.vm_writer.write_push("POINTER", 0)
            # advance tokenizer
            self.jack_tokenizer.advance()

        # varName | varName '[' expression ']' | subroutineCall
        elif self.jack_tokenizer.token_type() == "IDENTIFIER":

            # varName or className
            first_name = self.get_current_token_and_advance()

            # varName '[' expression ']'
            if self.jack_tokenizer.current_token == "[":
                # [
                self.jack_tokenizer.advance()
                # expression
                self.compile_expression()
                # push varName
                self.push_variable(first_name)
                # add array address and expression
                self.vm_writer.write_arithmetic("ADD")
                # pop pointer 1
                self.vm_writer.write_pop("POINTER", 1)
                # push that 0
                self.vm_writer.write_push("THAT", 0)
                # ]
                self.jack_tokenizer.advance()

            # subroutineCall
            elif self.jack_tokenizer.current_token == "." or self.jack_tokenizer.current_token == "(":
                self.handles_subroutine_call(first_name)

            # varName
            else:
                self.push_variable(first_name)

        #  '(' expression ')'
        elif self.jack_tokenizer.current_token == "(":
            # (
            self.jack_tokenizer.advance()
            # expression
            self.compile_expression()
            # )
            self.jack_tokenizer.advance()

        elif self.jack_tokenizer.current_token in ["-", "~"]:
            # unaryOP
            unary_operator = self.get_current_token_and_advance()
            # term
            self.compile_term()
            if unary_operator == '-':
                self.vm_writer.write_arithmetic("NEG")
            elif unary_operator == "~":
                self.vm_writer.write_arithmetic("NOT")

    def compile_expression_list(self):
        """
        This function compiles a list of expressions
        :return:
        """
        if self.jack_tokenizer.current_token == ")":
            return
        # expression
        self.compile_expression()
        self.subroutine_call_arguments_num += 1
        #  (',' expression)*
        while self.jack_tokenizer.current_token == ",":
            # ,
            self.jack_tokenizer.advance()

            temp_number_of_arguments = self.subroutine_call_arguments_num
            # expression
            self.compile_expression()
            self.subroutine_call_arguments_num = temp_number_of_arguments + 1

    def get_current_token_and_advance(self):
        """
        Returns the current token and advances the jack Tokenizer
        :return: The current token
        """
        temp = self.jack_tokenizer.current_token
        self.jack_tokenizer.advance()
        return temp

    def handles_subroutine_call(self, first_name):
        """
        This function is responsible writing function calls
        in vm according the jack code
        :param first_name: The name of the function
        :return: None
        """
        second_name = ""
        if self.jack_tokenizer.current_token == ".":
            # .
            self.jack_tokenizer.advance()
            # subroutineName
            second_name = self.get_current_token_and_advance()

        if second_name == "":
            self.vm_writer.write_push("POINTER", 0)
            self.subroutine_call_arguments_num += 1

        # calling an object method (first_name is not a class name, e.g. first_name is a variable name)
        elif self.symbol_table.kind_of(first_name) != "NONE":
            # push the current object address
            self.push_variable(first_name)
            first_name = self.symbol_table.type_of(first_name)
            self.subroutine_call_arguments_num += 1
        # (
        self.jack_tokenizer.advance()
        # expressionList
        self.compile_expression_list()
        # )
        self.jack_tokenizer.advance()

        # subroutine call
        if second_name == "":
            self.vm_writer.write_call(self.class_name + "." + first_name, self.subroutine_call_arguments_num)
        else:

            self.vm_writer.write_call(first_name + "." + second_name, self.subroutine_call_arguments_num)
        self.subroutine_call_arguments_num = 0

    def push_variable(self, first_name):
        """
        The function pushes a variable to the stack
        :param first_name: The name of the variable
        :return: None
        """
        variable_segment = self.symbol_table.kind_of(first_name)
        variable_index = self.symbol_table.index_of(first_name)
        if variable_segment == "STATIC":
            self.vm_writer.write_push("STATIC", variable_index)
        elif variable_segment == "FIELD":
            self.vm_writer.write_push("THIS", variable_index)
        elif variable_segment == "ARG":
            self.vm_writer.write_push("ARG", variable_index)
        elif variable_segment == "VAR":
            self.vm_writer.write_push("LOCAL", variable_index)
