from expression import Variable, Constant, Wildcard

x = Variable("x")
y = Variable("y")

expressions = [
    x,
    x+y,
    x*y,
    (x+1)**2,
    (x+y)**2
]

for expression in expressions:
    expression.substitute(x+y, Constant(7)).short_print()

wild1 = Wildcard(0)
wild2 = Wildcard(1)
for expression in expressions:
    expression.substitute(wild1**wild2, wild1+wild2).short_print()