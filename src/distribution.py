import numpy as np

class MaxEntDistributionABCD:
    def __init__(self, a, b, c, d):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

        self.mode = 0

        self.normalising_constant = 0

    def _unnormalised(self, x):

        p = x
        y = self.a*p

        p *= p
        y += self.b * p

        p *= p
        y += self.c * p

        p *= p
        y += self.d * p

        return np.exp(-y)

    def __call__(self):
        pass
