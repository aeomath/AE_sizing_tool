def test(a, b):
    a += 1
    return a + b, a


a = 2
print(test(a, 3))
