from __future__ import annotations

from typing import Dict, Any, Optional, Callable, List, Set

from fractions import Fraction
from collections import defaultdict

import numpy as np

import logging

logger = logging.getLogger("expressions")


class NonDifferentiableExpressionError(Exception):
    def __init__(self, msg):
        super.__init__(msg)

class EvaluationError(Exception):
    """ A problem with evaluating an expression"""
    def __init__(self, msg):
        super().__init__(msg)

class SubstitutionError(Exception):
    """ A problem with the substitution procedure"""
    def __init__(self, msg):
        super().__init__(msg)

class MatchFailure(Exception):
    """ Exception used to signal that a pattern does not match"""
    def __init__(self, pattern, expression):
        self.msg = f"{pattern} does not match {expression}"
        super().__init__(self.msg)


class MatchError(Exception):
    """ Something went wrong trying to match expressions """
    def __init__(self, msg):
        super().__init__(msg)


class Expression:

    # Generally useful things for navigating an expression

    @property
    def head(self) -> str:
        return self.__class__.__name__

    @property
    def terms(self) -> List[Expression]:
        raise NotImplementedError(f"terms not implemented in {self.__class__.__name__}")

    # Don't have a full-blown substitution system right now
    def wildcard_substitute(self, wildcard_id: int, expression: Expression):
        raise NotImplementedError(f"wildcard_substitute not implemented in {self.__class__.__name__}")

    @property
    def wildcard_numbers(self) -> Set[int]:
        out = set()
        for term in self.terms:
            out.update(term.wildcard_numbers)
        return out

    def replace(self, source_pattern: Expression, target_pattern: Expression) -> Expression:
        return self.substitute(source_pattern, target_pattern).simplify()

    def substitute(self, source_pattern: Expression, target_pattern: Expression) -> Expression:
        # Check that the other doesn't contain wildcards not in the original
        bad_wildcards = target_pattern.wildcard_numbers.difference(source_pattern.wildcard_numbers)
        if len(bad_wildcards) > 0:
            raise SubstitutionError(f"Target expression contains wildcards not in source expression ({bad_wildcards})")

        # print(f"Attempting substution in {self.short_string()}:", end="")
        # print(f"  {source_pattern.short_string()} -> {target_pattern.short_string()}")

        return self._substitute(source_pattern, target_pattern)

    def _substitute(self, source_pattern: Expression, target_pattern: Expression) -> Expression:
        raise NotImplementedError(f"{self.__class__.__name__} does not implement _substitute")

    def simplify(self, max_iters=100) -> Expression:
        last_expression = self
        new_expression = self
        for i in range(max_iters):

            for source, target in simplification_substitutions:
                new_expression = new_expression.substitute(source, target)

            if new_expression.full_identity(last_expression):
                last_expression = new_expression
                break

            last_expression = new_expression

        else:
            logger.warning(f"Reached max_iters (={max_iters}) in simplification.")

        return last_expression

    def match(self, expression: Expression) -> Optional[Dict[int, Expression]]:
        # Check that `expression` does not contain wildcards

        if len(expression.wildcard_numbers) != 0:
            raise MatchError("Wildcard in target expression")

        try:
            match_data = self._match(expression)

            # If there are multiple uses of a wildcard, check their contents is the same
            output_dict: Dict[int, Expression] = {}
            for key in match_data:
                if len(match_data[key]) > 1:
                    ref = match_data[key][0]
                    for other in match_data[key][1:]:
                        ref.match(other)  # Should raise a MatchFailed exception if it doesn't work

                output_dict[key] = match_data[key][0]
            return output_dict

        except MatchFailure:
            return None

    def _match(self, expression: Expression) -> Dict[int, List[Expression]]:

        """
        Recursively defined, matching failure indicated via an exception being raised

        Overriden by special objects - Constant, Variable, Wildcard

        """

        if self.head != expression.head:  # Checks class name, not class object - probably good for serialisation
            raise MatchFailure(self, expression)

        # Recursively check internals
        output_dict: Dict[int, List[Expression]] = defaultdict(list)
        for p, e in zip(self.terms, expression.terms):
            match_data = p._match(e)
            for key in match_data:
                output_dict[key] += match_data[key]

        return output_dict

    def matches(self, pattern: Expression) -> bool:
        return self.match(pattern) is not None

    # Calculus

    def diff(self, term: Variable) -> Expression:
        return self.fast_diff(term).simplify()

    def fast_diff(self, term: Variable) -> Expression:
        if self.differentiable:
            return self._diff(term)
        else:
            raise NonDifferentiableExpressionError(
                f"Cannot differentiate Expression object of type {self.__class__.__name__}")

    def _diff(self, term: Variable) -> Expression:
        """Differentiate this expression with respect to a variable"""

        raise NotImplementedError(f"diff not implemented in {self.__class__.__name__}")

    @property
    def differentiable(self):
        return True


    # Evaluation

    def __call__(self, variable_map: Dict[Variable, Any]):
        raise NotImplementedError(f"__call__ not implemented in {self.__class__.__name__}")

    # Algabraic methods

    @staticmethod
    def _sanitise(value: Any, operation_name: Optional[str]=None) -> Expression:
        """ Takes inputs that might be numbers, expressions, or something else,
        and return an Expression"""

        if isinstance(value, (int, float, Fraction, np.ndarray)):
            return Constant(value)
        elif isinstance(value, Expression):
            return value
        else:
            if operation_name is not None:
                raise TypeError(f"Invalid input to operation '{operation_name}': {repr(value)}")
            else:
                raise TypeError(f"Invalid input to Expression object: {repr(value)}")

    def __add__(self, other):
        other = Expression._sanitise(other, "+")
        return Plus(self, other)

    def __radd__(self, other):
        other = Expression._sanitise(other, "+")
        return Plus(other, self)

    def __sub__(self, other):
        other = Expression._sanitise(other, "-")
        return Minus(self, other)

    def __rsub__(self, other):
        other = Expression._sanitise(other, "-")
        return Minus(other, self)

    def __neg__(self):
        return Neg(self)

    def __mul__(self, other):
        other = Expression._sanitise(other, "*")
        return Times(self, other)

    def __rmul__(self, other):
        other = Expression._sanitise(other, "*")
        return Times(other, self)

    def __truediv__(self, other):
        other = Expression._sanitise(other, "/")
        return Divide(self, other)

    def __rdiv__(self, other):
        other = Expression._sanitise(other, "/")
        return Divide(other, self)

    def __mod__(self, other):
        other = Expression._sanitise(other, "%")
        return Modulo(self, other)

    def __rmod__(self, other):
        other = Expression._sanitise(other, "%")
        return Modulo(other, self)

    def __pow__(self, other):
        other = Expression._sanitise(other, "**")
        return Power(self, other)

    def __rpow__(self, other):
        other = Expression._sanitise(other, "**")
        return Power(other, self)

    @property
    def exp(self):
        return Exp(self)

    @property
    def log(self):
        return Log(self)

    def __abs__(self):
        return Abs(self)

    @property
    def sign(self):
        return Sign(self)

    #
    # Comparisons
    #

    def full_identity(self, other: Expression) -> bool:
        raise NotImplementedError(f"{self.__class__.__name__} does not implement full_identity")

    #
    # Strings
    #

    def pretty_print(self, indent_str: str = "  ", file=None):
        print(self.pretty_print_string(indent_str), file=file)

    def pretty_print_string(self, indent_str: str = "  "):
        return "\n".join(self._pretty_print_lines(indent_str))

    def _pretty_print_lines(self, indent_str: str) -> List[str]:
        raise NotImplementedError(f"`pretty_print` not implemented in {self.__class__.__name__}")

    def short_string(self):
        return repr(self)

    def short_print(self, file=None):
        print(self.short_string(), file=file)


