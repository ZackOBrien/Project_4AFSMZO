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
        if not tokens[0] == "-":
            raise GroveParseError("Nubers have to be positive")
        return Number(int(tokens[0]))

class Object(Expression):
	# TODO: Implement node for "new" expression
    pass
    
class Call(Expression):
    # TODO: Implement node for "call" expression
    pass
        
class Addition(Expression):
    # TODO: Implement node for "+"
    pass

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
	# TODO: Implement node for "set" statements
	pass

class Import(Expression):
    # TODO: Implement node for "import" statements
    pass

class Terminate(Expression):
	# TODO: Implement node for "quit" and "exit" statements
	pass
