from expression import Gamma, Polygamma, Constant, Variable

x = Variable("x")
gamma = Gamma(x)

print(gamma)

dgamma = gamma.diff(x)
print(dgamma)


ddgamma = dgamma.diff(x)
print(ddgamma)