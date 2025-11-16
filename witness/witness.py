import json


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


def load_public_witness_from_json(json_path = './examples/example1/public_witness.json', modulo = None, galois_field=None):

    

    with open(json_path, 'r') as f:
        data = json.load(f)
    public_witness = data

    assert len(public_witness) > 0, "Public witness cannot be empty"

    # if galois_field is provided, convert to galois field elements
    if galois_field is not None:
        public_witness = [galois_field(val) for val in public_witness]
        return public_witness
    
    # ensure all entries are integers modulo the given modulo
    if modulo is not None:
        public_witness = [int(val) % modulo for val in public_witness]

        

    return public_witness

def public_inputs_length(json_path = './examples/example1/public_witness.json'):
    public_witness = load_public_witness_from_json(json_path=json_path)

    return len(public_witness)
