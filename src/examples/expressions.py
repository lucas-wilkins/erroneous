from expression import Variable

x = Variable("x")
y = Variable("y")

expressions = [
    x,
    x+y,
    x*y,
    (x+1)**2,
    (x+y)**2
]

for expr in expressions:
    print("\n\n")
    print("f(x,y) =", expr.pretty_print_string())
    print("f(1,2) =", expr({"x": 1, "y": 2}))
    print("d/dx f(x,y) =", expr.fast_diff(x).pretty_print_string())
    print("d/dx f(1,2) =", expr.fast_diff(x)({"x": 1, "y": 2}))