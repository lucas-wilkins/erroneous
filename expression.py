from __future__ import annotations


class Expression:

    @property
    def hash(self):
        pass

    def diff(self, term: Variable) -> Expression:
        pass

    def __call__(self, x):
        pass

    def __add__(self, other):
        pass

    def __radd__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __rsub__(self, other):
        pass

    def __mul__(self, other):
        pass

    def __rmul__(self, other):
        pass

    def __divmod__(self, other):
        pass

    def __rdiv__(self, other):
        pass

    def __pow__(self, other):
        pass

    def __rpow__(self, other):
        pass

    def __abs__(self, other):
        pass

class Variable(Expression):
    pass


class Plus(Expression):
    def __init__(self, a: Expression, b: Expression):
        self.a = a
        self.b = b

    def diff(self, term: Variable):
        return Plus(self.a.diff(term), self.b.diff(term))

    def __call__(self, x):
        return self.a(x) + self.b(x)

class Minus(Expression):
    def __init__(self, a: Expression, b: Expression):
        self.a = a
        self.b = b

    def diff(self, term: Variable):
        return Minus(self.a.diff(term), self.b.diff(term))

    def __call__(self, x):
        return self.a(x) - self.b(x)

class Neg(Expression):
    pass

class Times(Expression):
    pass

class Divide(Expression):
    pass

class Power(Expression):
    pass

class Abs(Expression):
    pass