#
# Helper classes
#


class Unary(Expression):
    """ Base class for unary expression components"""
    def __init__(self, a: Any):
        self.a = Expression._sanitise(a)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.a})"

    @property
    def terms(self) -> List[Expression]:
        return [self.a]

    def wildcard_substitute(self, wildcard_id: int, expression: Expression):
        return self.__class__(self.a.wildcard_substitute(wildcard_id, expression))

    def _pretty_print_lines(self, indent_str) -> List[str]:
        a_lines = self.a._pretty_print_lines(indent_str)
        a_lines = [indent_str + line for line in a_lines]
        a_lines[-1] += ")"
        return [f"{self.__class__.__name__}("] + a_lines


    def _substitute(self, source_pattern: Expression, target_pattern: Expression) -> Expression:

        new_a = self.a._substitute(source_pattern, target_pattern)

        new_self = self.__class__(new_a)

        match_data = source_pattern.match(new_self)

        if match_data is not None:
            replacement = target_pattern
            for key in match_data:
                replacement = replacement.wildcard_substitute(key, match_data[key])

            return replacement

        else:
            return new_self

    def full_identity(self, other: Expression) -> bool:
        return self.head == other.head and self.a.full_identity(other.a)

class Binary(Expression):
    """ Base class for binary expression components"""
    def __init__(self, a: Any, b: Any):
        self.a = Expression._sanitise(a)
        self.b = Expression._sanitise(b)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.a}, {self.b})"

    @property
    def terms(self) -> List[Expression]:
        return [self.a, self.b]

    def wildcard_substitute(self, wildcard_id: int, expression: Expression):
        return self.__class__(
            self.a.wildcard_substitute(wildcard_id, expression),
            self.b.wildcard_substitute(wildcard_id, expression))

    def _pretty_print_lines(self, indent_str) -> List[str]:
        a_lines = self.a._pretty_print_lines(indent_str)
        a_lines = [indent_str + line for line in a_lines]
        a_lines[-1] += ","
        b_lines = self.b._pretty_print_lines(indent_str)
        b_lines = [indent_str + line for line in b_lines]
        b_lines[-1] += ")"

        return [f"{self.__class__.__name__}("] + a_lines + b_lines

    def _substitute(self, source_pattern: Expression, target_pattern: Expression) -> Expression:

        new_a = self.a._substitute(source_pattern, target_pattern)
        new_b = self.b._substitute(source_pattern, target_pattern)

        new_self = self.__class__(new_a, new_b)

        match_data = source_pattern.match(new_self)

        if match_data is not None:
            replacement = target_pattern
            for key in match_data:
                replacement = replacement.wildcard_substitute(key, match_data[key])

            return replacement

        else:
            return new_self


    def full_identity(self, other: Expression) -> bool:
        return self.head == other.head and self.a.full_identity(other.a) and self.b.full_identity(other.b)

