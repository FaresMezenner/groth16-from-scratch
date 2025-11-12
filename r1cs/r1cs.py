import json

def load_matrices_from_json(json_path = './examples/example1//r1cs.json'):
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


    return L, R, O