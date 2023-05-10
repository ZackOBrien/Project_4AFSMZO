from __future__ import annotations #we made this
## Parse tree nodes for the Calc language
import re
import sys
import importlib
import builtins
#imports we made
from abc import ABCMeta, abstractmethod
from typing import Any, Union
# The exception classes from the notes.
class GroveError(Exception): pass
class GroveParseError(GroveError): pass
class GroveEvalError(GroveError): pass

#TODO ask if we need these?
# create a context where variables stored with set are kept
context: dict[str, int] = {}
# add a "verbose" flag to print all parse exceptions while debugging
verbose = False
#

# Command Base Class (superclass of expressions and statements)
class Command(metaclass=ABCMeta): #TODO check if this is right -we made this
    @abstractmethod
    def __init__(self): pass
    @abstractmethod
    def eval(self) -> Union[int,None]: pass
    @staticmethod
    def parse(s: str) -> Command:
        """Factory method for creating Command subclasses from lines of code"""
        # the command should split the input into tokens based on whitespace
        tokens: list[str] = s.strip().split()
        # a command must be either a statement or an expression
        try:
            # first try to parse the command as a statement
            return Statement.parse(tokens)
        except GroveParseError as e:
            if verbose: print(e)
        try:
            # if it is not a statement, try an expression
            return Expression.parse(tokens)
        except GroveParseError as e:
            if verbose: print(e)
        raise GroveParseError(f"Unrecognized Command: {s}")

# Expression Base Class (superclass of Num, Name, StringLiteral, etc.)
class Expression(Command):
    @abstractmethod
    def __init__(self): pass
    @abstractmethod
    def eval(self) -> int: pass
    @classmethod
    def parse(cls, tokens: list[str]) -> Expression:
        """Factory method for creating Expression subclasses from tokens"""
        # get a list of all the subclasses of Expression
        subclasses: list[type[Expression]] = cls.__subclasses__()
        # try each subclass in turn to see if it matches the pattern
        for subclass in subclasses:
            try: 
                return subclass.parse(tokens)
            except GroveParseError as e:
                if verbose: print(e)
        # if none of the subclasses parsed successfully raise an exception
        raise GroveParseError(f"Unrecognized Expression: {' '.join(tokens)}")
    @staticmethod
    def match_parens(tokens: list[str]) -> int:
        """Searches tokens beginning with ( and returns index of matching )"""
        # ensure tokens is such that a matching ) might exist
        if len(tokens) < 2: raise GroveParseError("Expression too short")
        if tokens[0] != '(': raise GroveParseError("No opening ( found")
        # track the depth of nested ()
        depth: int = 0
        for i,token in enumerate(tokens):
            # when a ( is found, increase the depth
            if token == '(': depth += 1
            # when a ) is found, decrease the depth
            elif token == ')': depth -= 1
            # if after a token the depth reaches 0, return that index
            if depth == 0: return i
        # if the depth never again reached 0 then parens do not match
        raise GroveParseError("No closing ) found")

# Statement Base Class (superclass of Assign, Terminate, and Import)
class Statement(Command):
    @abstractmethod
    def __init__(self): pass
    @abstractmethod
    def eval(self) -> None: pass
    @staticmethod
    def parse(tokens: list[str]) -> Statement:
        """Factory method for creating Statement subclasses from tokens"""
        # the only valid statement in our language is set so try that
        stmt: Statement = Assignment.parse(tokens)
        return stmt

# -----------------------------------------------------------------------------
# Implement each of the following parse tree nodes for the Grove language
# -----------------------------------------------------------------------------

class Number(Expression): #TODO check if this is right -we made this
    def __init__(self, num: int):
        self.num = num
    def eval(self) -> int:
        return self.num
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Number) and other.num == self.num
    @staticmethod
    def parse(tokens: list[str]) -> Number:
        #0. ensure there is exactly one token
        if len(tokens) != 1:
            raise GroveParseError(f"Wrong number of tokens ({len(tokens)}) for Number")
        #1. ensure that all chars in that token are digits
        if not tokens[0].isdigit():
            raise GroveParseError("Nubers can contain only digits")
        if not tokens[0] == "-":
            raise GroveParseError("Nubers have to be positive")
        return Number(int(tokens[0]))

class StringLiteral(Expression): #TODO check if this is right -we made this
    def __init__(self, string_lit: str):
        self.value = string_lit
    def eval(self) -> str:
        return self.value
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, StringLiteral) and other.value == self.value
    def parse(tokens: list[str]) -> StringLiteral:
        #0. ensure there is exactly one token
        if len(tokens) != 1:
            raise GroveParseError(f"Wrong number of tokens ({len(tokens)}) for String")
        #1. ensure that the string does not contain any quotes
        if '"' in tokens[0][1:-1]:
            raise GroveParseError("String cannot contain quotes")
        #2. ensure that the string does not contain any whitespace
        if ' ' in tokens[0]:
            raise GroveParseError("String cannot contain whitespace")
        if tokens[0][0] != '"' or tokens[0][-1] != '"':
            raise GroveParseError("String must be wrapped in quotes")
        return StringLiteral(tokens[0])

