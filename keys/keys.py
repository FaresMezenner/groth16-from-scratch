import json

from utils import utils

def save_prooving_key_to_json(srs1, srs2, srs3, psi, alpha, beta_G1, beta_G2, delta_G1, delta_G2, tau_G1, tau_G2, json_path = './examples/example1/proving_key.json'):
    proving_key_data = {
        'srs1': utils.serialize_points_G1(srs1),
        'srs2': utils.serialize_points_G2(srs2),
        'srs3': utils.serialize_points_G1(srs3),
        'psi': utils.serialize_points_G1(psi),
        'alpha': utils.serialize_point_G1(alpha),
        'beta_G1': utils.serialize_point_G1(beta_G1),
        'beta_G2': utils.serialize_point_G2(beta_G2),
        'delta_G1': utils.serialize_point_G1(delta_G1),
        'delta_G2': utils.serialize_point_G2(delta_G2),
        'tau_G1': utils.serialize_point_G1(tau_G1),
        'tau_G2': utils.serialize_point_G2(tau_G2),
    }

    with open(json_path, 'w') as f:
        print("Openinf file to save proving key:", json_path)
        json.dump(proving_key_data, f, indent=4)

def load_proving_key_from_json(json_path = './examples/example1/proving_key.json'):

    with open(json_path, 'r') as f:
        print("Opening file to load proving key:", json_path)
        data = json.load(f)
    proving_key_data = data

    assert 'srs1' in proving_key_data and 'srs2' in proving_key_data and 'srs3' in proving_key_data and 'psi' in proving_key_data and 'alpha' in proving_key_data and 'beta_G1' in proving_key_data and 'beta_G2' in proving_key_data and 'delta_G1' in proving_key_data and 'delta_G2' in proving_key_data and 'tau_G1' in proving_key_data and 'tau_G2' in proving_key_data, "Proving key must contain 'srs1', 'srs2', 'srs3', 'psi', 'alpha', 'beta_G1', 'beta_G2', 'delta_G1', 'delta_G2', 'tau_G1' and 'tau_G2'"
    srs1 = utils.deserialize_points_G1(proving_key_data['srs1'])
    srs2 = utils.deserialize_points_G2(proving_key_data['srs2'])
    srs3 = utils.deserialize_points_G1(proving_key_data['srs3'])
    psi = utils.deserialize_points_G1(proving_key_data['psi'])
    alpha = utils.deserialize_point_G1(proving_key_data['alpha'])
    beta_G1 = utils.deserialize_point_G1(proving_key_data['beta_G1'])
    beta_G2 = utils.deserialize_point_G2(proving_key_data['beta_G2'])
    delta_G1 = utils.deserialize_point_G1(proving_key_data['delta_G1'])
    delta_G2 = utils.deserialize_point_G2(proving_key_data['delta_G2'])
    tau_G1 = utils.deserialize_point_G1(proving_key_data['tau_G1'])
    tau_G2 = utils.deserialize_point_G2(proving_key_data['tau_G2'])
    return srs1, srs2, srs3, psi, alpha, beta_G1, beta_G2, delta_G1, delta_G2, tau_G1, tau_G2


def save_proof_to_json(A, B, C, json_path = './examples/example1/proof.json'):
    proof_data = {
        'A': utils.serialize_point_G1(A),
        'B': utils.serialize_point_G2(B),
        'C': utils.serialize_point_G1(C),
    }

    with open(json_path, 'w') as f:
        print("Opening file to save proof:", json_path)
        json.dump(proof_data, f, indent=4)

def load_proof_from_json(json_path = './examples/example1/proof.json'):

    with open(json_path, 'r') as f:
        print("Opening file to load proof:", json_path)
        data = json.load(f)
    proof_data = data

    assert 'A' in proof_data and 'B' in proof_data and 'C' in proof_data, "Proof must contain 'A', 'B' and 'C'"
    A = utils.deserialize_point_G1(proof_data['A'])
    B = utils.deserialize_point_G2(proof_data['B'])
    C = utils.deserialize_point_G1(proof_data['C'])
    return A, B, C


def save_verifying_key_to_json(alpha, beta, delta_G2, gamma_G2, verifying_psi, json_path = './examples/example1/verifying_key.json'):
    verifying_key_data = {
        'alpha': utils.serialize_point_G1(alpha),
        'beta': utils.serialize_point_G2(beta),
        'delta': utils.serialize_point_G2(delta_G2),
        'gamma': utils.serialize_point_G2(gamma_G2),
        'psi': utils.serialize_points_G1(verifying_psi),
    }

    with open(json_path, 'w') as f:
        print("Opening file to save verifying key:", json_path)
        json.dump(verifying_key_data, f, indent=4)

def load_verifying_key_from_json(json_path = './examples/example1/verifying_key.json'):

    with open(json_path, 'r') as f:
        print("Opening file to load verifying key:", json_path)
        data = json.load(f)
    verifying_key_data = data

    assert 'alpha' in verifying_key_data and 'beta' in verifying_key_data and 'delta' in verifying_key_data and 'gamma' in verifying_key_data and 'psi' in verifying_key_data, "Verifying key must contain 'alpha', 'beta', 'delta', 'gamma' and 'psi'" 
    alpha = utils.deserialize_point_G1(verifying_key_data['alpha'])
    beta = utils.deserialize_point_G2(verifying_key_data['beta'])
    delta_G2 = utils.deserialize_point_G2(verifying_key_data['delta'])
    gamma_G2 = utils.deserialize_point_G2(verifying_key_data['gamma'])
    verifying_psi = utils.deserialize_points_G1(verifying_key_data['psi'])
    return alpha, beta, delta_G2, gamma_G2, verifying_psi