import json

def load_witness_from_json(json_path = './examples/example1/witness.json'):

    

    with open(json_path, 'r') as f:
        data = json.load(f)
    witness = data

    assert len(witness) > 0, "Witness cannot be empty"


    return witness


