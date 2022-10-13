from __future__ import annotations

from fractions import Fraction
import numpy as np
from typing import Dict, Any, Optional


class Expression:

    @property
    def hash(self):
        pass

    # Calculus

    def diff(self, term: Variable) -> Expression:
        """Differentiate this expression with respect to a variable"""

    # Evaluation

    def __call__(self, variable_map: Dict[Variable, Any]):
        pass

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

    def __abs__(self, other):
        return Abs(self)


class Unary(Expression):
    """ Base class for unary expression components"""
    def __init__(self, a: Any):
        self.a = Expression._sanitise(a)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.a})"


class Binary(Expression):
    """ Base class for binary expression components"""
    def __init__(self, a: Any, b: Any):
        self.a = Expression._sanitise(a)
        self.b = Expression._sanitise(b)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.a}, {self.b})"


class Constant(Expression):
    """ Represents a constant"""
    def __init__(self, value: Any):
        # This should NOT be a subtype of Unary, because it is the result of
        # Expression._sanitise when given a number
        self.value = value

    def __repr__(self):
        return repr(self.value)


class Variable(Expression):
    def __init__(self):
        pass


class Plus(Binary):
    def __init__(self, a: Expression, b: Expression):
        super().__init__(a, b)

    def diff(self, term: Variable):
        return Plus(self.a.diff(term), self.b.diff(term))

    def __call__(self, x):
        return self.a(x) + self.b(x)


class Minus(Binary):
    def __init__(self, a: Expression, b: Expression):
        super().__init__(a, b)

    def diff(self, term: Variable):
        return Minus(self.a.diff(term), self.b.diff(term))

    def __call__(self, x):
        return self.a(x) - self.b(x)


class Neg(Unary):
    def __init__(self, a: Expression):
        super().__init__(a)


class Times(Binary):
    def __init__(self, a: Expression, b: Expression):
        super().__init__(a, b)


class Divide(Binary):
    def __init__(self, a: Expression, b: Expression):
        super().__init__(a, b)


class Modulo(Binary):
    def __init__(self, a: Expression, b: Expression):
        super().__init__(a, b)


class Power(Binary):
    def __init__(self, a: Expression, b: Expression):
        super().__init__(a, b)


class Abs(Unary):
    def __init__(self, a: Expression):
        super().__init__(a)
