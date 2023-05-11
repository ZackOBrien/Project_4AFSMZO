#Question: Is your Grove interpreter using a static or dynamic type system? Briefly explain what aspects of the interpreter make it so.
# Our Grove interpreter uses a dynamic type system.
# Becuase for example we never say the variable type when we use "set", the intrepreter decides by the value we give it whether it is a String or Int
from grove_parse import *
from grove_lang import *

if __name__ == "__main__":
    # TODO: Implement your REPL here
    # print("Welcome to the Grove REPL!")
    # print("Enter your commands or ':done' to exit")
    while True:
        # s: str = input('Grove >> ')
        s: str = input('')
        if s.strip() == 'quit' or s.strip() == 'exit': Terminate.parse(['quit']).eval()
        try:
            x = Command.parse(s).eval()
            if x is not None: print(x)
        except GroveParseError as e:
            print(f"Error parsing {s}")
            print(e)
        except GroveEvalError as e:
            print(f"Error Evaluating {s}")
            print(e)