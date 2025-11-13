import json
from galois import GF

def load_matrices_from_json(json_path = './examples/example1//r1cs.json', modulo = None , galois_field=GF(101)):
    with open(json_path, 'r') as f:
        data = json.load(f)
    L = data['L']
    R = data['R']
    O = data['O']

    # check that L, R, O are matrices with the same dimensions and non-empty
    
    assert len(L) == len(R) == len(O), "L, R, O must have the same number of rows"
    assert all(len(row) == len(L[0]) for row in L), "All rows in L must have the same number of columns"
    assert all(len(row) == len(R[0]) for row in R), "All rows in R must have the same number of columns"
    assert all(len(row) == len(O[0]) for row in O), "All rows in O must have the same number of columns"
    assert len(L) > 0 and len(L[0]) > 0, "Matrices L, R, O cannot be empty"

    # if galois_field is provided, convert to galois field elements
    if galois_field is not None:
        L = [[galois_field(val % galois_field.order) for val in row] for row in L]
        R = [[galois_field(val % galois_field.order) for val in row] for row in R]
        O = [[galois_field(val % galois_field.order) for val in row] for row in O]
        return L, R, O

    # ensure all entries are integers modulo the given modulo

    if modulo is not None:
        L = [[int(val) % modulo for val in row] for row in L]
        R = [[int(val) % modulo for val in row] for row in R]
        O = [[int(val) % modulo for val in row] for row in O]



    return L, R, O