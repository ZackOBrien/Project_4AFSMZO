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
class Command(object): #TODO check if this is right -we made this
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
    pass

# Statement Base Class (superclass of Assign, Terminate, and Import)
class Statement(Command):
    pass

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
            raise GroveParseError(f"Wrong number of tokens ({len(tokens)}) for StringLiteral")
        #1. ensure that all chars in that token are letters
        if not tokens[0].isalpha():
            raise GroveParseError("Nubers can contain only digits")
        return Number(int(tokens[0]))

class Object(Expression):
	# TODO: Implement node for "new" expression
    pass
    
class Call(Expression):
    # TODO: Implement node for "call" expression
    pass
        
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
        pass #TODO 
    

class Import(Expression):
    # TODO: Implement node for "import" statements
    pass

class Terminate(Expression):
	# TODO: Implement node for "quit" and "exit" statements
    print("Goodbye and thank you for using Grove!")
    sys.exit() 
