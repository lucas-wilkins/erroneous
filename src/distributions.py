from typing import Optional

from expression import Variable, Expression


class Distribution:
    parameter_names = None

    def __init__(self, parameters):
        if len(parameters) != len(self.parameter_names):
            raise ValueError(f"Incorrect number of parameters supplied to {self.__class__}")

        self.parameters = parameters

    def fisher_information(self, base_variable: Variable) -> Expression:
        pass

    def variance(self, base_variable: Variable) -> Expression:
        pass

    def likelihood_function(self, observation):
        pass

    def log_likelihood_function(self, observatation):
        pass

class Normal(Distribution):
    parameter_names = ["mean", "var"]

    def __init__(self, mean: Optional[float], var: Optional[float]):
        super().__init__((mean, var))


class Poisson(Distribution):
    parameter_names = ["rate"]

    def __init__(self, rate: Optional[float]):
        super().__init__((rate, ))

    def likelihood_function(self, observation):
        pass

    def log_likelihood_function(self, observatation):
        pass

    def fisher_information(self, base_variable: Variable):
        pass

class Binomial(Distribution):
    parameter_names = ["n", "p"]

    def __init__(self, n: Optional[int], p: Optional[float]):
        super().__init__((n, p))


