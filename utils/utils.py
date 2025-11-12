def linear_combination(coeffs, vars, modulo):
    assert len(coeffs) == len(vars), "Length of coeffs and vars must be the same"
    return sum(c * v for c, v in zip(coeffs, vars)) % modulo

def matrix_vector_product(matrix, vector, modulo):
    return [linear_combination(row, vector, modulo) for row in matrix]

def vectors_modular_equal(vec1, vec2, modulo):
    if len(vec1) != len(vec2):
        return False
    return all((a % modulo) == (b % modulo) for a, b in zip(vec1, vec2))
    

def hadamard_product(vec1, vec2, modulo):
    assert len(vec1) == len(vec2), "Vectors must be of the same length"
    return [(a * b) % modulo for a, b in zip(vec1, vec2)]

