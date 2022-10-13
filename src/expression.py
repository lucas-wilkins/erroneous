from __future__ import annotations

from fractions import Fraction
import numpy as np
from typing import Dict, Any, Optional

class NonDifferentiableExpressionError(Exception):
    def __init__(self, msg):
        super.__init__(msg)

class Expression:

    # Functions for pattern matching

    @property
    def head(self):
        return self.__class__.__name__

    @property
    def terms(self):
        raise NotImplementedError(f"diff not implemented in {self.__class__.__name__}")

    # Calculus

    def diff(self, term: Variable) -> Expression:
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

    def exp(self):
        return Exp(self)

    def log(self):
        return Log(self)

    def __abs__(self, other):
        return Abs(self)

    def sign(self):
        return Sign(self)




#
# Helper classes
#

class Unary(Expression):
    """ Base class for unary expression components"""
    def __init__(self, a: Any):
        self.a = Expression._sanitise(a)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.a})"

    def terms(self):
        return [self.a]


class Binary(Expression):
    """ Base class for binary expression components"""
    def __init__(self, a: Any, b: Any):
        self.a = Expression._sanitise(a)
        self.b = Expression._sanitise(b)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.a}, {self.b})"



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
    def terms(self):
        return [self.value]


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
    def terms(self):
        return [self.identity]

class Wildcard(Expression):
    def __init__(self, number):
        self.number = number

    @property
    def differentiable(self):
        return False

    def __repr__(self):
        return f"#{self.number}"

    @property
    def terms(self):
        return []

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


class Minus(Binary):
    def __init__(self, a: Expression, b: Expression):
        super().__init__(a, b)

    def _diff(self, term: Variable):
        return Minus(self.a._diff(term), self.b._diff(term))

    def __call__(self, x):
        return self.a(x) - self.b(x)


class Neg(Unary):
    def __init__(self, a: Expression):
        super().__init__(a)

    def _diff(self, term: Variable):
        return Neg(self.a._diff(term))

    def __call__(self, x):
        return -self.a(x)


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


class Modulo(Binary):
    def __init__(self, a: Expression, b: Expression):
        super().__init__(a, b)

    def _diff(self, term: Variable):
        return self.a._diff(term)

    def __call__(self, x):
        return self.a(x) % self.b(x)


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


class Exp(Unary):
    def __init__(self, a: Expression):
        super().__init__(a)

    def _diff(self, term: Variable):
        return Times(Exp(self.a), self.a._diff(term))

    def __call__(self, x):
        return np.exp(self.a(x))


class Log(Unary):
    def __init__(self, a: Expression):
        super().__init__(a)

    def _diff(self, term: Variable):
        return Divide(self.a._diff(term), self.a)

    def __call__(self, x):
        return np.log(self.a(x))

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

class Sign(Unary):
    def __init__(self, a: Expression):
        super().__init__(a)

    def _diff(self, term: Variable):
        return Times(Delta(self.a), self.a._diff(term))

    def __call__(self, x):
        return np.sign(self.a(x))


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
