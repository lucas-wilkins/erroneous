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
    # "comma":       r",",                    # Commas - required for binary functions
    "name":        r"[a-zA-Z][a-zA-Z0-9]*", # Character strings
    "number":      r"[+-]?(\d+([.]\d*)?([eE][+-]?\d+)?|[.]\d+([eE][+-]?\d+)?)", # Numbers
    "wildcard":    r"#[0-9]*",              # Wildcards
    "op":          r"(\+|-|\*|/|\^|%)"        # Infix/postfix operators (note: lower priority than numbers, which might start with +/-)
}

unary_functions = {
    "exp": expr.Exp,
    "log": expr.Log,
    "abs": expr.Abs,
    "sign": expr.Sign,
    "cos": expr.Cos,
    "sin": expr.Sin,
    "sqrt": lambda x: expr.Power(x, expr.Constant(0.5))
}

# infix operators in order of precedence
infix_operators_pre_unary_minus = [
    ("^", expr.Power),
    ("/", expr.Divide),
    ("%", expr.Modulo),
    ("*", expr.Times)
]

infix_operators_post_unary_minus = [
    ("-", expr.Minus),
    ("+", expr.Plus)
]

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

def _parse_constant(string: str) -> expr.Constant:
    try:
        num = int(string)
        return expr.Constant(num)
    except ValueError:
        try:
            num = float(string)
            return expr.Constant(num)
        except ValueError:
            raise ParseFailed(f"Could not parse constant value '{string}'")

def _parse_wildcard(string: str) -> expr.Wildcard:

    if len(string) == 1:
        return expr.Wildcard(-1)

    else:
        try:
            num = int(string[1:])
            return expr.Wildcard(num)

        except ValueError:
            raise ParseFailed(f"Could not parse wildcard token '{string}'")


def parse_expression(string: str) -> Expression:
    tokens = _tokenise(string)

    # check left and right parentheses match
    count = 0
    for token in tokens:
        if token[1] == "left_paren":
            count += 1
        elif token[1] == "right_paren":
            count -= 1
            if count < 0:
                raise SyntaxError("Unmatched parenthesis")

    if count != 0:
        raise SyntaxError("Unmatched parenthesis")

    return _parse_tokens(tokens)


