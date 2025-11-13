import json

from utils import utils

def save_prooving_key_to_json(srs1, srs2, srs3, json_path = './examples/example1/proving_key.json'):
    proving_key_data = {
        'srs1': utils.serialize_points_G1(srs1),
        'srs2': utils.serialize_points_G2(srs2),
        'srs3': utils.serialize_points_G1(srs3),
    }

    with open(json_path, 'w') as f:
        json.dump(proving_key_data, f, indent=4)

def load_proving_key_from_json(json_path = './examples/example1/proving_key.json'):

    with open(json_path, 'r') as f:
        data = json.load(f)
    proving_key_data = data

    assert 'srs1' in proving_key_data and 'srs2' in proving_key_data and 'srs3' in proving_key_data, "Proving key must contain 'srs1', 'srs2' and 'srs3'"
    srs1 = utils.deserialize_points_G1(proving_key_data['srs1'])
    srs2 = utils.deserialize_points_G2(proving_key_data['srs2'])
    srs3 = utils.deserialize_points_G1(proving_key_data['srs3'])
    return srs1, srs2, srs3


def save_proof_to_json(A, B, C, json_path = './examples/example1/proof.json'):
    proof_data = {
        'A': utils.serialize_point_G1(A),
        'B': utils.serialize_point_G2(B),
        'C': utils.serialize_point_G1(C),
    }

    with open(json_path, 'w') as f:
        json.dump(proof_data, f, indent=4)

def load_proof_from_json(json_path = './examples/example1/proof.json'):

    with open(json_path, 'r') as f:
        data = json.load(f)
    proof_data = data

    assert 'A' in proof_data and 'B' in proof_data and 'C' in proof_data, "Proof must contain 'A', 'B' and 'C'"
    A = utils.deserialize_point_G1(proof_data['A'])
    B = utils.deserialize_point_G2(proof_data['B'])
    C = utils.deserialize_point_G1(proof_data['C'])
    return A, B, C