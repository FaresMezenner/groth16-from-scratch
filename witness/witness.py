import json
from py_ecc.bn128.bn128_curve import G1, G2


def load_witness_from_json(json_path = './examples/example1/witness.json', modulo = None, galois_field=None):

    

    with open(json_path, 'r') as f:
        data = json.load(f)
    witness = data

    assert len(witness) > 0, "Witness cannot be empty"

    # if galois_field is provided, convert to galois field elements
    if galois_field is not None:
        witness = [galois_field(val) for val in witness]
        return witness
    
    # ensure all entries are integers modulo the given modulo
    if modulo is not None:
        witness = [int(val) % modulo for val in witness]

        

    return witness


