from typing import List, Tuple, Union
from expression import Expression
import expression as expr
import re

class ParseFailed(Exception):
    """ Parsing a string failed"""
    def __init__(self, msg):
        super().__init__(msg)

class SyntaxError(Exception):
    """ String has bad syntax """
    def __init__(self, msg):
        super().__init__(msg)

_token_res = {
    "left_paren":  r"\(",                   # Parenthesis
    "right_paren": r"\)",
    "comma":       r",",                    # Commas
    "name":        r"[a-zA-Z][a-zA-Z0-9]*", # Character strings
    "number":      r"[+-]?(\d+([.]\d*)?([eE][+-]?\d+)?|[.]\d+([eE][+-]?\d+)?)", # Numbers
    "wildcard":    r"#[0-9]*",              # Wildcards
    "op":          r"(\+|-|\*|/|\^)"        # Infix/postfix operators (note: lower priority than numbers, which might start with +/-)
}

unary_functions = {
    "exp": expr.Exp,
    "log": expr.Log,
    "abs": expr.Abs,
    "sign": expr.Sign,
}

def _tokenise(string: str) -> List[Tuple[str, str]]:
    """ Split string into meaningful tokens"""
    tokens = []
    while True:

        match_success = False

        m = re.match(r"^\s+", string) # Match whitespace but don't include it

        if m is None:

            for key in _token_res:
                m = re.match(r"^" + _token_res[key], string)
                if m is not None:
                    tokens.append((m[0], key))
                    string = string[m.end(0):]
                    match_success = True
                    continue

        else:
            string = string[m.end(0):]
            match_success = True

        if not match_success:
            if len(string) > 0:
                raise ParseFailed(f"Could not find valid token starting at '{string}'")
            else:
                return tokens



def parse_expression(string: str) -> Expression:
    tokens = _tokenise(string)
    _parse_tokens(tokens)

def _parse_tokens(tokens: List[Union[Tuple[str, str], Expression, Tuple[Expression, Expression]]]) -> Expression:

    while True:

        print([t[0] for t in tokens])

        # step one: find first innermost parentheses

        start = 0
        end = None
        count = 0
        for i, token in enumerate(tokens):
            if isinstance(token, tuple):
                if token[1] == "left_paren":
                    start = i
                    count += 1
                elif token[1] == "right_paren":
                    if count <= 0:
                        raise SyntaxError("Unmatched parenthesis")
                    end = i
                    break

        if end is not None:
            # We got one!

            left = tokens[:start]
            middle = tokens[start+1:end]
            right = tokens[end+1:]
            # print(left, middle, right)

            # Now, is the parenthesis part of a function call
            function_call = False
            if len(left) > 0:
                # check token type
                if left[-1][1] == "name":
                    # check for keyword
                    # TODO: Add support for binary+ functions

                    if left[-1][0] in unary_functions:


            [_parse_tokens(middle)]

        else:
            # No brackets at all
            pass

        break

def tokeniser_proto_test():
    # TODO: Make these into proper tests
    whitespace_test_string = " a \t b\nc\td e fgh "
    other_string = "not starting with whitespace"
    some_algebra = "a + (b-#1)^(a^2)"
    print(_tokenise(whitespace_test_string))
    print(_tokenise(other_string))
    print(_tokenise(some_algebra))


def main():
    some_algebra = "a + (b-#1)^(a^2)"
    parse_expression(some_algebra)


if __name__ == "__main__":
    main()