class Object(Expression):
	# TODO: Implement node for "new" expression
    def __init__(self, obj: Expression):
        self.obj = obj
    def eval(self) -> Object:
        return self.obj
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Object) and other.obj == self.obj
    def parse(tokens: list[str]) -> Object:
        #0. ensure that the first token is "new"
        if tokens[0] != "new":
            raise GroveParseError("Object must begin with 'new'")
        #1. ensure that the second token is a Name
        try:
            name: Name = Name.parse([tokens[1]])
        except GroveParseError:
            raise GroveParseError("Object must have a Name after 'new'")
        #2. optionally check that every token after the second is a . followed by a Name
        for i in range(2, tokens.__len__):
            if tokens[i] != ".":
                raise GroveParseError("Object must have a '.' after the Name")
            # Check that all tokens have been consumed
            if len(tokens) != i + 1:
                raise GroveParseError("Unexpected tokens after object name")
            try:
                name: Name = Name.parse([tokens[i+1]])
            except GroveParseError:
                raise GroveParseError("Object must have a Name after the '.'")
        # return the object
        return Object(name)
    
class Call(Expression):
    def __init__(self, call: Expression):
        self.call = call #TODO SEAN CHECK IF THIS RIGHT, like do we need more variables?
    def eval(self) -> Call:
        return self.call
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Call) and other.call == self.call
    def parse(tokens: list[str]) -> Call:
        #A method call expression starts with the keyword call, followed by open parenthesis, a Name, another Name, zero or more Expressions (arguments), and closing parenthesis.
        #0. ensure that the first token is "call"
        if tokens[0] != "call":
            raise GroveParseError("Call must begin with 'call'")
        #1. ensure that the second token is "("
        if tokens[1] != "(":
            raise GroveParseError("Call must have '(' after 'call'")
        #2. ensure that the third token is a Name
        try:
            name1: Name = Name.parse([tokens[2]])
        except GroveParseError:
            raise GroveParseError("Call must have a Name after '('")
        #3. ensure that the fourth token is a Name
        try:
            name2: Name = Name.parse([tokens[3]])
        except GroveParseError:
            raise GroveParseError("Call must have a second Name after the first Name")
        # make sure the rest of the tokens until the last one are Expressions
        
        #4. ensure that the last token is ")"
        if tokens[tokens.__len__ - 1] != ")":
            raise GroveParseError("Call must end with ')'")
        #5. ensure that the tokens in between are Expressions
        #TODO
        
        
class Addition(Expression):
    def __init__(self, first: Expression, second: Expression):
        self.first = first
        self.second = second
    def eval(self) -> int:
        first_val = self.first.eval()
        second_val = self.second.eval()
        if isinstance(first_val, int) and isinstance(second_val, int):
            return first_val + second_val
        elif isinstance(first_val, str) and isinstance(second_val, str):
            return first_val + second_val
        else:
            raise GroveEvalError("Addition is only defined for two integers or two strings")
    def __eq__(self, other) -> bool:
        return (isinstance(other, Addition) and 
                other.first == self.first and 
                other.second == self.second)
    @staticmethod
    def parse(tokens: list[str]) -> Addition:
        """Factory method for creating Add expressions from tokens"""
        s = ' '.join(tokens)
        # check to see if this string matches the pattern for add
        # 0. ensure there are enough tokens for this to be a add expression
        if len(tokens) < 7:
            raise GroveParseError(f"Not enough tokens for Add in: {s}")
        # 1. ensure the first two tokens are + and (
        if tokens[0] != '+' or tokens[1] != '(':
            raise GroveParseError(f"Add must begin with '+ (' in {s}")
        # 2. ensure there is an expression inside that open parentheses
        try:
            cut = Expression.match_parens(tokens[1:])+1
            first: Expression = Expression.parse(tokens[2:cut])
        except GroveParseError:
            raise GroveParseError(f"Unable to parse first addend in: {s}")
        # 3. ensure there are enough tokens left after the first expression
        tokens = tokens[cut+1:]
        if len(tokens) < 3:
            raise GroveParseError(f"Not enough tokens left for Add in: {s}")
        # 4. ensure the first and last of the remaining tokens are ( and )
        if tokens[0] != '(' or tokens[-1] != ')':
            raise GroveParseError(f"Addends must be wrapped in ( ): {s}")
        # 5. ensure the tokens between these are a valid expression
        try:
            second: Expression = Expression.parse(tokens[1:-1])
        except GroveParseError:
            raise GroveParseError(f"Unable to parse second addend in: {s}")
        # if this point is reached, this is a valid Add expression
        return Addition(first, second)

