from grove_parse import *
from grove_lang import *

if __name__ == "__main__":
    # TODO: Implement your REPL here
    print("Welcome to the Grove REPL!")
    print("Enter your commands or ':done' to exit")
    while True:
        s: str = input('> ')
        if s.strip() == ':done': break
        try:
            x = Command.parse(s).eval()
            if x is not None: print(x)
        except GroveParseError as e:
            print(f"Error parsing {s}")
            print(e)
        except GroveEvalError as e:
            print(f"Error Evaluating {s}")
            print(e)
    print("Goodbye and thank you for using Grove!")