#
# Special Expressions
#


class Constant(Expression):
    """ Represents a constant"""
    def __init__(self, value: Any):
        # This should NOT be a subtype of Unary, because it is the result of
        # Expression._sanitise when given a number
        self.value = value

    def __repr__(self):
        return repr(self.value)

    @property
    def terms(self) -> List[Expression]:
        return []

    def wildcard_substitute(self, wildcard_id: int, expression: Expression):
        return self

    def _match(self, expression: Expression) -> Dict[int, List[Expression]]:
        if not isinstance(expression, Constant):
            raise MatchFailure(self, expression)

        if self.value != expression.value:
            raise MatchFailure(self, expression)

        return {}

    def _pretty_print_lines(self, indent_str: str) -> List[str]:
        return [str(self.value)]

    def _diff(self, term):
        return Constant(0)

    def __call__(self, x):
        return self.value

    def _substitute(self, source_pattern: Expression, target_pattern: Expression) -> Expression:

        match_data = source_pattern.match(self)

        if match_data is not None:
            replacement = target_pattern
            for key in match_data:
                replacement = replacement.wildcard_substitute(key, match_data[key])

            return replacement

        else:
            return self

    def full_identity(self, other: Expression) -> bool:
        return other.head == self.head and self.value == other.value


class Variable(Expression):
    def __init__(self, identity, print_alias: Optional[str]=None):
        self.identity = identity
        if print_alias is None:
            self.print_alias = str(self.identity)
        else:
            self.print_alias = print_alias

    def __repr__(self):
        return self.print_alias

    @property
    def terms(self) -> List[Expression]:
        return []

    def wildcard_substitute(self, wildcard_id: int, expression: Expression):
        return self

    def _match(self, expression: Expression) -> Dict[int, List[Expression]]:

        if not isinstance(expression, Variable):
            raise MatchFailure(self, expression)

        if self.identity != expression.identity:
            raise MatchFailure(self, expression)

        return {}

    def _pretty_print_lines(self, indent_str: str) -> List[str]:
        return [self.print_alias]

    def _diff(self, term: Variable):
        if term.identity == self.identity:
            return Constant(1)
        else:
            return Constant(0)

    def __call__(self, x):
        return x[self.identity]

    def _substitute(self, source_pattern: Expression, target_pattern: Expression) -> Expression:

        match_data = source_pattern.match(self)

        if match_data is not None:
            replacement = target_pattern
            for key in match_data:
                replacement = replacement.wildcard_substitute(key, match_data[key])

            return replacement

        else:
            return self

    def full_identity(self, other: Expression) -> bool:
        return self.head == other.head and self.identity == other.identity



