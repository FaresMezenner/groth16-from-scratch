from py_ecc.bn128.bn128_curve import G1, G2, curve_order
from py_ecc.bn128.bn128_pairing import pairing
from py_ecc.bn128.bn128_curve import multiply, add

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


def save_json(data, json_path):
    import json
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4)

def pair_vector_with_G1(vector):
    return [pairing(v, G1) for v in vector]

def pair_vector_with_G2(vector):
    return [pairing(G2, v) for v in vector]



def linear_combination_ecc(coeffs, points):
    assert len(coeffs) == len(points), "Length of coeffs and points must be the same"
    result = None
    for c, p in zip(coeffs, points):
        if p is None:
            continue  # skip point at infinity
        k = int(c) % curve_order
        if k == 0:
            continue  # skip zero coefficient
        term = multiply(p, k)
        result = term if result is None else add(result, term)
    return result

def matrix_vector_product_ecc(matrix, vector):
    return [linear_combination_ecc(row, vector) for row in matrix]

def linear_pairing_vectors(g1_points, g2_points):
    assert len(g1_points) == len(g2_points), "Length of G1 and G2 points must be the same"
    return [pairing(g2, g1) for g1, g2 in zip(g1_points, g2_points)]

