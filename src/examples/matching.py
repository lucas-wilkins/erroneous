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

print("Cross match")
for e1 in expressions:
    for e2 in expressions:
        print(e1.match(e2))

print("match with generated x+y")
for e in expressions:
    print(e.match(x+y))

