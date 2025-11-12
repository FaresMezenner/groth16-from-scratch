from utils.utils import save_json
from witness.witness import load_witness_from_json, save_somewhat_zk_proof_witness_to_json
from py_ecc.bn128.bn128_curve import G1, G2, multiply


class Prover:
    def __init__(self, example_path = './examples/example1/'):
        self.example_path = example_path
    

    def generate_somewhate_zk_proof_r1cs(self):
        witness = load_witness_from_json(json_path=self.example_path + 'witness.json')

        wintess_G1 = [multiply(G1, w) for w in witness ]
        wintess_G2 = [multiply(G2, w) for w in witness ]




        save_somewhat_zk_proof_witness_to_json(wintess_G1, wintess_G2, json_path=self.example_path + 'somewhat_zk_proof_witness.json')

        return wintess_G1, wintess_G2