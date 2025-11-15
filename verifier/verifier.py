
from py_ecc.bn128.bn128_curve import G2
from py_ecc.bn128.bn128_pairing import pairing
from keys import keys

class Verifier:
    def __init__(self, example_path='./examples/example1/'):

        self.example_path = example_path
    def verify(self):
        A, B, C = keys.load_proof_from_json(json_path=self.example_path + 'proof.json')
        alpha, beta = keys.load_verifying_key_from_json(json_path=self.example_path + 'verifying_key.json')

        
        assert pairing(B, A) == pairing(beta, alpha) * pairing(G2, C), "Proof verification failed."

        print("Proof verification succeeded.")
        return True