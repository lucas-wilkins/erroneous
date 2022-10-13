from typing import Optional, Dict

from expression import Expression, Wildcard, Constant, Variable

class MatchFailure(Exception):
    """ Exception used to signal that a pattern does not match"""
    def __init__(self, pattern, expression):
        self.msg = f"{pattern} does not match {expression}"
        super().__init__(self.msg)


def match(pattern: Expression, expression: Expression) -> Optional[Dict[int, Expression]]:
    # Check that `expression` does not contain wildcards


    try:
        match_data = _match(pattern, expression)

        # If there are multiple uses of a wildcard, check their contents is the same

        
    except MatchFailure:
        return None


def _match(pattern: Expression, expression: Expression) -> Optional[Dict[int, Expression]]:

    """
    Recursively defined, matching failure indicated via an exception being raised
    """

    # Wildcard should match anything
    if isinstance(pattern, Wildcard):
        return {pattern.number: expression}

    # Need to check all the other special expression types (Constant, Variable) differently from the rest,
    # because their .terms field does not contain expressions
    elif isinstance(pattern, Constant):

        if not isinstance(expression, Constant):
            raise MatchFailure(pattern, expression)

        if pattern.value != expression.value:
            raise MatchFailure(pattern, expression)

        # Otherwise, nothing else to do here

    elif isinstance(pattern, Variable):
        if not isinstance(expression, Variable):
            raise MatchFailure(pattern, expression)

        if pattern.identity != expression.identity:
            raise MatchFailure(pattern, expression)

        # Otherwise, nothing else to do here

    # All the other expression types
    else:
        if pattern.head != expression.head:
            raise MatchFailure(pattern, expression)

        if len(pattern.terms) != len(expression.terms):
            raise MatchFailure(pattern, expression)

        # Recursively check internals
        output_dict: Dict[int, Expression] = {}
        for p, e in zip(pattern.terms, expression.terms):
            output_dict.update(_match(p, e)) # TODO: But what if we have multiple uses of the same wildcard???

        return output_dict


def matches(pattern: Expression, expression: Expression) -> bool:
    return match(pattern, expression) is not None