class Wildcard(Expression):
    def __init__(self, number):
        self.number = number

    @property
    def differentiable(self):
        return False

    def __repr__(self):
        return f"#{self.number}"

    @property
    def terms(self) -> List[Expression]:
        return []

    def wildcard_substitute(self, wildcard_id: int, expression: Expression):
        if self.number == wildcard_id:
            return expression
        else:
            return self

    @property
    def wildcard_numbers(self) -> Set[int]:
        return {self.number}

    def _match(self, expression: Expression):
        return {self.number: [expression]}

    def _pretty_print_lines(self, indent_str: str) -> List[str]:
        return [f"<{self.number}>"]

    def __call__(self, x):
        raise EvaluationError("Wildcards cannot be evaluated")

    def _substitute(self, source_pattern: Expression, target_pattern: Expression) -> Expression:
        raise SubstitutionError("Attempted to substitute into expression with a wildcard")

    def full_identity(self, other: Expression) -> bool:
        return self.head == other.head and self.number == other.number

#
# Standard algabraic operations
#

class Plus(Binary):
    def __init__(self, a: Expression, b: Expression):
        super().__init__(a, b)

    def _diff(self, term: Variable):
        return Plus(self.a._diff(term), self.b._diff(term))

    def __call__(self, x):
        return self.a(x) + self.b(x)

    def short_string(self):
        return f"({self.a.short_string()} + {self.b.short_string()})"


class Minus(Binary):
    def __init__(self, a: Expression, b: Expression):
        super().__init__(a, b)

    def _diff(self, term: Variable):
        return Minus(self.a._diff(term), self.b._diff(term))

    def __call__(self, x):
        return self.a(x) - self.b(x)

    def short_string(self):
        return f"({self.a.short_string()} - {self.b.short_string()})"


class Neg(Unary):
    def __init__(self, a: Expression):
        super().__init__(a)

    def _diff(self, term: Variable):
        return Neg(self.a._diff(term))

    def __call__(self, x):
        return -self.a(x)

    def short_string(self):
        return f"-{self.a.short_string()}"


class Times(Binary):
    def __init__(self, a: Expression, b: Expression):
        super().__init__(a, b)

    def _diff(self, term: Variable):
        return Plus(
            Times(
                self.a,
                self.b._diff(term)),
            Times(
                self.a._diff(term),
                self.b))

    def __call__(self, x):
        return self.a(x) * self.b(x)


    def short_string(self):
        return f"({self.a.short_string()} * {self.b.short_string()})"

class Divide(Binary):
    def __init__(self, a: Expression, b: Expression):
        super().__init__(a, b)

    def _diff(self, term: Variable):
        return Divide(
            Minus(
                Times(
                    self.a._diff(term),
                    self.b),
                Times(
                    self.a,
                    self.b._diff(term))),
            Power(self.b, Constant(2)))

    def __call__(self, x):
        return self.a(x) / self.b(x)

    def short_string(self):
        return f"({self.a.short_string()} / {self.b.short_string()})"

class Modulo(Binary):
    def __init__(self, a: Expression, b: Expression):
        super().__init__(a, b)

    def _diff(self, term: Variable):
        return self.a._diff(term)

    def __call__(self, x):
        return self.a(x) % self.b(x)

    def short_string(self):
        return f"({self.a.short_string()} % {self.b.short_string()})"

class Power(Binary):
    def __init__(self, a: Expression, b: Expression):
        super().__init__(a, b)

    def _diff(self, term: Variable):

        """
        The general expression is
        (f g' log f + g f') f^(g-1)

        """

        f = self.a
        g = self.b
        df = self.a._diff(term)
        dg = self.b._diff(term)

        return Times(
                Plus(
                    Times(
                        Times(f, dg),
                        Log(f)),
                    Times(g, df)),
                Power(
                    f,
                    Minus(g, Constant(1))
                )
            )

    def __call__(self, x):
        return self.a(x) ** self.b(x)

    def short_string(self):
        return f"({self.a.short_string()} ^ {self.b.short_string()})"

class Exp(Unary):
    def __init__(self, a: Expression):
        super().__init__(a)

    def _diff(self, term: Variable):
        return Times(Exp(self.a), self.a._diff(term))

    def __call__(self, x):
        return np.exp(self.a(x))

    def short_string(self):
        return f"exp({self.a.short_string()})"

