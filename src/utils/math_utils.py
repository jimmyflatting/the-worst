def normalize(vector):
    length = sum(x ** 2 for x in vector) ** 0.5
    if length == 0:
        return vector
    return [x / length for x in vector]

def dot_product(v1, v2):
    return sum(x * y for x, y in zip(v1, v2))

def cross_product(v1, v2):
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ]

def subtract(v1, v2):
    return [x - y for x, y in zip(v1, v2)]

def add(v1, v2):
    return [x + y for x, y in zip(v1, v2)]

def scale(vector, scalar):
    return [x * scalar for x in vector]

def length(vector):
    return sum(x ** 2 for x in vector) ** 0.5

def distance(v1, v2):
    return length(subtract(v1, v2))