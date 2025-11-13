from py_ecc.bn128.bn128_curve import G1, G2, curve_order
from py_ecc.bn128.bn128_pairing import pairing
from py_ecc.bn128.bn128_curve import multiply, add

from py_ecc.bn128 import FQ, FQ2  # type: ignore
from galois import lagrange_poly, GF




def save_json(data, json_path):
    import json
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4)



def lagrange_poly_vector(vector, galois_field=GF(curve_order)):

    vector = galois_field(vector)
    x_vals = galois_field.Range(1, len(vector) + 1)

    return lagrange_poly(x_vals, vector)

def serialize_point_G1(point):
    if point is None:
        return []
    return [int(coord) for coord in point]
def serialize_point_G2(point):
    if point is None:
        return []
    return [ [int(coeff) for coeff in  point[0].coeffs], [int(coeff) for coeff in  point[1].coeffs] ]

def serialize_points_G1(points):
    return [serialize_point_G1(point) for point in points]
def serialize_points_G2(points):
    return [serialize_point_G2(point) for point in points]

def deserialize_point_G1(point):
    if point is None or (isinstance(point, list) and len(point) == 0):
        return None
    if len(point) == 2:
        return (FQ(point[0]), FQ(point[1]))
    raise ValueError(f"Invalid G1 point format: {point}")

def deserialize_point_G2(point):
    if point is None or len(point) == 0:
        return None
    x_coeffs = tuple(point[0])
    y_coeffs = tuple(point[1])
    if len(x_coeffs) != 2 or len(y_coeffs) != 2:
        raise ValueError(f"Invalid G2 FQ2 coeffs: {point}")
    return (FQ2(x_coeffs), FQ2(y_coeffs))

def deserialize_points_G1(points):
    return [deserialize_point_G1(point) for point in points]

def deserialize_points_G2(points):
    return [deserialize_point_G2(point) for point in points]

def get_coeff_from_poly(poly, degree):
    return poly.coeffs[poly.degree - degree]