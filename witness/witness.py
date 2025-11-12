import json
from py_ecc.bn128.bn128_curve import G1, G2
from py_ecc.bn128 import FQ, FQ2 # type: ignore

def load_witness_from_json(json_path = './examples/example1/witness.json', modulo = None):

    

    with open(json_path, 'r') as f:
        data = json.load(f)
    witness = data

    assert len(witness) > 0, "Witness cannot be empty"
    # ensure all entries are integers modulo the given modulo
    if modulo is not None:
        witness = [int(val) % modulo for val in witness]

    return witness


def save_somewhat_zk_proof_witness_to_json(witness_g1, witness_g2, json_path = './examples/example1/somewhat_zk_proof_witness.json'):
    
    somewhat_zk_proof_witness = {
            'witness_G1': [[int(coord) for coord in point] if point is not None else [] for point in witness_g1],
            'witness_G2': [ [[int(coeff) for coeff in  point[0].coeffs],[int(coeff) for coeff in  point[1].coeffs]] if point is not None and len(point) != 0 else [] for point in witness_g2],
    }

    with open(json_path, 'w') as f:
        json.dump(somewhat_zk_proof_witness, f, indent=4)


def load_somewhat_zk_proof_witness_from_json(json_path = './examples/example1/somewhat_zk_proof_witness.json'):

    

    with open(json_path, 'r') as f:
        data = json.load(f)
    somewhat_zk_proof_witness = data

    assert 'witness_G1' in somewhat_zk_proof_witness and 'witness_G2' in somewhat_zk_proof_witness, "Encrypted witness must contain 'witness_G1' and 'witness_G2'"

    # Build FQ/FQ2 points; empty list or None indicates point at infinity
    wintess_g1 = []
    for point in somewhat_zk_proof_witness['witness_G1']:
        if point is None or (isinstance(point, list) and len(point) == 0):
            wintess_g1.append(None)
        else:
            if len(point) == 2:
                wintess_g1.append((FQ(point[0]), FQ(point[1])))
            else:
                raise ValueError(f"Invalid G1 point format: {point}")

    witness_g2 = []
    for point in somewhat_zk_proof_witness['witness_G2']:
        if point is None or len(point) == 0:
            witness_g2.append(None)
        else:
            x_coeffs = tuple(point[0])
            y_coeffs = tuple(point[1])
            if len(x_coeffs) != 2 or len(y_coeffs) != 2:
                raise ValueError(f"Invalid G2 FQ2 coeffs: {point}")
            witness_g2.append((FQ2(x_coeffs), FQ2(y_coeffs)))
    return wintess_g1, witness_g2
