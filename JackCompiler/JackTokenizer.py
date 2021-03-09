

class JackTokenizer:
    """
    Tokenizer object for jack files
    """
    def __init__(self, file_name):
        """
        Constructor
        :param file_name: A file
        """
        self.tokens_list = []
        self.current_token = None
        self.current_token_index = -1
        self.keywords = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char",
                         "boolean", "void", "true", "false", "null", "this", "let", "do", "if", "else", "while",
                         "return"]
        self.symbols_list = ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=",
                             "~"]
        first_pass = removing_irrelevant_expressions(file_name)
        second_pass_list = second_pass(first_pass)
        for string in second_pass_list:
            tokens_list = self.analyze_string(string)
            self.tokens_list += tokens_list

    def analyze_string(self, string):
        """
        This function analyzes a string by parsing it by the symbol_list.
        The function reads every character and combines it with the next character until we get
        a string that's in the symbol_list. we do this until the end of the string
        :param string: A string
        :return: A list of strings.
        """
        current_string = ""
        tokens_list = []
        inverted_commas_counter = 0
        for char in string:
            if char in self.symbols_list and inverted_commas_counter % 2 == 0:
                if current_string != "":
                    tokens_list.append(current_string)
                tokens_list.append(char)
                current_string = ""
                continue
            elif char == '"':
                inverted_commas_counter += 1
                current_string += char
            else:
                current_string += char
        if current_string != "":
            tokens_list.append(current_string)

        return tokens_list

    def has_more_tokens(self):
        """
        :return: Boolean that check if we have more tokens
        """
        return self.current_token_index != (len(self.tokens_list) - 1)

    def advance(self):
        """
        This function advances to the token
        :return: None
        """
        if self.has_more_tokens():
            self.current_token_index += 1
            self.current_token = self.tokens_list[self.current_token_index]

    def token_type(self):
        """
        This function returns the type of the token
        :return: returns a string that represents the type
        of token.
        """
        if self.current_token in self.keywords:
            return "KEYWORD"
        elif self.current_token in self.symbols_list:
            return "SYMBOL"
        elif self.current_token.isdigit():
            return "INT_CONST"
        elif self.current_token[0] == '"' and self.current_token[-1] == '"':
            return "STRING_CONST"
        else:
            return "IDENTIFIER"

    def key_word(self):
        """
        :return: if the current token is a keyword returns it in a upper case
        format else returns None
        """
        if self.token_type() == "KEYWORD":
            return self.current_token.upper()

    def symbol(self):
        """
        :return: if the current token is a symbol returns it else returns None
        """
        if self.token_type() == "SYMBOL":
            return self.current_token

    def identifier(self):
        """
        :return: if the current token is a identifier returns it else returns None
        """
        if self.token_type() == "IDENTIFIER":
            return self.current_token

    def int_val(self):
        """
        :return: if the current token is an integer returns it as an int else returns None
        """
        if self.token_type() == "INT_CONST":
            return int(self.current_token)

    def string_val(self):
        """
        :return: if the current token is a string returns it as a string without the inverted commas else returns None
        """
        if self.token_type() == "STRING_CONST":
            return self.current_token[1:-1]


def second_pass(first_pass):
    """
    This function gets an array of strings and parses each string by white space or
    by inverted comma if the string has a inverted comma in it.
    :param first_pass: A list of strings
    :return: The list of strings
    """
    second_pass_list = []
    for line in first_pass:
        if '"' in line:
            current_string = ""
            inverted_commas_counter = 0
            for char in line:
                if char == '"':
                    inverted_commas_counter += 1
                if char != " " or inverted_commas_counter == 1:
                    current_string += char
                    continue
                if char == " " and inverted_commas_counter % 2 == 0:
                    second_pass_list.append(current_string)
                    current_string = ""
            second_pass_list.append(current_string)
        else:
            line = line.split()
            for part in line:
                second_pass_list.append(part)
    return second_pass_list


def removing_irrelevant_expressions(file_name):
    """
    This function reads a jack file and stores all the relevant lines(doesn't store any remarks or documentation)
    :param file_name: A string
    :return: A list of string
    """
    file = open(file_name, "r")
    is_documentation = False
    first_pass = []
    for line in file:
        line = line.lstrip()
        line = line.rstrip()
        inverted_commas_indexes = []
        last_backslash_index = -1
        for i in range(len(line)):
            if line[i] == '"':
                inverted_commas_indexes.append(i)
        for i in range(len(line) - 1):
            if (line[i] + line[i+1]) == "//":
                last_backslash_index = i

        if not inverted_commas_indexes:
              line = line.split("//")[0]

        elif (last_backslash_index != -1) and (inverted_commas_indexes[0] > last_backslash_index or
                                               last_backslash_index > inverted_commas_indexes[1]):
            line = line[:last_backslash_index]

        documentation_start = line.find("/*")
        documentation_end = line.find("*/")
        if documentation_start != -1 and documentation_end != -1:
            line = line[:documentation_start] + line[documentation_end+2:]
        if line == "":
            continue
        if line[:2] == "/*" and (line[len(line) - 2] + line[len(line) - 1]) == "*/":
            continue
        if line[:2] == "/*":
            is_documentation = True
            continue
        if (len(line) >= 2) and (line[len(line) - 2] + line[len(line) - 1]) == "*/":
            is_documentation = False
            continue
        if is_documentation:
            continue
        first_pass.append(line)
    file.close()
    return first_pass
