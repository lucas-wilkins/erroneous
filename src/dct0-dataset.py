from expression import Variable
from dct import dct_hash

class DCTMetaData:
    def __init__(self, x, y, y_err, *higher_moments, metadata=None, name=None):
        self.x = x
        self.y = y
        self.y_err = y_err
        self.higher_moments = higher_moments
        self.name = name

        self.hash = dct_hash(x, y, y_err, higher_moments)

    def variable(self):
        return Variable(self.hash, self.name)

class DCTComponent()

class DCTDataSet(ABC):

    def __init__(self, x, y, y_err, *higher_moments, metadata=None, name=None):
        self._dct_meta = DCTMetaData(x, y, y_err, *higher_moments, metadata=metadata, name=name)
        self._dct = self._dct_meta.variable()

    @abstractmethod
    def __dct_add__(self, other, dct):


    def __add__(self, other):
        return self.__dct_add__(other, self._dct + other._dct)

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