class Log(Unary):
    def __init__(self, a: Expression):
        super().__init__(a)

    def _diff(self, term: Variable):
        return Divide(self.a._diff(term), self.a)

    def __call__(self, x):
        return np.log(self.a(x))

    def short_string(self):
        return f"log({self.a.short_string()})"
#
# Some less nice operations that should none-the-less be supported
#

class Abs(Unary):
    def __init__(self, a: Expression):
        super().__init__(a)

    def _diff(self, term: Variable):
        return Times(Sign(self.a), self.a._diff(term))

    def __call__(self, x):
        return np.log(self.a(x))

    def short_string(self):
        return f"abs({self.a.short_string()})"

class Sign(Unary):
    def __init__(self, a: Expression):
        super().__init__(a)

    def _diff(self, term: Variable):
        return Times(Delta(self.a), self.a._diff(term))

    def __call__(self, x):
        return np.sign(self.a(x))

    def short_string(self):
        return f"sign({self.a.short_string()})"


class Delta(Unary):
    def __init__(self, a: Expression):
        super().__init__(a)

    def _diff(self, term: Variable):
        return Times(Delta(self.a), self.a._diff(term))

    def __call__(self, x):
        return np.sign(self.a(x))

    @property
    def differentiable(self):
        return False

    def short_string(self):
        return f"delta({self.a.short_string()})"

# Simplification rules:
# The idea here is to have a set of rules,
#  each one of which makes the expression simpler
#  these will be applied over and over again until
#  they make no difference.
#
# it is a local simplifier
#
# This is not the best simplification, and there are some obvious
# things it cannot do such as merge constants other than zero or one,
# it can't really take advantage of associativity either
#
# This set of rules cannot have an circularities, otherwise bad things
#  will happen

w1 = Wildcard(0)
w2 = Wildcard(1)
w3 = Wildcard(2)

simplification_substitutions = [
    (w1 + 0,            w1), # Additive identity -> remove constant
    (0 + w1,            w1),
    (1 * w1,            w1), # Multiplicative identity -> remove constant
    (w1 * 1,            w1),
    (w1 - 0,            w1), # Subtractive identity -> remove constant
    (w1 / 1,            w1), # Division identity -> remove constant
    (w1 ** 1,           w1), # Exponential identity -> remove constant
    (0 * w1,            Constant(0)),  # Multiplication by zero -> remove zero constant and anything it multiplies
    (w1 * 0,            Constant(0)),
    (1 ** w1,           Constant(1)),  # Power rules, 1^x = 1
    # (0 ** w1,           Constant(0)),  # 0^x = 0 (not quite true)
    (w1 ** 0,           Constant(1)),  # x^0 = 1
    (w1 - (-w2),        w1+w2),        # Remove double minus -> remove minus signs
    (-(-(w1)),          w1),
    (w1 + (-w2),        w1 - w2),      # +- simplify -> reduce +- sign total
    ((-w1) + w2,        w2 - w1),
    (Constant(1).log,   Constant(0)),  # Log 1 = 0 -> reduce number of logs
    (Constant(0).exp,   Constant(1)),  # Exp 0 = 1 -> reduce exp number
    # (w1*w2 + w1*w3,     w1*(w2 + w3)),  # Distributivity of multiplication over addition
    # (w2*w1 + w1*w3,     w1*(w2 + w3)),
    # (w2*w1 + w3*w1,     w1*(w2 + w3)),
    # (w1*w2 + w3*w1,     w1*(w2 + w3)),
    # (w2/w1 + w3/w1,     (w2+w3) / w1),  # Distributivity of division over addition
    # (w1*w2 - w1*w3,     w1*(w2 - w3)),  # Distributivity of multiplication over subtraction
    # (w2*w1 - w1*w3,     w1*(w2 - w3)),
    # (w2*w1 - w3*w1,     w1*(w2 - w3)),
    # (w1*w2 - w3*w1,     w1*(w2 - w3)),
    # (w2/w1 - w3/w1,     (w2-w3) / w1),  # Distributivity of division over subtraction
    (w1**w2 * w1**w3,   w1**(w2+w3)),   # Exponent rules -> reduce number of exps
    (w1.exp * w2.exp,   (w1+w2).exp),
    (w1.log + w2.log,   (w1*w2).log),   # Log xply rule, reduce number of logs

]