def _parse_tokens(tokens: List[Union[Tuple[str, str], Expression, Tuple[Expression, Expression]]]) -> Expression:

    if len(tokens) == 0:
        raise SyntaxError("Empty expression")

    while True:

        # Useful debugging statement
        # print([t[0] if isinstance(t, tuple) else t for t in tokens])

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

            # Now, is the parenthesis part of a function call?
            function_call = False
            if len(left) > 0:
                # check token type
                if left[-1][1] == "name":
                    # check for keyword
                    # TODO: Add support for binary+ functions

                    if left[-1][0] in unary_functions:
                        ex = unary_functions[left[-1][0]]

                        new_middle = ex(_parse_tokens(middle))

                        tokens = left[:-1] + [new_middle] + right

                    else:
                        raise ParseFailed(f"Unknown function: '{left[-1][0]}'")

                else:
                    new_middle = _parse_tokens(middle)
                    tokens = left + [new_middle] + right
            else:
                new_middle = _parse_tokens(middle)
                tokens = left + [new_middle] + right

        else:
            # The pattern should be: (neg*) symbol infix (neg*) symbol infix (neg*) symbol ...
            # First thing to do has to be to convert symbols to expression objects

            new_tokens = []
            for token in tokens:
                if isinstance(token, tuple):
                    if token[1] == "name":
                        new_tokens.append(expr.Variable(token[0]))
                    elif token[1] == "number":
                        new_tokens.append(_parse_constant(token[0]))
                    elif token[1] == "wildcard":
                        new_tokens.append(_parse_wildcard(token[0]))
                    elif token[1] == "op":
                        new_tokens.append(token[0])
                    else:
                        raise ParseFailed(f"Unknown or misplaced token type '{token[1]}'")

                elif isinstance(token, Expression):
                    new_tokens.append(token)

                else:
                    raise RuntimeError(f"Token string contains element that is not an Expression or tuple: {token}")

            tokens = new_tokens

            # Next we apply all the of the operators that have a higher precedence than -

            for op_string, op_cls in infix_operators_pre_unary_minus:

                while True:

                    for token_index, token in enumerate(tokens):
                        if token == op_string:
                            break
                    else:
                        break

                    left = tokens[:token_index - 1]
                    a = tokens[token_index - 1]
                    b = tokens[token_index + 1]
                    right = tokens[token_index + 2:]

                    if not isinstance(a, Expression):
                        raise SyntaxError(f"Cannot apply {op_string} to {a}")

                    if not isinstance(b, Expression):
                        raise SyntaxError(f"Cannot apply {op_string} to {b}")

                    tokens = left + [op_cls(a, b)] + right

                    # print("Reduced:", tokens)

            # Now to deal with the prefix operators

            # group tokens into parts ending in an symbol,
            # which should now be represented as an expression

            sections = []
            this_section = []
            for token in tokens:
                this_section.append(token)
                if isinstance(token, Expression):
                    sections.append(this_section)
                    this_section = []

            if len(this_section) > 0:
                raise SyntaxError("(sub)expression terminates with operator: ")

            # Now the rightmost value in section should be a symbol
            #  and the leftmost value in all sections but the first should be an op

            # There should be at least one section, because we have checked for tokens
            # Check the first section is of the form (neg*) symbol, we know it must end in
            # a symbol because of the previous operation, just check everything before it is -
            prefix_applied = sections[0][-1]
            for token in sections[0][:-1]:
                if token == "-":
                    prefix_applied = expr.Neg(prefix_applied)
                else:
                    err_string = ' '.join([str(token) for token in tokens])
                    raise SyntaxError(f"invalid prefix operator '{token}' in {err_string}")

            new_tokens = [prefix_applied]

            for section in sections[1:]:
                new_tokens.append(section[0])
                prefix_applied = section[-1]
                for token in section[1:-1]:
                    if token == "-":
                        prefix_applied = expr.Neg(prefix_applied)
                    else:
                        err_string = ' '.join([str(token) for token in tokens])
                        raise SyntaxError(f"invalid prefix operator '{token}' in {err_string}")

                new_tokens.append(prefix_applied)

            tokens = new_tokens

            # tokens should now be of the form: symbol op symbol op ... op symbol
            # go through each type of operator and apply it until there is none left
            for op_string, op_cls in infix_operators_post_unary_minus:

                while True:

                    for token_index, token in enumerate(tokens):
                        if token == op_string:
                            break
                    else:
                        break

                    left = tokens[:token_index-1]
                    a = tokens[token_index-1]
                    b = tokens[token_index+1]
                    right = tokens[token_index+2:]

                    tokens = left + [op_cls(a, b)] + right


                    # print("Reduced:", tokens)

        # print("Before break test", tokens)
        if len(tokens) == 1:
            break


    return tokens[0]


def tokeniser_proto_test():
    # TODO: Make these into proper tests
    whitespace_test_string = " a \t b\nc\td e fgh "
    other_string = "not starting with whitespace"
    some_algebra = "-a + (b-#1)^(a^2)"
    print(_tokenise(whitespace_test_string))
    print(_tokenise(other_string))
    print(_tokenise(some_algebra))


def parser_proto_test():

    some_algebra = "-a + --(b-#1)^(a^2)"
    print(some_algebra)
    parse_expression(some_algebra).short_print()

    more_algebra = "sqrt(----a^2 + b^2)"
    print(more_algebra)
    parse_expression(more_algebra).short_print()
    parse_expression(more_algebra).simplify().short_print()


def main():
    # tokeniser_proto_test()
    # parser_proto_test()
    from expression import Variable
    parse_expression("sin(x)").diff(Variable('x'), True).pretty_print()

if __name__ == "__main__":
    main()