class Name(Expression): #TODO check if this is right -we made this
    def __init__(self, name: str):
        self.name = name
    def eval(self) -> int:
        if self.name in context:
            return context[self.name]
        else:
            raise GroveEvalError(f"{self.name} is undefined")
    def __eq__(self, other: Any) -> bool:
        return (isinstance(other, Name) and other.name == self.name)
    @staticmethod
    def parse(tokens: list[str]) -> Name:
        # 0. ensure there is exactly one token
        if len(tokens) != 1:
            raise GroveParseError("Wrong number of tokens for name")
        # 1. ensure that the first character is alphabetic or underscore
        if not tokens[0][0].isalpha() or tokens[0][0] == '_':
            raise GroveParseError("Names must start with a letter or underscore")
        # 2. ensure that all characters are alphanumeric or underscore
        if not all(c.isalnum() or c == '_' for c in tokens[0]):
            raise GroveParseError("Names can contain only letters, digits, and underscores")
        return Name(tokens[0])


class Assignment(Expression):
    def __init__(self, name: Name, value: Expression):
        self.name = name
        self.value = value
    def eval(self) -> bool:
        context[self.name.name] = self.value.eval()
    def __eq__(self, other: Any):
        return (
            isinstance(other, Assignment)
            and self.name == other.name
            and self.value == other.value
        )
    @staticmethod
    def parse(tokens: list[str]) -> Assignment:
        """Factory method for creating Set commands from tokens"""
        # check to see if this string matches the pattern for set
        # 0. ensure there are enough tokens for this to be a set statement
        if len(tokens) < 4:
            raise GroveParseError("Statement too short for Set")
        # 1. ensure that the very first token is "set" otherwise throw Exception
        if tokens[0] != 'set': 
            raise GroveParseError("Set statements must begin with 'set'")
        # 2. ensure that the next token is a valid Name
        try:
            name: Name = Name.parse([tokens[1]])
        except GroveParseError:
            raise GroveParseError("No name found for Set statement")
        # 3. ensure that the next token is an '='
        if tokens[2] != '=':
            raise GroveParseError("Set statement requires '='")
        # 4. ensure the remaining tokens represent an expression
        try:
            value: Expression = Expression.parse(tokens[3:])
        except GroveParseError:
            raise GroveParseError("No value found for Set statement")
        # if this point is reached, this is a valid Set statement
        return Assignment(name, value)
    

class Import(Expression):
    # TODO: Implement node for "import" statements
    def __init__(self, name: Name):
        self.name = name
    def eval(self) -> None:
        try:
            importlib.import_module(self.name.name)
        except ModuleNotFoundError:
            raise GroveEvalError(f"Module {self.name.name} not found")
    def __eq__(self, other: Any):
        return (
            isinstance(other, Import)
            and self.name == other.name
        )
    @staticmethod
    def parse(tokens: list[str]) -> Import:
        #0. ensure that the first token is "new"
        if tokens[0] != "import":
            raise GroveParseError("Object must begin with 'import'")
        #1. ensure that the second token is a Name
        try:
            name: Name = Name.parse([tokens[1]])
        except GroveParseError:
            raise GroveParseError("Import must have a Name after 'import'")
        #2. optionally check that every token after the second is a . followed by a Name
        for i in range(2, tokens.__len__):
            if tokens[i] != ".":
                raise GroveParseError("Import must have a '.' after the Name")
            # Check that all tokens have been consumed
            if len(tokens) != i + 1:
                raise GroveParseError("Unexpected tokens after import name")
            try:
                name: Name = Name.parse([tokens[i+1]])
            except GroveParseError:
                raise GroveParseError("Import must have a Name after the '.'")
        # return the object
        return Import(name)

class Terminate(Expression):
    # TODO: Implement node for "quit" and "exit" statements
    def __init__(self, keyword: str):
        self.keyword = keyword
    def eval(self) -> None:
        sys.exit()
    def __eq__(self, other: Any):
        return (
            isinstance(other, Terminate)
            and self.keyword == other.keyword
        )
    @staticmethod
    def parse(tokens: list[str]) -> Terminate:
        #0. ensure that the first token is "quit" or "exit"
        if tokens[0] != "quit" and tokens[0] != "exit":
            raise GroveParseError("Terminate must begin with 'quit' or 'exit'")
        return Terminate(tokens[0])
